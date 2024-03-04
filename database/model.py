from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class User(BaseModel):
    id: int = Field(..., alias="_id", description="The unique identifier for the user")
    userName: str = Field(..., description="The user's name")
    points: int = Field(0, description="The user's points")
    joinedDate: Optional[datetime] = Field(None, description="The date the user joined")
    createdAt: datetime = Field(default_factory=datetime.utcnow, description="The creation date of the user record")
    updatedAt: datetime = Field(default_factory=datetime.utcnow, description="The last update date of the user record")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        json_schema_extra = {
            "example": {
                "id": 123456789,
                "userName": "JohnDoe",
                "points": 100,
                "joinedAt": "2024-01-01T00:00:00Z",
                "createdAt": "2024-01-02T00:00:00Z",
                "updatedAt": "2024-01-03T00:00:00Z"
            }
        }

