import os
from dotenv import load_dotenv


from fastapi import FastAPI, Response, status, Body, HTTPException
from models import ConnectionModel, UpdateConnectionModel, ConnectionCollection
from db_connection import Database


from bson.objectid import ObjectId

from fastapi.middleware.cors import CORSMiddleware


load_dotenv()  # take environment variables from .env.


uri = os.environ.get('MONGODB_URI')
db: Database = Database(uri)
db.connect(database=os.environ.get('DATABASE_NAME'), collection='connections')


app: FastAPI = FastAPI()


origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/connections/",
         response_description="List all students",
         response_model=ConnectionCollection,
         response_model_by_alias=False,
         )
def list_connections():
    return ConnectionCollection(connections=db.find())


@app.post(
    "/connections/",
    response_description="Create a new connection",
    response_model=ConnectionModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False
)
def create_connection(connection: ConnectionModel = Body(...)):
    """
    Insert a new connection record.

    A unique id will be created and returned in the response.
    """

    new_connection = db.insert_one(
        connection.model_dump(by_alias=True, exclude=["id"])
    )
    created_connection = db.find_one({"_id": new_connection.inserted_id})
    return created_connection


@app.get(
    "/connections/{id}",
    response_description="Get a single connection",
    response_model=ConnectionModel,
    response_model_by_alias=False
)
def show_connection(id: str):
    """
    Get the record for a specific connection, looked up by `id`.
    """
    if (
        connection := db.find_one({"_id": ObjectId(id)})
    ) is not None:
        return connection
    raise HTTPException(status_code=404, detail=f"Connection {id} not found")


@app.put("/connections/{id}",
         response_description="Update a connection",
         response_model=ConnectionModel,
         response_model_by_alias=False
         )
def update_connection(id: str, connection: UpdateConnectionModel):
    """
    Update individual fields of an existing connection record.

    Only the provided fields will be updated.
    Any missing or `null` fields will be ignored.
    """
    connection = {
        key: value
        for key, value in connection.model_dump(by_alias=True).items()
        if value is not None
    }

    if len(connection) == 0:
        raise HTTPException(status_code=400, detail="No fields provided")
    x = db.update_one({"_id": ObjectId(id)}, connection)
    print(x)
    updated_connection = db.find_one({"_id": ObjectId(id)})
    if updated_connection is None:
        raise HTTPException(
            status_code=404,
            detail=f"Connection {id} not found"
        )
    return updated_connection


@app.delete("/connections/{id}",
            response_description="Delete a connection",
            # status_code=status.HTTP_204_NO_CONTENT
            )
def delete_connection(id: str):
    """
    Delete a connection record.
    """
    x = db.delete_one({"_id": ObjectId(id)})

    if x.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Connection {id} not found"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
