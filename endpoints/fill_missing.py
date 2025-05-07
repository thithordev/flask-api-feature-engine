from flask import Blueprint, request, jsonify
import pandas as pd
from feature_engine.imputation import MeanMedianImputer

file_path = "data/dummy_data_with_outliers.csv"
fill_missing_bp = Blueprint('fill_missing', __name__)

@fill_missing_bp.route('/fill_missing', methods=['GET'])
def fill_missing():
    try:
        # Load the data
        df = pd.read_csv(file_path)
        print("Original Data (with missing values):")
        print(df.head())
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Get the imputation method from the request
    method = request.args.get("method", "").lower()
    df_imputed = None

    try:
        if method == "mean":
            imputer = MeanMedianImputer(imputation_method='mean')
            df_imputed = imputer.fit_transform(df)
            print("Imputed Data (mean):")
            print(df_imputed.head())

        elif method == "constant":
            df.fillna(value=0, inplace=True)
            df_imputed = df
            print("Imputed Data (constant):")
            print(df.head())

        elif method == "linear":
            df_imputed = df.interpolate(method='linear')
            print("Imputed Data (linear):")
            print(df_imputed.head())

        else:
            return jsonify({"error": "Invalid method. Only \"mean\", \"constant\", \"linear\" are supported."}), 400

        # Save the imputed DataFrame to a CSV file
        save_path = "data/imputed_data.csv"
        df_imputed.to_csv(save_path, index=False)
        print(f"Imputed data saved to {save_path}")

        # Return success response
        return jsonify({
            "message": "Missing values filled successfully.",
            "file_path": save_path
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500