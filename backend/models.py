"""
Models with Pydantic
"""
from datetime import datetime
import pytz
from bson.objectid import ObjectId

from pydantic import BaseModel, Field

from db_connection import Database


def get_current_date():
    current_time = datetime.now(pytz.timezone('Asia/Calcutta'))
    return current_time


current_time = get_current_date()
print(current_time)


class Connection(BaseModel):
    id: ObjectId = Field(default_factory=ObjectId,
                         primary_key=True,
                         alias='_id')
    status: bool = Field(default=False)
    created_at: datetime = Field(default_factory=get_current_date)
    updated_at: datetime = Field(default_factory=get_current_date)
    # expiresAfterSeconds: int = Field(default=20)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "id": "ObjectId('65dada7b59da6c90515c8fbb')",
                "status": False,
                "created_at": "2022-01-01T00:00:00.000000Z",
                "updated_at": "2022-01-01T00:00:00.000000Z"
            }
        }


class ConnectionUpdate(BaseModel):
    status: bool
    update_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "status": 0
            }
        }


conn_obj = Connection(
    status=1
)

# try:
#     print(conn_obj.model_dump(by_alias=True))
# except Exception as ex:
#     print(ex)


uri = "mongodb+srv://poqt5yzgwjnfu1bgct:J4YsDqkdJo8dNoDF@omegle-django.tmnziov.mongodb.net/?retryWrites=true&w=majority&appName=omegle-django"  # noqa
db = Database(uri)
db.connect('omegle-django')


# db.create_index("connections",
#                 "created_at",
#                 expire_after_seconds=3600)  # 1 hour
# db.drop_index("connections", "created_at_1")
print(list(db.list_indexes("connections")))
# db.create_index("created_at", expireAfterSeconds=3600)
# print(list(db.list_indexes()))

# id = db.insert_one('connections',
#                    conn_obj.model_dump(by_alias=True)
#                    ).inserted_id

# print(id)
# print(db.find_one('connections', {'_id': id}).get('created_at'))
