import json
import requests
from func.services.fill_missing import fill_missing
from app.configs.rabbitmq_config import RabbitMQHelper, RabbitMQConfig

def process_fill_missing(ch, method, properties, body):
    """Process the fill_missing task."""
    message = json.loads(body)
    file_id = message['file_id']
    file_path = message['file_path']
    fill_method = message.get('method_fill_missing', 'mean')
    fill_value = message.get('constant_value', 0)

    outlier_method = message.get('method_outlier', 'mean')
    range = message.get('range', 100)

    try:
        # Process the file using fill_missing
        filled_file_path = fill_missing(file_path, method=fill_method, fill_value=fill_value)

        # Update preprocessing status to 33%
        update_data = {
            "file_id": file_id,
            "step_preprocess": "fill_missing",
            "percentage_completed": 33,
            "file_path_preprocess": filled_file_path,
            "status": "pending"
        }
        requests.post("http://localhost:5000/api/preprocessing", json=update_data)

        # Publish message to the next queue (detect_outliers)
        next_message = {
            "file_id": file_id,
            "file_path": filled_file_path,
            "step_preprocess": "detect_outliers",
            "method_fill_missing": fill_method,
            "constant_value": fill_value,
            "method_outlier": outlier_method,
            "range": range,
            "status": "pending",
            "percentage_completed": 33
        }
        rabbitmq_helper.publish_message("dataset_exchange_preprocess", "detect_outliers", json.dumps(next_message))

    except Exception as e:
        print(f"Error processing fill_missing: {e}")

# Initialize RabbitMQ
rabbitmq_config = RabbitMQConfig()
rabbitmq_helper = RabbitMQHelper(rabbitmq_config)
rabbitmq_helper.consume_messages("dataset_queue_fill_missing", process_fill_missing)