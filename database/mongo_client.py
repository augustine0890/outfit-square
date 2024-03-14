from pymongo import MongoClient
from .model import User, Activity, ActivityType, LottoGuess, LottoDraw
from util.helper import get_week_number, lotto_drawing
from datetime import datetime, timezone
from typing import List, Optional


class MongoDBInterface:
    def __init__(self, uri: str, dbname: str):
        self.client = MongoClient(uri)
        self.db = self.client[dbname]
        self.user_collection = self.db["user"]
        self.activity_collection = self.db["activity"]
        self.lottoguess_collection = self.db["lottoguess"]
        self.lottodraw_collection = self.db["lottodraw"]

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
        # Specify the fields to return
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

    # Calculate and return the rank of a user based on their points
    def get_user_rank(self, user_id: int) -> dict:
        # Define the MongoDB aggregation pipeline
        pipeline = [
            {
                "$match": {"points": {"$exists": True}}
            },  # Filter the documents that have 'points'
            {"$sort": {"points": -1}},  # Sort documents
            {
                "$group": {"_id": None, "rankings": {"$push": "$_id"}}
            },  # Group all documents to create a rankings list
            {
                "$project": {
                    "rankIndex": {
                        "$indexOfArray": ["$rankings", user_id]
                    },  # Find the index (rank) of the user_id in the rankings
                    "count": {"$size": "$rankings"},
                }
            },
            {
                "$project": {"rank": {"$add": ["$rankIndex", 1]}, "count": 1}
            },  # Adjust rank to be 1-based instead of 0-based
        ]
        # Execute the aggregation pipeline
        result = list(self.user_collection.aggregate(pipeline))
        if result:
            return {"rank": result[0]["rank"], "count": result[0]["count"]}
        else:
            return {"rank": None, "count": 0}

    def add_weekly_draw(self) -> bool:
        """Return True if a new draw was added, False otherwise."""
        # Get the current week number
        current_year, current_week = get_week_number()
        draw_numbers: List[int] = lotto_drawing()

        # Check if a draw for the current week already exists
        if not self.lottodraw_collection.find_one(
            {"year": current_year, "weekNumber": current_week}
        ):
            # Create and insert the LottoDraw
            lotto_draw = LottoDraw(
                numbers=draw_numbers, year=current_year, weekNumber=current_week
            )
            lotto_draw_dict = lotto_draw.dict(by_alias=True, exclude_none=True)
            self.lottodraw_collection.insert_one(lotto_draw_dict)
            return True
        return False

    def get_lotto_draw(self, year: int, week_number: int) -> Optional[List[int]]:
        """A list of integers representing the lotto draw numbers if found, otherwise returns None"""
        filter_week = {"year": year, "week_number": week_number}
        result = self.lottodraw_collection.find_one(filter_week)
        return result.get("numbers") if result else None

    def try_add_lotto_guess(self, guess: LottoGuess) -> bool:
        """True if the guess was successfully added, False if the user has reached the maximum number of guesses for
        the week."""
        guess_dict = guess.dict(by_alias=True, exclude_none=True)
        # Check how many guesses the user has made this week
        count_guess = self.lottoguess_collection.count_documents(
            {"dcId": guess_dict["dcId"], "weekNumber": guess_dict["weekNumber"]}
        )
        # If the user has made 5 or more guesses this week, return false
        if count_guess < 5:
            self.lottoguess_collection.insert_one(guess_dict)
            return True

        return False
