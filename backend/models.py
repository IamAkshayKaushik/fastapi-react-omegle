"""
Models with Pydantic
"""
from datetime import datetime
import pytz
from bson.objectid import ObjectId

from pydantic import BaseModel, Field
from pydantic.functional_validators import BeforeValidator

# from db_connection import Database

from typing import Optional, List
from typing_extensions import Annotated


def get_current_date() -> datetime:
    current_time: datetime = datetime.now(pytz.timezone('Asia/Calcutta'))
    return current_time


# Represents an ObjectId field in the database.
# It will be represented as a `str` on the model
# so that it can be serialized to JSON.
PyObjectId = Annotated[str, BeforeValidator(str)]


class ConnectionModel(BaseModel):
    """
    Container for a single connection record.
    """

    # The primary key for ConnectionModel, stored as a `str` on the instance.
    # This will be aliased to `_id` when sent to MongoDB,
    # but provided as `id` in the API requests and responses.
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    status: bool = Field(default=False)
    created_at: datetime = Field(default_factory=get_current_date)
    updated_at: datetime = Field(default_factory=get_current_date)

    class Config:
        """
        Config subclass is used to configure how Pydantic should handle the
        data when creating instances of the model.
        """
        populate_by_name = True
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "status": False,
            }
        }


class UpdateConnectionModel(BaseModel):
    """
    A set of optional updates to be made to a document in the database.
    """
    status: bool = Field(default=False)
    updated_at: datetime = Field(default_factory=get_current_date)

    class Config:
        arbitrary_types_allowed = True,
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "status": False,
            }
        }


class ConnectionCollection(BaseModel):
    """
    A container holding a list of `ConnectionModel` instances.

    This exists because providing a top-level array
    in a JSON response can be a
    [vulnerability](https://haacked.com/archive/2009/06/25/json-hijacking.aspx/)
    """

    connections: List[ConnectionModel]

# conn_obj = Connection(status=1)

# # try:
# #     print(conn_obj.model_dump(by_alias=True))
# # except Exception as ex:
# #     print(ex)


# uri = "mongodb+srv://poqt5yzgwjnfu1bgct:J4YsDqkdJo8dNoDF@omegle-django.tmnziov.mongodb.net/?retryWrites=true&w=majority&appName=omegle-django"  # noqa
# db = Database(uri)
# db.connect('omegle-django', 'connections')


# db.create_index("created_at",
#                 expire_after_seconds=3600
#                 )  # 1 hour
# # db.drop_index("created_at_1")
# print(list(db.list_indexes()))

# id = db.insert_one(conn_obj.model_dump(by_alias=True)
#                    ).inserted_id

# print(id)
# print(db.find_one({'_id': id}).get('created_at'))
