import os
import asyncio
import json
import websockets
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Render port requirement workaround
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Deriv Trading Bot is Running!")

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    server.serve_forever()

# Deriv Bot Logic
async def run_bot():
    api_token = os.environ.get("DERIV_API_TOKEN")
    if not api_token:
        print("ስህተት: DERIV_API_TOKEN አልተገኘም!")
        return

    url = "wss://ws.derivws.com/websockets/v3?app_id=1089"

    async with websockets.connect(url) as websocket:
        print("ወደ Deriv WebSocket በሰላም ተገናኝቷል...")

        # Authenticate
        auth_req = json.dumps({"authorize": api_token})
        await websocket.send(auth_req)
        auth_res = await websocket.recv()
        print(f"Auth Response: {auth_res}")

        # Subscribe to Volatility 10 Index Tick Stream
        ticks_req = json.dumps({"ticks": "R_10"})
        await websocket.send(ticks_req)

        while True:
            response = await websocket.recv()
            print(f"Tick Data: {response}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    # Start HTTP server in a background thread for Render health check
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()

    # Run the Deriv Bot
    asyncio.run(run_bot())
