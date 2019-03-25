from threading import Thread
import queue
import time

class InputMessage:
    def __init__(self, filename, path, content):
        self.filename = filename
        self.path = path
        self.content = content

class MessageDecoderThread(Thread):
    def __init__(self, inputQueue, discoveryQueue, clientQueues):
        Thread.__init__(self)
        self.daemon = True
        self.active = True
        self.name = "message decoder"
        self.inputQueue = inputQueue
        self.discoveryQueue = discoveryQueue
        self.clientQueues = clientQueues

    def run(self):
        while self.active:
            try:
                message = self.inputQueue.get_nowait()
            except queue.Empty:
                time.sleep(0.01)
                continue
            
            print(message.content)

    def finish(self):
        self.active = False
