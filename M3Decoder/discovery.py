from threading import Thread
import queue
import time
import serial

'''
Discovery messages are sent directly to the web frontend so that the user may select the new node.
'''
class DiscoveryMessageProcessorThread(Thread):
    def __init__(self, inputQueue, sensorApiUrl):
        Thread.__init__(self)
        self.daemon = True
        self.active = True
        self.name = "discovery processor"
        pass

    def run(self):
        while self.active:
            pass
            time.sleep(0.01)

    def finish(self):
        self.active = False
