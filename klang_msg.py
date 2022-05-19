#!/usr/bin/env python

import asyncio
import websockets
import json

uri = "wss://klang.org.cn:8099/user"

async def msg():

    reset_stock = json.dumps({"type": 'U_CMD',"content":"UPDATEALL","pw":"Klang"})
    async with websockets.connect(uri) as websocket:
        
        await websocket.send(reset_stock)
        await websocket.recv()

asyncio.get_event_loop().run_until_complete(msg())
