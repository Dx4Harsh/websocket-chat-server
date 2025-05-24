#!/usr/bin/env python

import asyncio
import json
import sys
import time
import websockets
import random

# Sample usernames for demo
SAMPLE_USERNAMES = ["Alice", "Bob", "Charlie", "Dave", "Eve", "Frank"]

async def send_message(websocket, message_type, **kwargs):
    """Send a message to the server."""
    message = {"type": message_type, **kwargs}
    await websocket.send(json.dumps(message))

async def receive_messages(websocket):
    """Receive and display messages from the server."""
    try:
        async for message in websocket:
            data = json.loads(message)
            if data["type"] == "message":
                print(f"[{data['username']}]: {data['message']}")
            elif data["type"] == "join":
                print(f"User {data['username']} joined the chat")
                print(f"Active users: {', '.join(data['users'])}")
            elif data["type"] == "leave":
                print(f"User {data['username']} left the chat")
                print(f"Active users: {', '.join(data['users'])}")
            elif data["type"] == "system":
                print(f"System: {data['message']}")
            else:
                print(f"Received: {data}")
    except websockets.exceptions.ConnectionClosed:
        print("Connection to server closed")

async def chat_client():
    """Connect to the chat server and handle user input."""
    # Connect to the WebSocket server
    uri = "ws://localhost:8765"
    
    try:
        async with websockets.connect(uri) as websocket:
            # Start a task to receive messages
            receiver_task = asyncio.create_task(receive_messages(websocket))
            
            # Choose a username
            if len(sys.argv) > 1:
                username = sys.argv[1]
            else:
                username = random.choice(SAMPLE_USERNAMES)
                print(f"Using random username: {username}")
            
            # Join the chat
            await send_message(websocket, "join", username=username)
            
            # Main input loop
            print("Type your messages (Ctrl+C to exit):")
            try:
                while True:
                    message = input("> ")
                    if message.strip():
                        await send_message(
                            websocket, 
                            "message", 
                            message=message,
                            timestamp=time.time()
                        )
            except KeyboardInterrupt:
                print("\nExiting...")
            finally:
                receiver_task.cancel()
    
    except (websockets.exceptions.InvalidStatusCode, 
            websockets.exceptions.InvalidURI,
            ConnectionRefusedError) as e:
        print(f"Error connecting to the server: {e}")
        print("Make sure the server is running at ws://localhost:8765")

if __name__ == "__main__":
    asyncio.run(chat_client()) 