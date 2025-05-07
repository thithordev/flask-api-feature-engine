from flask import Blueprint, request ,jsonify
import pandas as pd
from feature_engine.imputation import MeanMedianImputer

file_path = "data/imputed_data.csv"
detect_outliers_bp = Blueprint('outlier', __name__)

@detect_outliers_bp.route('/detect_outliers', methods=['GET'])
def detect_outliers():
    try:
        df = pd.read_csv(file_path)
        method = request.args.get('method', default='mean', type=str)
        # Detect outliers using the specified method
        outlier_detector = MeanMedianImputer(method)
        outlier_detector.fit(df)
        # Transform the data to cap the outliers
        transformed_df = outlier_detector.transform(df)
        print("Transformed Data:")
        print(transformed_df.head())
        # Save the transformed data to a new CSV file
        save_path = "data/transformed_data.csv"
        transformed_df.to_csv(save_path, index=False)
        return jsonify({"message": "Outliers detected and data transformed successfully.", "file_path": save_path}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500