# mongo_utils.py
from pymongo import MongoClient
from django.conf import settings

def get_mongo_db():
    mongo_uri = getattr(settings, "MONGO_URI", "mongodb://localhost:27017")
    mongo_dbname = getattr(settings, "MONGO_DBNAME", "ai_documents")
    client = MongoClient(mongo_uri)
    return client[mongo_dbname]
