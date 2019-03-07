from threading import Thread
import queue
import time
import serial
        
class UartReceiverThread(Thread):
    def __init__(self, serialDevice, baudRate, readSize, readTmo, outputQueue):
        Thread.__init__(self)
        self.daemon = True
        self.active = True
        self.name = "uart receiver thread"
        self.serialDevice = serialDevice
        self.baudRate = baudRate
        self.readTmo = readTmo
        self.baudRate = baudRate
        self.readSize = readSize
        self.outputQueue = outputQueue
        self.serial = None

    def run(self):
        while self.active:
            if self.lost_connection():
                self.reconnect()
            else:
                bytesRead = self.serial.read(self.readSize)
                print("read=", str(bytesRead), ", type=", type(bytesRead))
                for byte in bytesRead:
                    self.outputQueue.put(byte)

            time.sleep(0.01)
    
    def lost_connection(self):
        return self.serial is None

    def reconnect(self):
        try:
            self.serial = serial.Serial(self.serialDevice, self.baudRate, timeout=self.readTmo)
        except serial.SerialException:
            if self.serial is not None:
                self.serial.close()
            self.serial = None
            pass

    def finish(self):
        self.active = False
