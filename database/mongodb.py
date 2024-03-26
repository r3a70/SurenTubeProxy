import os


from pymongo import MongoClient
from pymongo.database import Database


class MongoSingleton:

    _instance: 'MongoSingleton' = None
    client: MongoClient

    def __new__(cls, *args, **kwargs) -> 'MongoSingleton':

        if cls._instance is None:

            cls._instance = super().__new__(cls)
            cls._instance.client = MongoClient(*args, **kwargs)

        return cls._instance


mongo: MongoSingleton = MongoSingleton(
    f"mongodb://{os.getenv('MONGODB_HOST')}:{int(os.getenv('MONGODB_PORT'))}"
    if not os.getenv("MONGODB_USERNAME") and not os.getenv("MONGODB_PASSWORD") else
    f"""mongodb://{os.getenv('MONGODB_USERNAME')}:{os.getenv('MONGODB_PASSWORD')}@{os.getenv('MONGODB_HOST')}:{int(os.getenv('MONGODB_PORT'))}"""
)
mongo_db: Database = mongo.client[os.getenv('MONGODB_DB_NAME')]
