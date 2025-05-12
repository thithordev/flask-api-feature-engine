import pika

class RabbitMQConfig:
    def __init__(self, host='localhost', port=5672, user='admin', password='admin'):
        self.host = host
        self.port = port
        self.credentials = pika.PlainCredentials(user, password)

    def create_connection(self):
        connection_params = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=self.credentials
        )
        return pika.BlockingConnection(connection_params)

class RabbitMQHelper:
    def __init__(self, config: RabbitMQConfig):
        self.config = config
        self.connection = self.config.create_connection()
        self.channel = self.connection.channel()

    def declare_exchange(self, exchange_name, exchange_type='direct'):
        self.channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type)

    def declare_queue(self, queue_name):
        self.channel.queue_declare(queue=queue_name)

    def bind_queue(self, queue_name, exchange_name, routing_key):
        self.channel.queue_bind(queue=queue_name, exchange=exchange_name, routing_key=routing_key)

    def publish_message(self, exchange_name, routing_key, message):
        self.channel.basic_publish(
            exchange=exchange_name,
            routing_key=routing_key,
            body=message
        )

    def consume_messages(self, queue_name, callback):
        def wrapper(ch, method, properties, body):
            callback(ch, method, properties, body)

        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=wrapper,
            auto_ack=True
        )
        print(f"Waiting for messages in queue: {queue_name}. To exit press CTRL+C")
        self.channel.start_consuming()

    def close_connection(self):
        self.connection.close()