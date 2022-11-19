#!/usr/bin/env python

import socketio 
import json
import os

uri = "https://klang.org.cn:8099/user"
sio = socketio.Client()

@sio.event
def connect():
    print("connected! ")
    sio.emit("u_cmd_event",{"content":"UPDATEALL"})
    os._exit(0)

sio.connect(uri)

