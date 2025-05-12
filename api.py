import json
from bson import ObjectId
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from flask_socketio import SocketIO
import os
import time
from datetime import datetime
from dtale.app import get_instance
from app.configs.rabbitmq_config import RabbitMQConfig, RabbitMQHelper
from app.configs.mongodb_config import MongoDBConfig, MongoDBHelper
import dtale
import pandas as pd
import socket

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
CORS(app)

# Initialize Flask-SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

app.config['STATIC_FOLDER'] = 'static'

# Ensure the uploads folder exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Limit file size (2GB in this case)
app.config['MAX_CONTENT_LENGTH'] = 2000 * 1024 * 1024  # 2GB

# Initialize MongoDB configuration
mongo_config = MongoDBConfig(uri="mongodb://localhost:27017", database_name="dataset_db")
mongo_helper = MongoDBHelper(mongo_config)

def initialize_config_collection():
    """Initialize the config collection with default data."""
    config_collection = "config"
    default_configs = [
        {"_id": "fill_missing", "name": "fill_missing", "description": "Fill missing values in the dataset", "status": "active"},
        {"_id": "detect_outliers", "name": "detect_outliers", "description": "Detect outliers in the dataset", "status": "active"},
        {"_id": "feature_extraction", "name": "feature_extraction", "description": "Extract features from the dataset", "status": "active"},
    ]

    # Check if the collection already has data
    existing_configs = mongo_helper.list_documents(config_collection)
    if not existing_configs:
        mongo_helper.config.db[config_collection].insert_many(default_configs)
        print("Default configs initialized with fixed IDs.")
    else:
        print("Config collection already initialized.")

