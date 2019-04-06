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

                loading_path = os.path.join(self.loadingDirectory, filename)

                try:
                    os.rename(os.path.join(self.inputDirectory, filename), loading_path)
                    with open(loading_path, "rb") as file:
                        message = file.read()

                    processing_path = os.path.join(self.processingDirectory, filename)
                    os.rename(loading_path, processing_path)
                    # TODO: what if rename was successfully but could not put into queue? => rename back? maybe copy and delete instead?
                    self.decoderQueue.put(InputMessage(filename, processing_path, message))
                except:
                    # Unable to read a file or to move a file: reload the file list
                    break
            
            # TODO: reinsert all files of the loading directory into the init directory

            time.sleep(0.01)

    def finish(self):
        self.active = False
