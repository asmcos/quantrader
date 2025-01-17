import sys
TaskQ5_ROOT= "/home/jsh/TaskQ5-py"
sys.path.insert(0,TaskQ5_ROOT)
from TaskQ5.do_requests import send_request
from nostrclient.log import log 
import json
import threading

condition = threading.Condition()

def handle_task(request,response):
    def finish_task(data):
        nonlocal response
        res = json.loads(data["content"])
        response['data']          = res['data']
        response['status']        = res['status']
        response['headers']       = res['headers']
        with condition:
            condition.notify() 
        
    send_request(request,finish_task)
    with condition:
        ret = condition.wait(timeout=20) 
        if ret:
            return True
    log.red("Timeout")
    print(request)
    return False
