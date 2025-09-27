from pymongo import MongoClient
from django.conf import settings


def get_mongo_collection():
    client = MongoClient(settings.MONGO_URI)
    db = client[settings.MONGO_DATABASE]
    collection = db['messages']
    return collection