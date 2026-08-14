import asyncio
import os
import websockets
import json

# API Token ከ Render Environment Variable ይወሰዳል
API_TOKEN = os.environ.get("DERIV_API_TOKEN")
APP_ID = "1089"  # Default Deriv App ID

async def run_bot():
    if not API_TOKEN:
        print("ስህተት፡ DERIV_API_TOKEN አልተገኘም! እባክህ Render ላይ ሞላው።")
        return

    url = f"wss://ws.derivws.com/websockets/v3?app_id={APP_ID}"
    
    async with websockets.connect(url) as websocket:
        print("ወደ Deriv WebSocket በሰላም ተገናኝቷል...")
        
        # 1. አካውንቱን Authenticate ማድረግ
        auth_req = json.dumps({"authorize": API_TOKEN})
        await websocket.send(auth_req)
        auth_res = await websocket.recv()
        print(f"Auth Response: {auth_res}")
        
        # 2. የትሬዲንግ ሎጂክ እዚህ ይሄዳል (ለምሳሌ Volatility 10 Index ሰብስክራይብ ማድረግ)
        ticks_req = json.dumps({"ticks": "R_10"})
        await websocket.send(ticks_req)
        
        while True:
            response = await websocket.recv()
            print(f"Tick Data: {response}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(run_bot())
