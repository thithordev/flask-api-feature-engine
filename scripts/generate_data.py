import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import string

# Configuration
num_columns = 50  # Number of sensor columns
periods = 126000      # Number of rows (48 hours with 30-minute intervals)
freq_minutes = 30
start_time = datetime(2021, 5, 15, 0, 0, 0)

# Function to generate random sensor tag names in an industrial format
def generate_random_tag():
    prefix = random.choice(['AI', 'TI', 'PI', 'FI', 'PDI', 'TIC', 'FIC', 'PIC', 'TY', 'RX', 'SN', 'CAT'])
    section = f"{random.randint(1, 3)}{random.choice(string.ascii_uppercase)}{random.randint(1, 9)}"
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=2))
    postfix = random.choice(['.PV', '.CPV', '.MV'])
    return f"{prefix}-{section}{suffix}{postfix}"

# Generate timestamp list
timestamps = [start_time + timedelta(minutes=freq_minutes * i) for i in range(periods)]

# Generate random column names and values
np.random.seed(42)
random.seed(42)
columns = [generate_random_tag() for _ in range(num_columns)]
columns = list(set(columns))  # Remove duplicates if any
while len(columns) < num_columns:  # Refill if any duplicates were removed
    new_tag = generate_random_tag()
    if new_tag not in columns:
        columns.append(new_tag)

data = {"timestamp": timestamps}
for col in columns:
    # Assign value ranges based on tag prefix
    if col.startswith("TI") or col.startswith("TIC"):
        values = np.random.uniform(20, 600, size=periods)
    elif col.startswith("PI") or col.startswith("PDI") or col.startswith("PIC"):
        values = np.random.uniform(0, 100, size=periods)
    elif col.startswith("FI") or col.startswith("FIC"):
        values = np.random.uniform(100, 1000, size=periods)
    elif col.endswith(".MV"):
        values = np.random.uniform(0, 1, size=periods)
    else:
        values = np.random.uniform(0, 500, size=periods)

    # Add outliers (randomly adding some extreme values to create outliers)
    num_outliers = int(periods * 0.05)  # 5% of the data will have outliers
    outlier_indices = random.sample(range(periods), num_outliers)

    for idx in outlier_indices:
        # Create outliers by assigning extreme values outside the normal range
        if col.startswith("TI") or col.startswith("TIC"):
            values[idx] = random.choice([1000, 1500, 2000, 5000])  # Add high outlier
        elif col.startswith("PI") or col.startswith("PDI") or col.startswith("PIC"):
            values[idx] = random.choice([120, 150, 200])  # Add high outlier
        elif col.startswith("FI") or col.startswith("FIC"):
            values[idx] = random.choice([2000, 3000, 4000])  # Add high outlier
        elif col.endswith(".MV"):
            values[idx] = random.choice([2, 3, 10])  # Add high outlier
        else:
            values[idx] = random.choice([600, 700, 1000])  # Add high outlier

    # Introduce missing values
    num_missing = int(periods * 0.1)  # 10% of the data will have missing values
    missing_indices = random.sample(range(periods), num_missing)
    for idx in missing_indices:
        values[idx] = np.nan  # Assign NaN to create missing values

    data[col] = values

# Export to DataFrame
df = pd.DataFrame(data)
df.to_csv("data/dummy_data_with_outliers_1.csv", index=False)
print("✅ File 'dummy_data_with_outliers.csv' has been generated successfully with missing values.")
