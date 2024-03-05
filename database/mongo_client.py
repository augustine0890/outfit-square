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

    def get_user_points(self, user_id: int) -> int:
        # Create a filter to find the user by id
        filter_id = {"_id": user_id}
        # Specify the fields to return (only "points")
        projection = {"points": 1}
        result = self.user_collection.find(filter_id, projection)
        # If a user is found, return their points. Otherwise, return 0
        if result:
            return result.get("points", 0)
        else:
            return 0
