# message-processor/mongo_utils.py
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv('/Users/daniilradin/PycharmProjects/DjangoProject2/.env')  # Путь к .env

def get_mongo_collection():
    client = MongoClient(os.getenv('MONGO_URI'))
    db = client['kafka_db']
    collection = db['messages']
    return collection