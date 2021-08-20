#!/usr/bin/env python

import asyncio
import websockets
import json

uri = "ws://klang.org.cn:9099"

async def msg():

    reset_stock = json.dumps({"action": 'cmd',"content":"reset_stock","pw":"Klang"})
    async with websockets.connect(uri) as websocket:
        
        await websocket.send(reset_stock)
        await websocket.recv()

asyncio.get_event_loop().run_until_complete(msg())
