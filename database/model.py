from pydantic import BaseModel, Field
from pydantic.functional_validators import BeforeValidator
from datetime import datetime
from typing import Optional
from bson import ObjectId
from enum import Enum
from typing_extensions import Annotated


class User(BaseModel):
    id: int = Field(..., alias="_id", description="The unique identifier for the user")
    userName: str = Field(..., description="The user's name")
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
    attend = "attend"
    react = "react"
    receive = "receive"
    awaken = "awaken"
    poll = "poll"
    lotto = "lotto"


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
    channelId: int = Field(default=None, description="The Discord channel's id")
    activity: ActivityType = Field(
        ..., description="The actual activity of react, receive, attend"
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
                "channelId": "1095522779165638716",
                "activity": "react",
                "reward": 5,
                "emoji": "🫵🏻",
                "createdAt": "2024-01-01T00:00:00Z",
            }
        }
