from flask import Blueprint, request ,jsonify
import pandas as pd
from sklearn.feature_selection import SelectFromModel
from sklearn.ensemble import RandomForestClassifier

file_path = "data/transformed_data.csv"
feature_extraction_bp = Blueprint('feature_extraction', __name__)

@feature_extraction_bp.route('/feature_extraction', methods=['GET'])
def feature_extraction():
    try:
        df = pd.read_csv(file_path)
        print("Original Data (with missing values):")
        print(df.head())  # Print the first few rows of the original data

        top_x = request.args.get("top_x", 100) 
        top_x = int(top_x) if top_x.isdigit() else 100
        print(f"Top X: {top_x}")
        # Drop rows with missing values
        df = df.dropna()
        print("Data after dropping missing values:")
        print(df.head())  # Print the first few rows after dropping missing values
        # Separate features and target variable
        X = df.drop(columns=['timestamp'])
        y = df['timestamp']  # Assuming 'timestamp' is the target variable
        # Feature extraction using SelectFromModel
        model = SelectFromModel(estimator=RandomForestClassifier(n_estimators=100))
        model.fit(X, y)
        selected_features = model.get_support(indices=True)
        selected_columns = X.columns[selected_features]
        print("Selected Features:")
        print(selected_columns)  # Print the selected features
        # Select top X% features
        x_percent = int(len(selected_columns) * (top_x / 100))
        selected_columns = selected_columns[:x_percent]
        print(f"Top {top_x} Features:")
        print(selected_columns)  # Print the top X features
        # Create a new DataFrame with the selected features
        selected_df = df[selected_columns]
        selected_df['timestamp'] = df['timestamp']  # Add the timestamp column back
        # Save the new DataFrame to a CSV file
        selected_df.to_csv("data/selected_features.csv", index=False)
        print("Selected features saved to 'selected_features.csv'")
        return jsonify({"message": "Feature extraction completed successfully", "selected_features": selected_columns.tolist()}), 200
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500