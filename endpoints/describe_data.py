from flask import Blueprint, request ,jsonify
import pandas as pd

file_path = "data/selected_features.csv"
describe_data_bp = Blueprint('describe_data', __name__)

@describe_data_bp.route('/describe', methods=['GET'])
def describe_data():
    try:
        df = pd.read_csv(file_path)
        description = df.describe().to_dict()
        return jsonify(description)
    except Exception as e:
        return jsonify({"error": str(e)}), 500