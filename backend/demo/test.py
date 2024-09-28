from typing import Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
import uvicorn
from fastapi.templating import Jinja2Templates
import json
import asyncio
import string
import random


app = FastAPI()


clients = {}


def generate_unique_id(length=3):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


# Example usage:
unique_id = generate_unique_id()
print(unique_id)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
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
                    await other_client_websocket.send_text(json.dumps(data_json))

    except WebSocketDisconnect:
        # Remove the disconnected client from the clients dictionary
        clients.pop(client_id)
        print(f"WebSocket {client_id} disconnected")
        await websocket.close()


available_connections = []
pending_connections = []


# Dictionary to store user connections and their status
connections: Dict[WebSocket, str] = {}

# Constants for user status
STATUS_AVAILABLE = "available"
STATUS_CONNECTED = "connected"
STATUS_PENDING = "pending"


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections[websocket] = STATUS_AVAILABLE
    partner_websocket = None

    try:
        # Find a partner for the connected user
        for ws, status in connections.items():
            if ws != websocket and status == STATUS_AVAILABLE:
                partner_websocket = ws
                break

        # If a partner is found, connect them
        if partner_websocket:
            connections[websocket] = STATUS_CONNECTED
            connections[partner_websocket] = STATUS_CONNECTED
            await websocket.send_json({"message": "Connected to partner11111"})
            await partner_websocket.send_json({"message": "Connected to partner11111"})
        else:
            await websocket.send_json({"message": "Waiting for a partner..."})

            # Wait for a partner to connect
            while True:
                for ws, status in connections.items():
                    if ws != websocket and status == STATUS_AVAILABLE:
                        partner_websocket = ws
                        connections[websocket] = STATUS_CONNECTED
                        connections[partner_websocket] = STATUS_CONNECTED
                        await websocket.send_json({"message": "Connected to partner22222"})
                        await partner_websocket.send_json({"message": "Connected to partner22222"})
                        break
                if partner_websocket:
                    break
                else:
                    await asyncio.sleep(1)  # Adjust the sleep time as needed

        # Handle incoming messages from the WebSocket
        while True:
            data = await websocket.receive_json()
            # Forward the messages to the partner WebSocket
            if partner_websocket:
                await partner_websocket.send_json(data)

            # Check for incoming messages from the partner WebSocket
            try:
                partner_data = await asyncio.wait_for(partner_websocket.receive_json(), timeout=1)
                await websocket.send_json(partner_data)
            except asyncio.TimeoutError:
                pass  # Continue if no message received from the partner within the timeout

    except WebSocketDisconnect:
        connections.pop(websocket, None)
        if partner_websocket and partner_websocket in connections:
            connections[partner_websocket] = STATUS_AVAILABLE
            await partner_websocket.send_json({"message": "Partner disconnected"})

    finally:
        print(connections)


@app.websocket("/change_user")
async def change_user(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if connections[websocket] == STATUS_CONNECTED:
                partner = [conn for conn, status in connections.items(
                ) if status == STATUS_CONNECTED and conn != websocket][0]
                connections[websocket] = STATUS_AVAILABLE
                connections[partner] = STATUS_AVAILABLE
                available_connections.append(websocket)
                available_connections.append(partner)
                await websocket.send_text(json.dumps({"message": "Partner changed"}))
                await partner.send_text(json.dumps({"message": "Partner changed"}))

                if len(pending_connections) > 0:
                    new_partner = pending_connections.pop(0)
                    connections[websocket] = STATUS_CONNECTED
                    connections[new_partner] = STATUS_CONNECTED
                    await new_partner.send_text(json.dumps({"type": "offer", "offer": message["offer"]}))
                    await websocket.send_text(json.dumps({"message": "Connected to new partner"}))
                else:
                    await websocket.send_text(json.dumps({"message": "Waiting for a new partner..."}))

    except WebSocketDisconnect:
        connections.pop(websocket)
        available_connections.remove(websocket)
        pending_connections.remove(websocket)
        partner = [conn for conn, status in connections.items() if status == STATUS_CONNECTED][0]
        connections[partner] = STATUS_AVAILABLE
        available_connections.append(partner)
        await partner.send_text(json.dumps({"message": "Partner disconnected"}))


@app.websocket_route("/change_user")
async def change_user(websocket: WebSocket):
    await websocket.accept()
    if websocket in connections:
        # Mark the user as available
        connections[websocket] = STATUS_AVAILABLE
        await websocket.send_json({"message": "Waiting for a new partner..."})

        # Find a new partner to connect with
        partner = None
        for other_websocket, status in connections.items():
            if status == STATUS_AVAILABLE and other_websocket != websocket:
                partner = other_websocket
                break

        if partner:
            connections[websocket] = STATUS_CONNECTED
            connections[partner] = STATUS_CONNECTED
            await websocket.send_json({"message": "Connected to new partner"})
            await partner.send_json({"message": "Connected to new partner"})

            # Handle WebRTC handshake and video call logic here

            await websocket.receive_text()  # Wait for the connection to be closed
            await partner.receive_text()  # Wait for the connection to be closed


# Set Jinja2 templates directory
templates = Jinja2Templates(directory=".")


@app.get('/')
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
