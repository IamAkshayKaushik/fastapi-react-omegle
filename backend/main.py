import os
from dotenv import load_dotenv


from fastapi import (
    FastAPI,
    Request,
    Response,
    status,
    Body,
    HTTPException,
    WebSocket,
    WebSocketDisconnect
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from models import (
    ConnectionModel,
    UpdateConnectionModel,
    ConnectionCollection
)

from db_connection import Database

from bson.objectid import ObjectId
import string
import random
import json


load_dotenv()  # take environment variables from .env.


URI = os.environ.get('MONGODB_URI')
db: Database = Database(URI)
db.connect(database=os.environ.get('DATABASE_NAME'), collection='connections')


app: FastAPI = FastAPI()

# Set static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set Jinja2 templates directory
templates = Jinja2Templates(directory="templates")


origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/connections/",
         response_description="List all Connections",
         response_model=ConnectionCollection,
         response_model_by_alias=False,
         )
def list_connections(status: bool = None):
    query = {"status": status} if status is not None else {}
    return ConnectionCollection(connections=db.find(query))


@app.post(
    "/connections/",
    response_description="Create a new Connection",
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
    response_description="Get a single Connection",
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
         response_description="Update a Connection",
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
            response_description="Delete a Connection",
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


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


clients = {}


def generate_unique_id(length=3):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    A websocket endpoint for sending and receiving messages.
    """
    await websocket.accept()
    # client_id = str(websocket)  # Use the WebSocket object as the client ID
    client_id = generate_unique_id()
    # Add the new client to the clients dictionary
    clients[client_id] = websocket

    try:
        while True:
            data = await websocket.receive_text()
            data_json = json.loads(data)
            data_json["peer_id"] = client_id

            # Broadcast the message to all other clients
            for other_client_id, other_client_websocket in clients.items():
                if other_client_id != client_id:
                    await other_client_websocket.send_text(
                        json.dumps(data_json)
                    )

    except WebSocketDisconnect:
        # Remove the disconnected client from the clients dictionary
        clients.pop(client_id)
        print(f"WebSocket {client_id} disconnected")
        await websocket.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
