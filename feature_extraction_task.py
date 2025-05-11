import json
import requests
from services.feature_extraction import feature_extraction
from configs.rabbitmq_config import RabbitMQHelper, RabbitMQConfig

def process_feature_extraction(ch, method, properties, body):
    """Process the feature_extraction task."""
    message = json.loads(body)
    file_id = message['file_id']
    file_path = message['file_path']
    top_x = message.get('range', 100)

    try:
        # Process the file using feature_extraction
        feature_file_path = feature_extraction(file_path, top_x=top_x)

        # Update preprocessing status to 100% and mark as completed
        update_data = {
            "file_id": file_id,
            "step_preprocess": "feature_extraction",
            "percentage_completed": 100,
            "status": "completed"
        }
        requests.post("http://localhost:5000/api/preprocessing", json=update_data)

    except Exception as e:
        print(f"Error processing feature_extraction: {e}")

# Initialize RabbitMQ
rabbitmq_config = RabbitMQConfig()
rabbitmq_helper = RabbitMQHelper(rabbitmq_config)
rabbitmq_helper.consume_messages("dataset_queue_feature_extraction", process_feature_extraction)