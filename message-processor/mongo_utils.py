# message-processor/mongo_utils.py
from pymongo import MongoClient

def get_mongo_collection():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['kafka_db']
    collection = db['messages']
    return collection