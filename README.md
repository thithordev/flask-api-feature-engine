
# Flask API Feature Engineering

This project is a Flask-based API for data processing and feature engineering, integrated with a Dash dashboard for data visualization and analysis. It provides endpoints for various data preprocessing tasks such as detecting outliers, filling missing values, feature extraction, and more.

## Features

- **RESTful API Endpoints**:
  - Detect outliers in datasets.
  - Fill missing values in data.
  - Extract features from datasets.
  - Describe data statistics.
  - Upload and retrieve datasets.

- **Dash Dashboard**:
  - Upload CSV files for analysis.
  - Visualize and process data interactively.
  - Perform data transformations using API integrations.

## Project Structure

```
flask-api-feature-engine/
├── app.py                     # Main Flask application
├── endpoints/                 # API endpoints
│   ├── detect_outliers.py     # Outlier detection logic
│   ├── fill_missing.py        # Missing value handling
│   ├── feature_extraction.py  # Feature extraction logic
│   ├── describe_data.py       # Data description logic
│   ├── get_dataframe.py       # Retrieve datasets
│   ├── upload_data.py         # Upload datasets
│   └── dash_plot.py           # Dash dashboard integration
├── data/                      # Sample and processed data
├── .gitignore                 # Ignored files and directories
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/thithordev/flask-api-feature-engine.git
   cd flask-api-feature-engine
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   .venv\Scriptsctivate  # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Access the API at `http://127.0.0.1:5000/api/v1/` and the Dash dashboard at `http://127.0.0.1:5000/`.

## API Endpoints

| Endpoint                     | Method | Description                          |
|------------------------------|--------|--------------------------------------|
| `/api/v1/detect_outliers`    | GET    | Detect outliers in the dataset.      |
| `/api/v1/fill_missing`       | GET    | Fill missing values in the dataset.  |
| `/api/v1/feature_extraction` | GET    | Extract features from the dataset.   |
| `/api/v1/describe_data`      | GET    | Get descriptive statistics of data.  |
| `/api/v1/get_dataframe`      | GET    | Retrieve the uploaded dataset.       |
| `/api/v1/upload_data`        | POST   | Upload a new dataset.                |

## Dash Dashboard

The Dash dashboard provides an interactive interface for data analysis. Features include:

- Uploading CSV files for processing.
- Visualizing data transformations.
- Selecting options for API-based data processing.

## Requirements

- Python 3.8 or higher
- Flask
- Dash
- Dash Bootstrap Components
- Pandas
- Requests

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/) for the web framework.
- [Dash](https://dash.plotly.com/) for the interactive dashboard.
- [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/) for UI components.
