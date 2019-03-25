from threading import Thread
import queue
import time
import os
from decoder import InputMessage 

M3MSG_SUFFIX = ".m3.msg"

class MessageBrokerThread(Thread):
    def __init__(self, inputDirectory, loadingDirectory, processingDirectory, decoderQueue):
        Thread.__init__(self)
        self.daemon = True
        self.active = True
        self.name = "message broker"
        self.inputDirectory = inputDirectory
        self.loadingDirectory = loadingDirectory
        self.processingDirectory = processingDirectory
        self.decoderQueue = decoderQueue

    def run(self):
        while self.active:
            for filename in os.listdir(self.inputDirectory):
                if not filename.endswith(M3MSG_SUFFIX):
                    continue

                #try:
                loading_path = os.path.join(self.loadingDirectory, filename)
                os.rename(os.path.join(self.inputDirectory, filename), loading_path)
                with open(loading_path, "rb") as file:
                    message = file.read()

                processing_path = os.path.join(self.processingDirectory, filename)
                os.rename(loading_path, processing_path)
                self.decoderQueue.put(InputMessage(filename, processing_path, message))
                #except:
                #   break

            time.sleep(0.01)

    def finish(self):
        self.active = False
