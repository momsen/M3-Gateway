from threading import Thread
import queue
import time
import serial

class DiscoveryMessageProcessorThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        pass

    def run(self):
        while self.active:
            pass
            time.sleep(0.01)

    def finish(self):
        self.active = False
