import pandas as pd
from feature_engine.imputation import MeanMedianImputer
from feature_engine.selection import DropCorrelatedFeatures

def fill_missing(file_path, method='mean', fill_value=0):
    df = pd.read_csv(file_path)

    numeric_columns = df.select_dtypes(include=['number']).columns

    if method == 'mean':
        # Fill missing values with the mean of each column
        df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].mean())
    
    elif method == 'constant':
        # Fill missing values with a constant value
        df[numeric_columns] = df[numeric_columns].fillna(fill_value)
    
    elif method == 'linear':
        # Fill missing values using linear interpolation
        df[numeric_columns] = df[numeric_columns].interpolate(method='linear')

    else:
        raise ValueError("Invalid method. Choose 'mean', 'constant', or 'linear'.")
    
    # File name from the original file path
    file_name = file_path.split('\\')[-1].split('.')[0]
    # Create a new file name for the filled data
    filled_file_name = f"{file_name}_filled.csv"
    # Save the filled DataFrame to a new CSV file
    filled_file_path = f"uploads\\{filled_file_name}"
    df.to_csv(filled_file_path, index=False)

    return filled_file_path