import pytest
from flask import Flask
from app import app as flask_app

@pytest.fixture
def client():
    with flask_app.test_client() as client:
        yield client

def test_index(client):
    response = client.get('/api/v1/')
    assert response.status_code == 200
    assert b"Welcome to the Data Processing API!" in response.data

def test_upload_data_no_file(client):
    response = client.post('/api/v1/upload')
    assert response.status_code == 400
    assert response.json == {"error": "No file part in the request"}

def test_get_dataframe_file_not_found(client, monkeypatch):
    monkeypatch.setattr("endpoints.get_dataframe.file_path", "non_existent_file.csv")
    response = client.get('/api/v1/get_dataframe')
    assert response.status_code == 404
    assert response.json == {"error": "File not found"}

def test_describe_data_file_not_found(client, monkeypatch):
    monkeypatch.setattr("endpoints.describe_data.file_path", "non_existent_file.csv")
    response = client.get('/api/v1/describe')
    assert response.status_code == 500
    assert "error" in response.json

def test_fill_missing_file_not_found(client, monkeypatch):
    monkeypatch.setattr("endpoints.fill_missing.file_path", "non_existent_file.csv")
    response = client.get('/api/v1/fill_missing?method=mean')
    assert response.status_code == 404
    assert response.json == {"error": "File not found"}

def test_detect_outliers_file_not_found(client, monkeypatch):
    monkeypatch.setattr("endpoints.detect_outliers.file_path", "non_existent_file.csv")
    response = client.get('/api/v1/detect_outliers?method=mean')
    assert response.status_code == 500
    assert "error" in response.json

def test_feature_extraction_file_not_found(client, monkeypatch):
    monkeypatch.setattr("endpoints.feature_extraction.file_path", "non_existent_file.csv")
    response = client.get('/api/v1/feature_extraction?top_x=10')
    assert response.status_code == 404
    assert "error" in response.json

def test_upload_data_success(client, tmp_path):
    # Create a temporary CSV file
    temp_file = tmp_path / "test_data.csv"
    temp_file.write_text("col1,col2\n1,2\n3,4")

    with open(temp_file, "rb") as file:
        response = client.post('/api/v1/upload', data={'file': (file, 'test_data.csv')})
    
    assert response.status_code == 200
    assert response.json["message"] == "File uploaded successfully"

def test_upload_data_no_selected_file(client):
    response = client.post('/api/v1/upload', data={'file': (None, '')})
    assert response.status_code == 400
    assert response.json == {"error": "No selected file"}

def test_describe_data_success(client, monkeypatch, tmp_path):
    # Create a temporary CSV file
    temp_file = tmp_path / "valid_data.csv"
    temp_file.write_text("col1,col2\n1,2\n3,4")

    # Mock the file path to point to the temporary CSV file
    monkeypatch.setattr("endpoints.describe_data.file_path", str(temp_file))

    response = client.get('/api/v1/describe')
    assert response.status_code == 200

    # Check if the response contains statistical data for the columns
    response_json = response.json
    assert "col1" in response_json
    assert "col2" in response_json
    assert "mean" in response_json["col1"]  # Check if "mean" exists in the statistics for "col1"
    assert "mean" in response_json["col2"]  # Check if "mean" exists in the statistics for "col2"

def test_fill_missing_invalid_method(client):
    response = client.get('/api/v1/fill_missing?method=invalid')
    assert response.status_code == 400
    assert response.json == {"error": "Invalid method. Only \"mean\", \"constant\", \"linear\" are supported."}

def test_detect_outliers_invalid_method(client, monkeypatch):
    monkeypatch.setattr("endpoints.detect_outliers.file_path", "data/valid_data.csv")
    response = client.get('/api/v1/detect_outliers?method=invalid')
    assert response.status_code == 500
    assert "error" in response.json