import time
import copy
import threading


def change_valves(request):
    print(request)


def handle_valve(timer, request, target):
    time.sleep(timer)
    request[target] = False
    change_valves(request)


def post(request):
    if not request['cValve1'] and request['cValve1Time'] > 0:
        temp_req = copy.deepcopy(request)
        threading.Thread(target=handle_valve, args=(request['cValve1Time'], temp_req, 'cValve1')).start()
    if not request['cValve2'] and request['cValve2Time'] > 0:
        temp_req = copy.deepcopy(request)
        threading.Thread(target=handle_valve, args=(request['cValve2Time'], temp_req, 'cValve2')).start()
    if not request['fanAir1'] and request['fanAir1Time'] > 0:
        temp_req = copy.deepcopy(request)
        threading.Thread(target=handle_valve, args=(request['fanAir1Time'], temp_req, 'fanAir1')).start()
    if not request['fanAir2'] and request['fanAir2Time'] > 0:
        temp_req = copy.deepcopy(request)
        threading.Thread(target=handle_valve, args=(request['fanAir2Time'], temp_req, 'fanAir2')).start()
    request['cValve1'] = request['cValve1'] or bool(request['cValve1Time'])
    request['cValve2'] = request['cValve2'] or bool(request['cValve2Time'])
    request['fanAir1'] = request['fanAir1'] or bool(request['fanAir1Time'])
    request['fanAir2'] = request['fanAir2'] or bool(request['fanAir2Time'])
    change_valves(request)
    return None

if __name__ == '__main__':
    request = {'cValve1': True,
               'cValve1Time': 1,
               'cValve2': False,
               'cValve2Time': 0,
               'fanAir1': False,
               'fanAir1Time': 5,
               'fanAir2': True,
               'fanAir2Time': 1}
    post(request)