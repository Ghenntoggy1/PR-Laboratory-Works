import asyncio
import json

import websockets

chat_rooms: dict[str, list[dict]] = {}


async def register_client(client_socket: websockets.WebSocketServerProtocol, room_id, username):
    if room_id not in chat_rooms.keys():
        print(f"Client {username} {client_socket.remote_address[0]}:{client_socket.remote_address[1]} created Room {room_id}!")
        chat_rooms[room_id] = []

        await client_socket.send(json.dumps({"type": "message", "username": "System", "message": f"Room {room_id} created!"}))

    # Check if the username is already taken
    if any(client.get("username") == username for client in chat_rooms[room_id]):
        await client_socket.send(json.dumps({"type": "error", "message": "Username already taken!"}))
        return

    # Add the client to the chat room
    chat_rooms[room_id].append({"socket": client_socket, "username": username})

    # Notify others in the room about the new client
    for client in chat_rooms[room_id]:
        if client.get("socket") != client_socket:
            await client["socket"].send(json.dumps({"type": "message", "username": username, "message": f"Client {username} {client_socket.remote_address[0]}:{client_socket.remote_address[1]} joined Room {room_id}!"}))
        else:
            await client["socket"].send(json.dumps({"type": "message", "username": username, "message": f"Welcome to Room {room_id}!"}))


async def unregister_client(client_socket: websockets.WebSocketServerProtocol):
    print(chat_rooms)
    room_id_c = None
    username = None
    for room_id in chat_rooms:
        for client in chat_rooms[room_id]:
            if client.get("socket") == client_socket:
                chat_rooms[room_id].remove(client)
                room_id_c = room_id
                username = client.get("username")
                print(f"Client {username} {client_socket.remote_address} disconnected from Room {room_id}!")
    print(chat_rooms)
    await client_socket.close()
    if len(chat_rooms[room_id_c]) == 0:
        chat_rooms.pop(room_id_c)
        print(f"Room {room_id_c} removed!")
        print(chat_rooms)
        return
    for client in chat_rooms[room_id_c]:
        await client.get("socket").send(json.dumps({"type": "message", "username": username, "message": f"Client {username} {client_socket.remote_address[0]}:{client_socket.remote_address[1]} disconnected from Room {room_id_c}!"}))


async def send_message(message: str, client_socket: websockets.WebSocketServerProtocol):
    room_id_c = None
    username = None
    for room_id in chat_rooms:
        for client in chat_rooms[room_id]:
            if client.get("socket") == client_socket:
                room_id_c = room_id
                username = client.get("username")

    for client in chat_rooms[room_id_c]:
        await client.get("socket").send(json.dumps({"type": "message", "username": username, "message": message}))


async def process_message(message: str, client_socket: websockets.WebSocketServerProtocol):
    data = json.loads(message)
    print(f"Data: {data}")
    if data.get("type") == "join":
        await register_client(client_socket, data.get("room_id"), data.get("username"))
        print(f"Client {data.get('username')} joined room {data.get('room_id')}")
    if data.get("type") == "quit":
        await unregister_client(client_socket)
    if data.get("type") == "message":
        await send_message(data.get("message"), client_socket)


async def handle_client_connection(client_socket: websockets.WebSocketServerProtocol):
    message = await client_socket.recv()
    print(f"Client {client_socket.remote_address} connected!")
    print(f"Received message: {message}")

    data = json.loads(message)
    print(f"Data: {data}")

    await register_client(client_socket, data.get("room_id"), data.get("username"))
    print(f"Client {data.get('username')} joined room {data.get('room_id')}")

    while client_socket.open:
        new_message = await client_socket.recv()
        print(f"Received message: {new_message}")
        await process_message(new_message, client_socket)
        if json.loads(new_message).get("type") == "quit":
            print(f"Client TEST disconnected!")
            print("Status:", client_socket.open)


async def start_server():
    await websockets.serve(handle_client_connection, host="0.0.0.0", port=8001)
    print("Websocket Server Started!")
    await asyncio.Future()

#
# if __name__ == "__main__":
#     asyncio.run(start_server())
