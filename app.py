from flask import Flask
from endpoints.detect_outliers import detect_outliers_bp
from endpoints.fill_missing import fill_missing_bp
from endpoints.feature_extraction import feature_extraction_bp
from endpoints.describe_data import describe_data_bp
from endpoints.get_dataframe import get_dataframe_bp
from endpoints.upload_data import upload_data_bp
from endpoints.dash_plot import create_dash_app

app = Flask(__name__)

prefix = '/api/v1'

app.register_blueprint(detect_outliers_bp, url_prefix=prefix)
app.register_blueprint(fill_missing_bp, url_prefix=prefix)
app.register_blueprint(feature_extraction_bp, url_prefix=prefix)
app.register_blueprint(describe_data_bp, url_prefix=prefix)
app.register_blueprint(get_dataframe_bp, url_prefix=prefix)
app.register_blueprint(upload_data_bp, url_prefix=prefix)

create_dash_app(app)

@app.route(prefix + '/')
def index():
    return "<h1>Welcome to the Data Processing API!</h1>"

if __name__ == '__main__':
    app.run(debug=True)
