from pymongo import MongoClient
from settings import Config

def get_mongo_client():
    mongo_uri = f"mongodb://{Config.MONGO_USER}:{Config.MONGO_PASSWORD}@{Config.MONGO_HOST}:{Config.MONGO_PORT}/"
    return MongoClient(mongo_uri)

def get_database(client, dbname):
    return client[dbname]
