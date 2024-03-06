from pymongo import MongoClient
from .model import User, Activity
from datetime import datetime


class MongoDBInterface:
    def __init__(self, uri: str, dbname: str):
        self.client = MongoClient(uri)
        self.db = self.client[dbname]
        self.user_collection = self.db["user"]
        self.activity_collection = self.db["activity"]

    def add_or_update_user_points(self, user: User):
        # Create a filter to find the user by id
        filter_id = {"_id": user.id}
        # Prepare the update document
        update_doc = {
            # Ensure that the _id is properly set as an integer
            "$setOnInsert": {
                "_id": user.id,
                "userName": user.userName,
                "createdAt": user.createdAt,
            },
            "$inc": {"points": user.points},
            "$set": {"updatedAt": datetime.utcnow()},
        }

        # Perform the database operation
        result = self.user_collection.update_one(filter_id, update_doc, upsert=True)

        # If a new document was inserted, return its id. Otherwise, return None.
        return result.upserted_id

    def add_activity(self, activity: Activity):
        activity_dict = activity.dict(by_alias=True, exclude_none=True)
        result = self.activity_collection.insert_one(activity_dict)
        return result.inserted_id

    def get_user_points(self, user_id: int) -> dict:
        # Create a filter to find the user by id
        filter_id = {"_id": user_id}
        # # Specify the fields to return
        projection = {"points": 1, "updatedAt": 1}
        result = self.user_collection.find_one(filter_id, projection)
        # If a user is found, return their points and updatedAt. Otherwise, return {'points': 0, 'updatedAt': None}
        if result:
            return {
                "points": result.get("points", 0),
                "updatedAt": result.get("updatedAt"),
            }
        else:
            return {"points": 0, "updatedAt": None}
