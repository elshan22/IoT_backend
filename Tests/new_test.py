import time
import threading

def timer1():
    for i in range(10):
        print(f'this is {i}')
        time.sleep(1)

def timer2():
    for i in range(5):
        print(f'this thread is in {i}th step')
        time.sleep(2)

t1 = threading.Thread(target=timer1)
t2 = threading.Thread(target=timer2)
t1.start()
t2.start()