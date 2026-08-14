import os
import json
import asyncio
import websockets
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# 1. Environment Variables
API_TOKEN = os.environ.get("DERIV_API_TOKEN")
APP_ID = "1089"
PORT = int(os.environ.get("PORT", 10000))

# 2. Dumb HTTP Server for Render Keeping Alive
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Deriv AI Trading Bot is Running!")

def run_http_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"HTTP Server started on port {PORT}")
    httpd.serve_forever()

# 3. AI Smart Trading Logic
class AITrader:
    def __init__(self):
        self.ticks_history = []
        self.trade_memory = [] # ከስህተት መማሪያ (Memory)
        self.consecutive_losses = 0

    def check_market_news(self):
        # ዜና የማዳመጥ ሲሙሌሽን (High Impact News Check)
        # በእውነተኛ ገበያ ዜና ሲኖር True ይመልሳል
        return False

    def simulate_scenario(self, direction):
        # "ይህንን ብል ምን ይፈጠራል?" ብሎ አስቀድሞ ማሰብ (Risk Simulation)
        if len(self.ticks_history) < 5:
            return False
            
        win_probability = 0.5
        # ያለፉትን የ ticks እንቅስቃሴዎችን ያጠናል
        recent_diffs = [self.ticks_history[i] - self.ticks_history[i-1] for i in range(1, len(self.ticks_history))]
        
        if direction == "CALL" and sum(1 for d in recent_diffs if d > 0) >= 3:
            win_probability = 0.75
        elif direction == "PUT" and sum(1 for d in recent_diffs if d < 0) >= 3:
            win_probability = 0.75

        # ከዚህ ቀደም በተመሳሳይ ሁኔታ ተከስሮ ከነበረ እድሉን ይቀንሰዋል (Learning)
        if self.consecutive_losses > 2:
            win_probability -= 0.2

        print(f"🧠 AI Simulation for {direction}: Estimated Win Probability = {win_probability*100}%")
        return win_probability > 0.6

    def learn_from_result(self, is_win):
        # ከስህተት መማር
        if is_win:
            print("🎉 AI: Trade Won! Strategy validated.")
            self.consecutive_losses = 0
        else:
            print("⚠️ AI: Trade Lost. Learning from mistake & adjusting risk...")
            self.consecutive_losses += 1

# Initialize AI
ai_bot = AITrader()

async def connect_deriv():
    uri = f"wss://ws.derivws.com/websockets/v3?app_id={APP_ID}"
    
    async with websockets.connect(uri) as websocket:
        print(" Connected to Deriv WebSocket successfully!")
        
        # Authenticate
        auth_req = {"authorize": API_TOKEN}
        await websocket.send(json.dumps(auth_req))
        auth_res = await websocket.recv()
        print(f"Auth Response: {auth_res}")

        # Subscribe to Ticks
        ticks_req = {"ticks": "R_10"}
        await websocket.send(json.dumps(ticks_req))

        while True:
            response = await websocket.recv()
            data = json.loads(response)

            if "tick" in data:
                tick_price = data["tick"]["quote"]
                ai_bot.ticks_history.append(tick_price)
                if len(ai_bot.ticks_history) > 10:
                    ai_bot.ticks_history.pop(0)

                print(f"📈 Current Price: {tick_price}")

                # 1. ዜና ማዳመጥ
                if ai_bot.check_market_news():
                    print("📰 High impact news detected! Pausing trading for safety.")
                    continue

                # 2. አስቀድሞ ማሰብና መተንበይ (Rise or Fall)
                if ai_bot.simulate_scenario("CALL"):
                    print("🚀 Decision: Placing RISE (Buy) Trade based on AI Analysis!")
                    # Trade መክፈቻ ኮድ እዚህ ጋር ይነሳል
                elif ai_bot.simulate_scenario("PUT"):
                    print("ከ Decision: Placing FALL (Sell) Trade based on AI Analysis!")
                    # Trade መክፈቻ ኮድ እዚህ ጋር ይነሳል

            await asyncio.sleep(1)

if __name__ == "__main__":
    # Start Dummy Web Server
    threading.Thread(target=run_http_server, daemon=True).start()
    
    # Start Deriv AI Bot
    asyncio.run(connect_deriv())
