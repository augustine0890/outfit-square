from pydantic import BaseModel, Field
from pydantic.functional_validators import BeforeValidator
from datetime import datetime
from typing import Optional, List
from bson import ObjectId
from enum import Enum
from typing_extensions import Annotated


class UpdateUserPoints(str, Enum):
    SUCCESS = "success"
    MAX_POINTS_REACHED = "max_points_reached"
    ERROR = "error"


class User(BaseModel):
    id: int = Field(..., alias="_id", description="The unique identifier for the user")
    userName: Optional[str] = Field(None, description="The user's name")
    points: int = Field(..., description="The user's points")
    joinedDate: Optional[datetime] = Field(None, description="The date the user joined")
    createdAt: datetime = Field(
        default_factory=datetime.utcnow,
        description="The creation date of the user record",
    )
    updatedAt: datetime = Field(
        default_factory=datetime.utcnow,
        description="The last update date of the user record",
    )

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        json_schema_extra = {
            "example": {
                "id": 123456789,
                "userName": "augustine",
                "points": 100,
                "joinedAt": "2024-01-01T00:00:00Z",
                "createdAt": "2024-01-02T00:00:00Z",
                "updatedAt": "2024-01-03T00:00:00Z",
            }
        }


class ActivityType(str, Enum):
    ATTEND = "attend"
    REACT = "react"
    RECEIVE = "receive"
    SHARING = "sharing"
    REVOKE = "revoke"
    LOTTO = "lotto"


# Represents an ObjectId field in the database.
# It will be represented as a `str` on the model so that it can be serialized to JSON.
PyObjectId = Annotated[str, BeforeValidator(str)]


class Activity(BaseModel):
    id: Optional[PyObjectId] = Field(
        alias="_id",
        default=None,
        description="The unique identifier for the activities",
    )
    dcId: int = Field(..., description="The Discord user's id")
    dcUsername: str = Field(..., description="The Discord user's username")
    messageId: int = Field(default=None, description="The Discord message's id")
    channel: str = Field(default=None, description="The Discord message's channel name")
    activity: ActivityType = Field(
        ..., description="The actual activity of react, receive, attend, poll, lotto"
    )
    reward: int = Field(..., description="The given points reacted to")
    emoji: str = Field(None, description="The emoji used to react to")
    createdAt: datetime = Field(
        use_enum_values=True,
        default_factory=datetime.utcnow,
        description="The creation date of the activity record",
    )

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        json_schema_extra = {
            "example": {
                "id": "659b899d3c9b09b1579fa07a",
                "dcUsername": "augustine",
                "messageId": "1095522779165638716",
                "channel": "ugc-idea",
                "activity": "react",
                "reward": 5,
                "emoji": "🫵🏻",
                "createdAt": "2024-01-01T00:00:00Z",
            }
        }


class LottoDraw(BaseModel):
    id: Optional[PyObjectId] = Field(
        alias="_id", default=None, description="The identifier of the Lotto Draw"
    )
    numbers: List[int] = Field(
        ...,
        description="List of integers representing the Lotto Draw numbers",
    )
    year: int = Field(..., description="The current year of the Lotto Draw")
    weekNumber: int = Field(
        ..., description="The current week number of the Lotto Draw"
    )
    createdAt: datetime = Field(
        default_factory=datetime.utcnow,
        description="The Date and time when the Lotto Draw record was created",
    )

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        json_schema_extra = {
            "example": {
                "id": "659b239d3c9b05d1579fa07a",
                "numbers": [3, 7, 1, 9],
                "year": 2024,
                "weekNumber": 11,
                "createdAt": "2024-01-01T00:00:00Z",
            }
        }


class LottoGuess(BaseModel):
    id: Optional[PyObjectId] = Field(
        alias="_id", default=None, description="The identifier of the lotto guess"
    )
    dcId: int = Field(
        ...,
        description="The Discord user ID of the participant who submitted the guess",
    )
    dcUsername: str = Field(
        ...,
        description="The Discord username of the participant who submitted the guess",
    )
    numbers: List[int] = Field(
        ...,
        description="List of integers representing the participant's guessed lotto numbers",
    )
    year: int = Field(..., description="Year in which the guess was submitted")
    weekNumber: int = Field(
        ..., description="Week number within the year when the guess was submitted"
    )
    matchedCount: Optional[int] = Field(
        ...,
        description="Number of matches between the participant's guess and the winning numbers (optional)",
    )
    isMatched: Optional[bool] = Field(
        ...,
        description="Boolean flag indicating if the participant had any matching numbers (optional)",
    )
    points: Optional[int] = Field(
        ..., description="The points awarded to the participant if they win"
    )
    dmSent: Optional[bool] = Field(
        default=False,
        description="Flag indicating whether a direct message (DM) was sent to the participant regarding their guess "
        "(optional)",
    )
    createdAt: datetime = Field(
        default_factory=datetime.utcnow,
        description="The Date and time when the Lotto guess record was created",
    )
    updatedAt: datetime = Field(
        default_factory=datetime.utcnow,
        description="The Date and time when the Lotto guess record was last updated",
    )

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        json_schema_extra = {
            "example": {
                "id": "659b239d3c9b05d1579fa07a",
                "dcUsername": "augustine",
                "numbers": [3, 7, 1, 9],
                "year": 2024,
                "weekNumber": 11,
                "matchedCount": 3,
                "isMatched": True,
                "points": 5000,
                "dmSent": True,
                "createdAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-01T00:00:00Z",
            }
        }
