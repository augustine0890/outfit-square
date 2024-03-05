from pymongo import MongoClient
from .model import User, Activity
import datetime


class MongoDBInterface:
    def __init__(self, uri: str, dbname: str):
        self.client = MongoClient(uri)
        self.db = self.client[dbname]
        self.user_collection = self.db["user"]
        self.activity_collection = self.db["activity"]

    def add_user(self, user: User):
        # Ensure that the _id is properly set as an integer
        user_dict = user.dict(by_alias=True, exclude_none=True)
        result = self.user_collection.insert_one(user_dict)
        return result.inserted_id

    def add_activity(self, activity: Activity):
        activity_dict = activity.dict(by_alias=True, exclude_none=True)
        result = self.activity_collection.insert_one(activity_dict)
        return result.inserted_id
