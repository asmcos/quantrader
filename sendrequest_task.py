import websocket 
import json

req_task_content = {
    'type':'requests',
    'url':'https://www.google.com',
    'headers' : {'Host':'www.google.com',
                'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
                'Referer': 'https://www.google.com',
            },
    'Bridge':'wss://bridge.duozhutuan.com',
    'clientId':''
}


def handle_task(taskcontent,response):
    server="ws://localhost:8081/"
    def on_message(ws, message):
        
        message = json.loads(message)
        response['data'] = message['response']['data']
        response['status'] = message['response']['status']
        response['headers'] = message['response']['headers']
        if (message['type']=='response'):
            print(len(response['data']))
            ws.close()
    def on_open(ws):
        print("connect ok,send a new task")
        print(taskcontent)
        ws.send(json.dumps(taskcontent))

    ws = websocket.WebSocketApp(server,
                                on_open=on_open,
                                on_message=on_message
                                )

    ws.run_forever()


if __name__ == "__main__":
    response = {}
    handle_task(req_task_content,response)
    print(len(response['data']),response['status'])
