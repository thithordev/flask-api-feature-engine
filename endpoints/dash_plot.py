from flask import Blueprint, current_app
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from dash.dash_table import DataTable
import pandas as pd
import requests
import base64
import io

file_path = "data/selected_features.csv"
original_data_path = "data/dummy_data_with_outliers.csv"
transformed_data_path = "data/transformed_data.csv"
dash_plot_bp = Blueprint('dash_plot', __name__)

def create_dash_app(flask_app):
    app_dash = dash.Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/',
        external_stylesheets=[dbc.themes.BOOTSTRAP],
    )

    app_dash.layout = dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("Data Analysis Dashboard", className="text-center text-primary mb-4"), width=12)
        ]),

        # File Upload Section
        dbc.Row([
            dbc.Col([
                html.H3("Upload CSV File", className="text-secondary"),
                dcc.Upload(
                    id='upload-data',
                    children=dbc.Button("Upload File", color="primary", className="mt-2"),
                    multiple=False,
                    accept='.csv'
                ),
                html.Div(id='upload-status', className="mt-2 text-success")
            ], width=12)
        ], className="mb-4"),

        # Dropdowns and Inputs for APIs
        dbc.Row([
            dbc.Col([
                html.H3("Data Processing Options", className="text-secondary"),
                html.Label("Fill Missing Values:", className="mt-2"),
                dcc.Dropdown(
                    id='fill-missing-method',
                    options=[
                        {'label': 'Mean', 'value': 'mean'},
                        {'label': 'Constant', 'value': 'constant'},
                        {'label': 'Linear', 'value': 'linear'}
                    ],
                    placeholder="Select a method",
                    className="mb-3"
                ),
                html.Label("Detect Outliers:", className="mt-2"),
                dcc.Dropdown(
                    id='detect-outliers-method',
                    options=[
                        {'label': 'Mean', 'value': 'mean'},
                        {'label': 'Median', 'value': 'median'}
                    ],
                    placeholder="Select a method",
                    className="mb-3"
                ),
                html.Label("Feature Extraction (Top %):", className="mt-2"),
                dcc.Input(
                    id='feature-extraction-top-x',
                    type='number',
                    min=1,
                    max=100,
                    placeholder="Enter a percentage (1-100)",
                    className="mb-3"
                ),
                dbc.Button("Analyze Data", id='analyze-button', color="success", className="mt-2"),
                html.Div(id='analysis-status', className="mt-2 text-info")
            ], width=12)
        ], className="mb-4"),

        # Data Tables Section
        dbc.Row([
            dbc.Col([
                html.H3("Original Data", className="text-secondary"),
                dcc.Loading(
                    DataTable(
                        id='original-data-table',
                        style_table={'overflowX': 'auto'},
                        style_cell={'textAlign': 'left', 'minWidth': '100px', 'maxWidth': '200px', 'whiteSpace': 'normal'},
                        page_size=10
                    ),
                    type='circle'
                )
            ], width=12, className="mb-4"),
            dbc.Col([
                html.H3("Transformed Data", className="text-secondary"),
                dcc.Loading(
                    DataTable(
                        id='transformed-data-table',
                        style_table={'overflowX': 'auto'},
                        style_cell={'textAlign': 'left', 'minWidth': '100px', 'maxWidth': '200px', 'whiteSpace': 'normal'},
                        page_size=10
                    ),
                    type='circle'
                )
            ], width=12, className="mb-4")
        ]),

        # Data Description Section
        dbc.Row([
            dbc.Col([
                html.H3("Data Description", className="text-secondary"),
                dcc.Loading(
                    DataTable(
                        id='data-description-table',
                        style_table={'overflowX': 'auto'},
                        style_cell={'textAlign': 'left', 'minWidth': '100px', 'maxWidth': '200px', 'whiteSpace': 'normal'},
                        page_size=10
                    ),
                    type='circle'
                )
            ], width=12, className="mb-4")
        ]),

        # Graph Section
        dbc.Row([
            dbc.Col([
                html.H3("Data Visualization", className="text-secondary"),
                dcc.Graph(id='data-graph')
            ], width=12)
        ]),

        # Box Plot Section
        dbc.Row([
            dbc.Col([
                html.H3("Box Plot Visualization", className="text-secondary"),
                dcc.Loading(
                    dcc.Graph(id='box-plot-graph'),
                    type='circle'
                )
            ], width=12)
        ])
    ], fluid=True)

    @app_dash.callback(
        Output('upload-status', 'children'),
        Input('upload-data', 'contents'),
        State('upload-data', 'filename')
    )
    def upload_file(contents, filename):
        if contents is not None:
            try:
                # Decode the uploaded file
                content_type, content_string = contents.split(',')
                decoded = base64.b64decode(content_string)
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

                # Send file to the upload API
                response = requests.post(
                    'http://localhost:5000/api/v1/upload',
                    files={'file': (filename, decoded, 'text/csv')}
                )
                if response.status_code == 200:
                    return "File uploaded successfully!"
                else:
                    return f"Upload failed: {response.json().get('error', 'Unknown error')}"
            except Exception as e:
                return f"Error: {str(e)}"
        return ""

    @app_dash.callback(
        Output('analysis-status', 'children'),
        Input('analyze-button', 'n_clicks'),
        State('fill-missing-method', 'value'),
        State('detect-outliers-method', 'value'),
        State('feature-extraction-top-x', 'value')
    )
    def analyze_data(n_clicks, fill_method, outlier_method, top_x):
        if n_clicks > 0:
            try:
                # Step 1: Call fill_missing API
                if fill_method:
                    response = requests.get(
                        f'http://localhost:5000/api/v1/fill_missing?method={fill_method}'
                    )
                    if response.status_code != 200:
                        return f"Fill Missing API failed: {response.json().get('error', 'Unknown error')}"

                # Step 2: Call detect_outliers API
                if outlier_method:
                    response = requests.get(
                        f'http://localhost:5000/api/v1/detect_outliers?method={outlier_method}'
                    )
                    if response.status_code != 200:
                        return f"Detect Outliers API failed: {response.json().get('error', 'Unknown error')}"

                # Step 3: Call feature_extraction API
                if top_x:
                    response = requests.get(
                        f'http://localhost:5000/api/v1/feature_extraction?top_x={top_x}'
                    )
                    if response.status_code != 200:
                        return f"Feature Extraction API failed: {response.json().get('error', 'Unknown error')}"

                return "Data analysis completed successfully!"
            except Exception as e:
                return f"Error: {str(e)}"
        return ""

    @app_dash.callback(
        [Output('original-data-table', 'data'),
         Output('original-data-table', 'columns')],
        Input('analyze-button', 'n_clicks')
    )
    def display_original_data(n_clicks):
        if n_clicks > 0:
            try:
                df = pd.read_csv(original_data_path)
                return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]
            except Exception as e:
                return [], []
        return [], []

    @app_dash.callback(
        [Output('transformed-data-table', 'data'),
         Output('transformed-data-table', 'columns')],
        Input('analyze-button', 'n_clicks')
    )
    def display_transformed_data(n_clicks):
        if n_clicks > 0:
            try:
                df = pd.read_csv(transformed_data_path)
                return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]
            except Exception as e:
                return [], []
        return [], []

    @app_dash.callback(
        [Output('data-description-table', 'data'),
         Output('data-description-table', 'columns')],
        Input('analyze-button', 'n_clicks')
    )
    def update_data_description(n_clicks):
        if n_clicks > 0:
            try:
                # Gọi API /describe
                response = requests.get('http://localhost:5000/api/v1/describe')
                if response.status_code == 200:
                    description = response.json()
                    # Chuyển đổi dữ liệu mô tả thành định dạng phù hợp cho DataTable
                    df_description = pd.DataFrame(description)
                    df_description.reset_index(inplace=True)
                    df_description.rename(columns={'index': 'Statistic'}, inplace=True)
                    return df_description.to_dict('records'), [{"name": i, "id": i} for i in df_description.columns]
                else:
                    return [], []
            except Exception as e:
                return [], []
        return [], []

    @app_dash.callback(
        Output('data-graph', 'figure'),
        Input('analyze-button', 'n_clicks')
    )
    def update_graph(n_clicks):
        if n_clicks > 0:
            try:
                # Fetch data using get_dataframe API
                response = requests.get('http://localhost:5000/api/v1/get_dataframe')
                if response.status_code == 200:
                    df = pd.DataFrame(response.json())

                    # Create a bar chart for variance
                    numeric_df = df.select_dtypes(include=['number'])
                    return {
                        'data': [{'x': numeric_df.columns, 'y': numeric_df.var(), 'type': 'bar'}],
                        'layout': {'title': 'Variance Analysis'}
                    }
                else:
                    return {'data': [], 'layout': {'title': 'Error fetching data'}}
            except Exception as e:
                return {'data': [], 'layout': {'title': f'Error: {str(e)}'}}
        return {'data': [], 'layout': {'title': 'No Data Available'}}

    @app_dash.callback(
        Output('box-plot-graph', 'figure'),
        Input('analyze-button', 'n_clicks')
    )
    def update_box_plot(n_clicks):
        if n_clicks > 0:
            try:
                # Gọi API /get_dataframe để lấy dữ liệu
                response = requests.get('http://localhost:5000/api/v1/get_dataframe')
                if response.status_code == 200:
                    df = pd.DataFrame(response.json())

                    # Tạo Box Plot
                    numeric_columns = df.select_dtypes(include=['number']).columns
                    if numeric_columns.empty:
                        return {
                            'data': [],
                            'layout': {'title': 'No numeric data available for Box Plot'}
                        }

                    fig = {
                        'data': [
                            {
                                'y': df[col],
                                'type': 'box',
                                'name': col
                            } for col in numeric_columns
                        ],
                        'layout': {
                            'title': 'Box Plot of Numeric Features',
                            'yaxis': {'title': 'Values'},
                            'xaxis': {'title': 'Features'},
                            'boxmode': 'group'
                        }
                    }
                    return fig
                else:
                    return {
                        'data': [],
                        'layout': {'title': 'Error fetching data for Box Plot'}
                    }
            except Exception as e:
                return {
                    'data': [],
                    'layout': {'title': f'Error: {str(e)}'}
                }
        return {
            'data': [],
            'layout': {'title': 'No Data Available'}
        }

    return app_dash
