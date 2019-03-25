from threading import Thread
import queue
import time
import os

M3MSG_SUFFIX = ".m3.msg"

# TODO: split only if ; indicates really end of message.


class FsMessagePersisterThread(Thread):

    def __init__(self, targetDirectory, inputQueue):
        Thread.__init__(self)
        self.daemon = True
        self.active = True
        self.name = "fs persister thread"
        self.targetDirectory = targetDirectory
        self.inputQueue = inputQueue
        self.latestMessageBuffer = bytearray()
        self.hasFoundStart = False
        self.latestMessageIndex = 0

    def run(self):
        while self.active:
            try:
                byte = self.inputQueue.get_nowait()
            except queue.Empty:
                time.sleep(0.01)
                continue

            self.latestMessageBuffer.append(byte)
            if byte == ord(';'):
                self.interpretMessage()

    def interpretMessage(self):
        try:
            startIndex = self.latestMessageBuffer.index(b'M3v1')
        except ValueError:
            print("Unknown message: ", str(self.latestMessageBuffer))
            self.latestMessageBuffer.clear()
            return

        message = self.latestMessageBuffer[startIndex:]
        print("Found message: ", str(message))
        self.persist(message)
        self.latestMessageBuffer.clear()

    def persist(self, message):
        filepath = self.getNextMessageFilepath()
        try:
            print("Writing file ", str(filepath))
            with open(filepath, "wb") as file:
                file.write(message)
        except EnvironmentError as e:
            print("Unable to persist message (", str(message), ") to ",
                  str(filepath), ": ", str(e))

    def getNextMessageFilepath(self):
        self.latestMessageIndex += 1
        filepath = self.messageIndexToPath()
        if os.path.isfile(filepath):
            highestIndex = 0
            for filename in os.listdir(self.targetDirectory):
                if filename.endswith(M3MSG_SUFFIX):
                    try:
                        num = int(filename[:-len(M3MSG_SUFFIX)])
                        if num > highestIndex:
                            highestIndex = num
                    except ValueError:
                        pass

            self.latestMessageIndex = highestIndex + 1
            filepath = self.messageIndexToPath()
        return filepath

    def messageIndexToPath(self):
        filename = str(self.latestMessageIndex) + M3MSG_SUFFIX
        return os.path.join(self.targetDirectory, filename)

    def finish(self):
        self.active = False
