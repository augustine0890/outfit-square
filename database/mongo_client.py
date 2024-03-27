from pymongo import MongoClient
import logging
from .model import User, Activity, ActivityType, LottoGuess, LottoDraw, UpdateUserPoints
from util.helper import get_week_number, lotto_drawing
from datetime import datetime, timezone
from typing import List, Optional
from util.config import Config


class MongoDBInterface:
    def __init__(self, uri: str, dbname: str):
        self.client = MongoClient(uri)
        self.db = self.client[dbname]
        self.user_collection = self.db["user"]
        self.activity_collection = self.db["activity"]
        self.lottoguess_collection = self.db["lottoguess"]
        self.lottodraw_collection = self.db["lottodraw"]

    def add_or_update_user_points(self, user: User):
        # Get the current points of the user
        current_points_result = self.get_user_points(user_id=user.id)
        current_points = current_points_result["points"]
        points_to_add = user.points
        if user.points > 0:  # Adding points
            if current_points >= Config.MAX_POINTS:
                # Current points already exceed max, do nothing
                return UpdateUserPoints.MAX_POINTS_REACHED, current_points
            if current_points + user.points > Config.MAX_POINTS:
                # Adjust points to add if it would exceed max points
                points_to_add = Config.MAX_POINTS - current_points
        # If subtracting points, points_to_add remains as user.points (allow negative to decrease points)

        # Create a filter to find the user by id
        filter_id = {"_id": user.id}
        # Prepare the update document
        update_doc = {
            # Ensure that the _id is properly set as an integer
            "$setOnInsert": {
                "_id": user.id,
                "createdAt": user.createdAt,
            },
            "$inc": {"points": points_to_add},
            "$set": {"updatedAt": datetime.utcnow()},
        }
        # Conditionally add userName if it exists
        if user.userName:
            update_doc["$setOnInsert"]["userName"] = user.userName

        # Perform the database operation
        try:
            self.user_collection.update_one(filter_id, update_doc, upsert=True)
            # Calculate the new points total for success return
            new_points = current_points + points_to_add
            return UpdateUserPoints.SUCCESS, new_points
        except Exception as e:
            # Log the error for further investigation
            logging.error(f"Error updating user points for {user.id}: {e}")
            return (
                UpdateUserPoints.ERROR,
                current_points,
            )  # Return current points in case of error

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
        filter_week = {"year": year, "weekNumber": week_number}
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

    def get_top_ten_users(self):
        """Retrieves the top 10 users from the user collection based on their points."""

        try:
            # Define the sort and limit
            sort_and_limit = [("points", -1), ("updatedAt", 1)]
            top_users_cursor = (
                self.user_collection.find({}, projection={"points": 1, "userName": 1})
                .sort(sort_and_limit)
                .limit(10)
            )

            top_users = list(top_users_cursor)
            return True, top_users
        except Exception as e:
            return False, str(e)