@app.route('/')
def home():
    """Render the home page."""
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files from the static folder."""
    return send_from_directory(app.config['STATIC_FOLDER'], filename)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Save file metadata to MongoDB
    file_metadata = {
        "filename": file.filename,
        "upload_time": datetime.utcnow(),
        "file_path": file_path,
        "file_path_preprocess": None,
        "dtale_url": None,
        'status': 'pending',
        'step_preprocess': 'fill_missing',
        "size_original": os.path.getsize(file_path),
        "number_of_records_original": pd.read_csv(file_path).shape[0],
        "number_of_feature_original": pd.read_csv(file_path).shape[1] - 1,
        "size_preprocess": None,
        "number_of_records_preprocess": None,
        "number_of_feature_preprocess": None,
        "percentage_completed": 0,
    }
    file_id = mongo_helper.insert_document("dataset", file_metadata)
    return jsonify({"message": "File successfully uploaded", "filename": file.filename}), 200

@app.route('/processSubmit', methods=['POST'])
def submit_process_file():
    # Get infomation from form data
    fileId = request.form.get('dataset_id')
    fill_method = request.form.get('fill_method')
    constant_value = request.form.get('constant_value') if fill_method == 'constant' else None
    outlier_method = request.form.get('outlier_method')
    feature_range = request.form.get('feature_range')

    file = mongo_helper.find_document("dataset", {"_id": ObjectId(fileId)})

    # Save config data to dataset_config (intermediate table)
    dataset_config_data = {
        "dataset_id": str(fileId),
        "configs": [
            {
                "config_id": "fill_missing",
                "method": fill_method,
                "constant_value": constant_value
            },
            {
                "config_id": "detect_outliers",
                "method": outlier_method
            },
            {
                "config_id": "feature_extraction",
                "range": feature_range
            }
        ],
        "created_at": datetime.utcnow()
    }


    # Initialize RabbitMQ configuration
    rabbitmq_config = RabbitMQConfig()
    rabbitmq_helper = RabbitMQHelper(rabbitmq_config)

    # Declare an exchange
    exchange_name = 'dataset_exchange_preprocess'
    rabbitmq_helper.declare_exchange(exchange_name)

    # Declare a queue fill_missing
    queue_name_fill_missing = 'dataset_queue_fill_missing'
    rabbitmq_helper.declare_queue(queue_name_fill_missing)
    queue_name_detect_outliers = 'dataset_queue_detect_outliers'
    rabbitmq_helper.declare_queue(queue_name_detect_outliers)
    queue_name_feature_extraction = 'dataset_queue_feature_extraction'
    rabbitmq_helper.declare_queue(queue_name_feature_extraction)

    # Bind the queue to the exchange with a routing key
    routing_key_fill_missing = 'fill_missing'
    rabbitmq_helper.bind_queue(queue_name_fill_missing, exchange_name, routing_key_fill_missing)
    routing_key_detect_outliers = 'detect_outliers'
    rabbitmq_helper.bind_queue(queue_name_detect_outliers, exchange_name, routing_key_detect_outliers)
    routing_key_feature_extraction = 'feature_extraction'
    rabbitmq_helper.bind_queue(queue_name_feature_extraction, exchange_name, routing_key_feature_extraction)

    # Message to be sent to the queue
    message = {
        "file_id": str(fileId),
        "filename": file.get('filename'),
        "file_path": file.get('file_path'),
        "step_preprocess": 'fill_missing',
        "method_fill_missing": fill_method,
        "constant_value": constant_value,
        "method_outlier": outlier_method,
        "range": feature_range,
        "status": 'pending',
        "percentage_completed": 0,
    }

    # Publish the message to RabbitMQ
    rabbitmq_helper.publish_message(exchange_name, routing_key_fill_missing, json.dumps(message))

    return jsonify({"message": "File submit processed", "filename": file.get('filename')}), 200

@app.route('/uploads/<path:filename>', methods=['GET'])
def get_uploaded_file(filename):
    """Serve a file from the uploads folder."""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

@app.route('/uploads', methods=['GET'])
def list_uploaded_files():
    """Render a page with the list of uploaded files."""
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('uploads.html', files=files)

@app.route('/datasets', methods=['GET'])
def datasets_page():
    """Render the dataset page."""
    return render_template('dataset.html')

@app.route('/api/datasets', methods=['GET'])
def get_datasets():
    """API to fetch all datasets."""
    datasets = mongo_helper.list_documents("dataset")
    for dataset in datasets:
        dataset['_id'] = str(dataset['_id'])  # Convert ObjectId to string
    return jsonify(datasets), 200

@app.route('/api/datasets/<file_id>', methods=['DELETE'])
def delete_dataset(file_id):
    """API to delete a dataset."""
    # Get file path from MongoDB
    dataset = mongo_helper.find_document("dataset", {"_id": ObjectId(file_id)})
    result = mongo_helper.delete_document("dataset", {"_id": ObjectId(file_id)})
    # Delete dataset_config
    mongo_helper.delete_document("dataset_config", {"dataset_id": file_id})
    # Delete the file from the filesystem
    file_path = dataset.get('file_path')
    file_path_preprocess = dataset.get('file_path_preprocess')
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
    if file_path_preprocess and os.path.exists(file_path_preprocess):
        os.remove(file_path_preprocess)
    # Check if the dataset was deleted
    if result.deleted_count > 0:
        return jsonify({"message": "Dataset deleted successfully"}), 200
    else:
        return jsonify({"error": "Dataset not found"}), 404

@app.route('/api/datasets/<file_id>/view', methods=['GET'])
def view_dataset(file_id):
    """Launch D-Tale to view the dataset."""
    # Lấy thông tin dataset từ MongoDB
    dataset = mongo_helper.find_document("dataset", {"_id": ObjectId(file_id)})
    if not dataset:
        return jsonify({"error": "Dataset not found"}), 404

    # Kiểm tra trạng thái preprocessing
    if dataset.get('status') != 'completed':
        return jsonify({"error": "Dataset preprocessing is not completed yet"}), 400

    dtale_url = dataset.get('dtale_url')
    if dtale_url:
        session_id = dtale_url.split('/')[-1]
        if get_instance(session_id):
            return jsonify({"url": dtale_url}), 200

    # Đọc file CSV
    file_path = dataset.get('file_path_preprocess') or dataset.get('file_path')
    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "Processed file not found"}), 404
    
    # Khởi chạy D-Tale
    host_ip = socket.gethostbyname(socket.gethostname())
    df = pd.read_csv(file_path)
    df = df.drop_duplicates()
    instance = dtale.show(df, host=host_ip)

    dtale_url = instance._main_url

    mongo_helper.update_document("dataset", {"_id": ObjectId(file_id)}, {"dtale_url": dtale_url})
    return jsonify({"url": dtale_url}), 200

@app.route('/api/datasets/<file_id>/original', methods=['GET'])
def view_original_dataset(file_id):
    """Launch D-Tale to view the dataset."""
    dataset = mongo_helper.find_document("dataset", {"_id": ObjectId(file_id)})
    if not dataset:
        return jsonify({"error": "Dataset not found"}), 404
    
    dtale_url = dataset.get('dtale_url_original')
    if dtale_url:
        session_id = dtale_url.split('/')[-1]
        if get_instance(session_id):
            return jsonify({"url": dtale_url}), 200

    file_path = dataset.get('file_path')
    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "Processed file not found"}), 404
    host_ip = socket.gethostbyname(socket.gethostname())
    df = pd.read_csv(file_path)
    df = df.drop_duplicates()
    instance = dtale.show(df, host=host_ip)

    dtale_url = instance._main_url

    mongo_helper.update_document("dataset", {"_id": ObjectId(file_id)}, {"dtale_url_original": dtale_url})
    return jsonify({"url": dtale_url}), 200

@app.route('/api/preprocessing', methods=['POST'])
def preprocessing():
    """API to handle preprocessing updates for a dataset."""
    data = request.json

    # Extract information from request body
    file_id = data.get('file_id')
    step_preprocess = data.get('step_preprocess')
    percentage_completed = data.get('percentage_completed')
    file_path_preprocess = data.get('file_path_preprocess')
    status = data.get('status')

    # Validate required fields
    if not file_id or not step_preprocess or percentage_completed is None or not status:
        return jsonify({"error": "Missing required fields"}), 400

    # Find the dataset in MongoDB
    dataset = mongo_helper.find_document("dataset", {"_id": ObjectId(file_id)})
    if not dataset:
        return jsonify({"error": "Dataset not found"}), 404

    # Update preprocessing status in MongoDB
    update_data = {
        "step_preprocess": step_preprocess,
        "percentage_completed": percentage_completed,
        "file_path_preprocess": file_path_preprocess,
        "status": status
    }

    # If preprocessing is completed, calculate additional details
    if status == "completed" and file_path_preprocess and os.path.exists(file_path_preprocess):
        df = pd.read_csv(file_path_preprocess)
        update_data["size_preprocess"] = os.path.getsize(file_path_preprocess)
        update_data["number_of_records_preprocess"] = df.shape[0]
        update_data["number_of_feature_preprocess"] = df.shape[1] - 1

    mongo_helper.update_document("dataset", {"_id": ObjectId(file_id)}, update_data)

    # Emit progress update with additional details
    emit_progress_update(
        file_id,
        percentage_completed,
        status,
        file_path_preprocess=file_path_preprocess,
        size_preprocess=update_data.get("size_preprocess"),
        number_of_records_preprocess=update_data.get("number_of_records_preprocess"),
        number_of_feature_preprocess=update_data.get("number_of_feature_preprocess"),
    )

    return jsonify({"message": "Preprocessing updated successfully"}), 200


def emit_progress_update(file_id, percentage_completed, status, file_path_preprocess=None, size_preprocess=None, number_of_records_preprocess=None, number_of_feature_preprocess=None):
    """Emit progress updates to the WebSocket."""
    socketio.emit('progress_update', {
        'file_id': file_id,
        'percentage_completed': percentage_completed,
        'status': status,
        'file_path_preprocess': file_path_preprocess,
        'size_preprocess': size_preprocess,
        'number_of_records_preprocess': number_of_records_preprocess,
        'number_of_feature_preprocess': number_of_feature_preprocess
    })

# Simulate preprocessing updates (for demonstration purposes)
@app.route('/simulate_preprocessing/<file_id>', methods=['POST'])
def simulate_preprocessing(file_id):
    """Simulate preprocessing updates for a dataset."""
    for i in range(0, 101, 10):
        time.sleep(1)  # Simulate processing delay
        emit_progress_update(file_id, i, 'processing' if i < 100 else 'completed')
    return jsonify({"message": "Simulation completed"}), 200

if __name__ == '__main__':
    initialize_config_collection()
    socketio.run(app, debug=True, use_reloader=False)
