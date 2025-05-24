# WebSocket Chat Server

A simple WebSocket-based chat server built with Python for Flutter clients.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
   Alternatively, install dependencies individually:
   ```bash
   pip install websockets
   pip install python-dotenv
   ```

2. Start the server:
   ```bash
   python server.py
   ```

3. The server will start on `ws://localhost:8765` by default.

## Configuration

You can configure the server using environment variables or a `.env` file:
- `HOST`: Host address (default: 0.0.0.0)
- `PORT`: Port number (default: 8765)

## Platform Compatibility

The server has been updated to work on both Windows and Unix-like systems. It automatically detects your operating system and uses the appropriate implementation for handling server shutdowns.

## Flutter Client

For Flutter clients, use the following connection URLs:
- Android Emulator: `ws://10.0.2.2:8765`
- iOS Simulator: `ws://localhost:8765`
- Web: `ws://localhost:8765`
- Physical devices: `ws://<your_server_ip>:8765`

## Troubleshooting

If you encounter issues:

1. Make sure all dependencies are installed correctly:
   ```bash
   pip install -r requirements.txt
   ```

2. Check that the correct port is available (8765 by default)

3. For Windows users, the server uses a different approach to handle shutdowns since Windows doesn't support the same signal handling mechanisms as Unix-based systems. 