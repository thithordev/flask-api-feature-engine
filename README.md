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
├── api.py                     # Main Flask application
├── func/                      # Task processing and services
│   ├── fill_missing_task.py   # Task for filling missing values
│   ├── detect_outliers_task.py # Task for detecting outliers
│   ├── feature_extraction_task.py # Task for feature extraction
│   └── services/              # Service logic for tasks
│       ├── fill_missing.py    # Logic for filling missing values
│       ├── detect_outliers.py # Logic for detecting outliers
│       ├── feature_extraction.py # Logic for feature extraction
├── app/                       # Application configurations and templates
│   ├── configs/               # Configuration files
│   │   ├── rabbitmq_config.py # RabbitMQ configuration
│   │   ├── mongodb_config.py  # MongoDB configuration
│   └── templates/             # HTML templates for the Flask app
├── uploads/                   # Directory for uploaded and processed files
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
   .venv\Scripts\activate  # On Windows
   source .venv/bin/activate  # On macOS/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python api.py
   ```

5. Access the API at `http://127.0.0.1:5000/` and the Dash dashboard at `http://127.0.0.1:5000/`.

## API Endpoints

| Endpoint                     | Method | Description                          |
|------------------------------|--------|--------------------------------------|
| `/upload`                    | POST   | Upload a new dataset.                |
| `/processSubmit`             | POST   | Submit a dataset for processing.     |
| `/api/datasets`              | GET    | Fetch all datasets.                  |
| `/api/datasets/<file_id>`    | DELETE | Delete a dataset.                    |
| `/api/datasets/<file_id>/view` | GET  | View a processed dataset in D-Tale.  |
| `/api/datasets/<file_id>/original` | GET | View the original dataset in D-Tale. |
| `/api/preprocessing`         | POST   | Update preprocessing status.         |

## Dash Dashboard

The Dash dashboard provides an interactive interface for data analysis. Features include:

- Uploading CSV files for processing.
- Visualizing data transformations.
- Selecting options for API-based data processing.

## Requirements

- Python 3.11 or higher
- Flask
- Dash
- Pandas
- Requests
- MongoDB
- RabbitMQ
- Websocket

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/) for the web framework.
- [Dash](https://dash.plotly.com/) for the interactive dashboard.
- [Feature-engine](https://feature-engine.readthedocs.io/) for feature engineering utilities.
- [D-Tale](https://github.com/man-group/dtale) for dataset visualization.
