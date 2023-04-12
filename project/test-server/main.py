import asyncio
import websockets
import json
from math import cos, sin, pi

# Initialize an empty set to keep track of connected clients
clients = set()

count = 0
max_val = 360
rad = 3

async def handle_websocket(websocket, path):
    # This function handles incoming WebSocket connections.
    # It adds the client to the set of connected clients,
    # then waits for incoming messages and broadcasts them to all clients.
    clients.add(websocket)
    print(f"New client connected: {websocket.remote_address}")

    try:
        async for message in websocket:
            print(f"Received message from {websocket.remote_address}: {message}")

    except websockets.ConnectionClosed:
        print(f"Client disconnected: {websocket.remote_address}")

    finally:
        # Remove the client from the set of connected clients
        clients.remove(websocket)

async def send_data():
    global count
    x = rad * cos(pi * (count % max_val) / 180)
    y = rad * sin(pi * (count % max_val) / 180)
    z = 0
    
    count += 10
    
    for client in clients:
        await client.send(json.dumps({
        "x": x,
        "y": y,
        "z": z,
    }))

async def create_server():
    async with websockets.serve(handle_websocket, "localhost", 8765):
        print("Websocket server started!")
        await asyncio.Future()

async def main():
    server_task = asyncio.create_task(create_server())
    while True:
        await send_data()
        await asyncio.sleep(0.5)

if __name__ == '__main__':
    asyncio.run(main())

