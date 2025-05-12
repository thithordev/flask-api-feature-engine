import json
import requests
from func.services.detect_outliers import detect_outliers
from app.configs.rabbitmq_config import RabbitMQHelper, RabbitMQConfig

def process_detect_outliers(ch, method, properties, body):
    """Process the detect_outliers task."""
    message = json.loads(body)
    file_id = message['file_id']
    file_path = message['file_path']
    outlier_method = message.get('method_outlier', 'mean')

    fill_method = message.get('method_fill_missing', 'mean')
    fill_value = message.get('constant_value', 0)
    range = message.get('range', 100)

    try:
        # Process the file using detect_outliers
        outlier_file_path = detect_outliers(file_path, method=outlier_method)

        # Update preprocessing status to 66%
        update_data = {
            "file_id": file_id,
            "step_preprocess": "detect_outliers",
            "file_path_preprocess": outlier_file_path,
            "percentage_completed": 66,
            "status": "pending"
        }
        requests.post("http://localhost:5000/api/preprocessing", json=update_data)

        # Publish message to the next queue (feature_extraction)
        next_message = {
            "file_id": file_id,
            "file_path": outlier_file_path,
            "step_preprocess": "feature_extraction",
            "method_fill_missing": fill_method,
            "constant_value": fill_value,
            "method_outlier": outlier_method,
            "range": range,
            "status": "pending",
            "percentage_completed": 66
        }
        rabbitmq_helper.publish_message("dataset_exchange_preprocess", "feature_extraction", json.dumps(next_message))

    except Exception as e:
        print(f"Error processing detect_outliers: {e}")

# Initialize RabbitMQ
rabbitmq_config = RabbitMQConfig()
rabbitmq_helper = RabbitMQHelper(rabbitmq_config)
rabbitmq_helper.consume_messages("dataset_queue_detect_outliers", process_detect_outliers)