from threading import Thread
import queue
import time

class ClientDataMessageProcessingThread(Thread):
    def __init__(self, inputQueues, sensorApiUrl):
        Thread.__init__(self)
        self.daemon = True
        self.active = True
        self.name = "client processor"
        pass

    def run(self):
        while self.active:
            pass
            time.sleep(0.01)

    def finish(self):
        self.active = False
