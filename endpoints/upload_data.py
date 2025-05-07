from flask import Blueprint, request ,jsonify
import pandas as pd

file_path = "data/dummy_data_with_outliers.csv"
upload_data_bp = Blueprint('upload_data', __name__)

@upload_data_bp.route('/upload', methods=['POST'])
def upload_data():
    try:
        # Check if the file is part of the request
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
        
        file = request.files['file']
        
        # Check if a file was actually uploaded
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        # Read the uploaded CSV file into a DataFrame
        df = pd.read_csv(file)
        
        # Save the DataFrame to a CSV file
        df.to_csv(file_path, index=False)
        
        return jsonify({"message": "File uploaded successfully", "file_path": file_path}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500