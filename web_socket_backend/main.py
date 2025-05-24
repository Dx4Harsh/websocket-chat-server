#!/usr/bin/env python

import asyncio
import json
import logging
import os
import platform
import signal
import sys

import websockets
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Setup logging
logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)

# Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8765"))

# Store connected clients and their usernames
CONNECTIONS = set()
USERS = {}  # Maps WebSocket connection to username


async def notify_all(message):
    """Broadcast a message to all connected clients."""
    if CONNECTIONS:
        await asyncio.gather(
            *[connection.send(json.dumps(message)) for connection in CONNECTIONS]
        )


async def handle_join(websocket, username):
    """Handle a new user joining the chat."""
    USERS[websocket] = username
    join_message = {
        "type": "join",
        "username": username,
        "users": list(USERS.values()),
    }
    await notify_all(join_message)
    logging.info(f"User {username} joined the chat")


async def handle_leave(websocket):
    """Handle a user leaving the chat."""
    if websocket in USERS:
        username = USERS[websocket]
        del USERS[websocket]
        leave_message = {
            "type": "leave",
            "username": username,
            "users": list(USERS.values()),
        }
        await notify_all(leave_message)
        logging.info(f"User {username} left the chat")


async def handle_message(websocket, message_data):
    """Handle a chat message."""
    if websocket not in USERS:
        return
    
    username = USERS[websocket]
    message = {
        "type": "message",
        "username": username,
        "message": message_data["message"],
        "timestamp": message_data.get("timestamp", ""),
    }
    await notify_all(message)
    logging.info(f"Message from {username}: {message_data['message']}")


async def chat_server(websocket):
    """Handle a connection to the chat server."""
    try:
        CONNECTIONS.add(websocket)
        logging.info(f"New connection established")
        
        # Send welcome message
        await websocket.send(json.dumps({
            "type": "system",
            "message": "Connected to chat server",
        }))
        
        # Process messages
        async for message in websocket:
            try:
                data = json.loads(message)
                message_type = data.get("type")
                
                if message_type == "join":
                    await handle_join(websocket, data["username"])
                elif message_type == "message":
                    await handle_message(websocket, data)
                else:
                    logging.warning(f"Unknown message type: {message_type}")
            except json.JSONDecodeError:
                logging.error(f"Invalid JSON received: {message}")
                
    except websockets.exceptions.ConnectionClosed as e:
        logging.info(f"Connection closed: {e}")
    finally:
        CONNECTIONS.remove(websocket)
        await handle_leave(websocket)


async def windows_main():
    """Start the WebSocket server for Windows platforms."""
    # Create the server
    server = await websockets.serve(chat_server, HOST, PORT)
    logging.info(f"Server running on ws://{HOST}:{PORT}")
    logging.info("Press Ctrl+C to stop the server")
    
    # Keep the server running until Ctrl+C is pressed
    try:
        await asyncio.Future()  # Run forever
    except asyncio.CancelledError:
        pass
    finally:
        server.close()
        await server.wait_closed()
        logging.info("Server has been shut down")


async def unix_main():
    """Start the WebSocket server for Unix-like platforms with signal handling."""
    stop = asyncio.Future()
    
    # Handle graceful shutdown
    def handle_signal():
        logging.info("Shutting down...")
        stop.set_result(None)
    
    for sig in (signal.SIGINT, signal.SIGTERM):
        asyncio.get_event_loop().add_signal_handler(sig, handle_signal)
    
    async with websockets.serve(chat_server, HOST, PORT):
        logging.info(f"Server running on ws://{HOST}:{PORT}")
        await stop


if __name__ == "__main__":
    try:
        if platform.system() == "Windows":
            # Use windows-compatible approach
            asyncio.run(windows_main())
        else:
            # Use Unix signal handling approach
            asyncio.run(unix_main())
    except KeyboardInterrupt:
        logging.info("Shutting down due to keyboard interrupt...")
        sys.exit(0) 