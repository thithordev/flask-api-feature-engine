import pandas as pd
from feature_engine.imputation import MeanMedianImputer
from feature_engine.selection import DropCorrelatedFeatures

def feature_extraction(file_path, top_x = 100):
    df = pd.read_csv(file_path)
    top_x = int(top_x) if top_x.isdigit() else 100
    # Drop rows with missing values
    df.dropna(inplace=True)

    # Separate features and target variable
    X = df.drop(columns=['timestamp'])
    y = df['timestamp']  # Assuming 'timestamp' is the target variable

    # Feature extraction using DropCorrelatedFeatures
    feature_selector = DropCorrelatedFeatures(threshold=0.85) # Remove features with correlation > 0.85
    X_transformed = feature_selector.fit_transform(X)

    # Select top X % features
    num_features = int(len(X_transformed.columns) * (top_x / 100))
    selected_features = X_transformed.iloc[:, :num_features]
    
    # Combine selected features with the target variable
    features = pd.concat([y, selected_features], axis=1)
    
    # File name from the original file path
    file_name = file_path.split('\\')[-1].split('.')[0]
    # Create a new file name for the extracted features
    feature_file_name = f"{file_name}_features.csv"
    # Save the extracted features to a new CSV file
    feature_file_path = f"uploads\\{feature_file_name}"
    features.to_csv(feature_file_path, index=False)

    return feature_file_path