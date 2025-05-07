from flask import Blueprint, request ,jsonify
import pandas as pd

file_path = "data/selected_features.csv"
get_dataframe_bp = Blueprint('get_dataframe', __name__)

@get_dataframe_bp.route('/get_dataframe', methods=['GET'])
def get_dataframe():
    try:
        df = pd.read_csv(file_path)
        return jsonify(df.to_dict(orient='records')), 200
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500