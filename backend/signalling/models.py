"""
Models with Pydantic
"""
import datetime
from bson.objectid import ObjectId

from pydantic import BaseModel, Field

from db_connection import Database


class Connection(BaseModel):
    id: ObjectId = Field(default_factory=ObjectId, primary_key=True, alias='_id')
    status: bool = Field(default=False)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
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
    update_at: datetime.datetime

    class Config:
        json_schema_extra = {
            "example": {
                "status": 0
            }
        }


conn_obj = Connection(
    status=0
)

# try:
#     print(conn_obj.model_dump(by_alias=True))
# except Exception as ex:
#     print(ex)

Database.initialize()
# Database.delete_index('connections', "created_at")
Database.create_index('connections', "created_at", expireAfterSeconds=3600)  # 1 hour


# Database.DATABASE['connections'].create_index("created_at", expireAfterSeconds=3600)
# print(list(Database.DATABASE['connections'].list_indexes()))

id = Database.insert('connections',
                     conn_obj.model_dump(by_alias=True)
                     ).inserted_id
print(id)

print(Database.find_one('connections', {'_id': id}))
