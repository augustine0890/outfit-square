from pymongo import MongoClient
from .model import User, Activity, ActivityType
from datetime import datetime, timezone


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

    def add_reaction_activity(self, activity: Activity) -> bool:
        activity_dict = activity.dict(by_alias=True, exclude_none=True)
        # Use datetime.now(timezone.utc) to get the current UTC time directly
        today = datetime.utcnow().replace(
            tzinfo=timezone.utc, hour=0, minute=0, second=0, microsecond=0
        )
        # MongoDB query to count the documents
        count_reaction = self.activity_collection.count_documents(
            {
                "dcId": activity_dict["dcId"],
                "activity": activity.activity,
                "createdAt": {"$gte": today},
            }
        )

        # Logic to check activity type and react accordingly
        if (activity.activity == ActivityType.REACT and count_reaction > 4) or (
            activity.activity == ActivityType.RECEIVE and count_reaction > 9
        ):
            return False
        self.activity_collection.insert_one(activity_dict)
        return True

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
