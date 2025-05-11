from pymongo import MongoClient

class MongoDBConfig:
    def __init__(self, uri="mongodb://localhost:27017", database_name="dataset_db"):
        self.uri = uri
        self.database_name = database_name
        self.client = None
        self.db = None

    def connect(self):
        """Establish a connection to MongoDB."""
        self.client = MongoClient(self.uri)
        self.db = self.client[self.database_name]

    def close_connection(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()

class MongoDBHelper:
    def __init__(self, config: MongoDBConfig):
        self.config = config
        self.config.connect()

    def insert_document(self, collection_name, document):
        """Insert a document into a collection."""
        collection = self.config.db[collection_name]
        return collection.insert_one(document).inserted_id

    def find_document(self, collection_name, query):
        """Find a single document in a collection."""
        collection = self.config.db[collection_name]
        return collection.find_one(query)

    def update_document(self, collection_name, query, update_data):
        """Update a document in a collection."""
        collection = self.config.db[collection_name]
        return collection.update_one(query, {"$set": update_data})

    def delete_document(self, collection_name, query):
        """Delete a document from a collection."""
        collection = self.config.db[collection_name]
        return collection.delete_one(query)

    def list_documents(self, collection_name, query={}):
        """List all documents in a collection matching a query."""
        collection = self.config.db[collection_name]
        return list(collection.find(query))

    def close(self):
        """Close the MongoDB connection."""
        self.config.close_connection()