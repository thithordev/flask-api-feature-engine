import pandas as pd
from feature_engine.imputation import MeanMedianImputer
from feature_engine.selection import DropCorrelatedFeatures

def detect_outliers(file_path, method='mean'):
    df = pd.read_csv(file_path)

    outlier_detector = MeanMedianImputer(imputation_method=method)
    outlier_detector.fit(df)
    transformed_df = outlier_detector.transform(df)

    # File name from the original file path
    file_name = file_path.split('\\')[-1].split('.')[0]
    # Create a new file name for the outlier data
    outlier_file_name = f"{file_name}_outliers.csv"
    # Save the outlier DataFrame to a new CSV file
    outlier_file_path = f"uploads\\{outlier_file_name}"
    transformed_df.to_csv(outlier_file_path, index=False)

    return outlier_file_path