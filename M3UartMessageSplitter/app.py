import os
import signal
import sys
import time

import queue
import argparse

from uartreceiver import UartReceiverThread
from fspersister import FsMessagePersisterThread

running_threads = []

def sigint_handler(sig, frame):
    print("Received SIGINT.")

    print("Sending signals to threads.")
    for thread in running_threads:
        if thread.is_alive():
            thread.finish()

    for thread in running_threads:
        print("Waiting for [" + thread.name + "]", end='', flush=True)

        if not thread.is_alive():
            print(". Already down.")
            continue

        for _ in range(3):
            thread.join(1)
            if not thread.is_alive():
                break
            print(".", end='', flush=True)

        if thread.is_alive():
            print(" Thread is still hanging. Ignoring.")
        else:
            print(".")

    print("Terminating.")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, sigint_handler)

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--serialDevice", type=str, default="/dev/serial0", help="Serial device. Default is /dev/serial0")
    parser.add_argument("-r", "--baudRate", type=int, default=9600, help="UART Baud Rate, Default is 9600")
    parser.add_argument("-b", "--bytesPerRead", type=int, default=8, help="Num of bytes read per serial call. Default is 8")
    parser.add_argument("outputDirectory", type=str, help="Directory where the received m3.msg-files should be stored.")
    args = parser.parse_args()

    if not os.path.exists(args.outputDirectory):
        os.makedirs(args.outputDirectory)

    uartQueue = queue.Queue()
    uart = UartReceiverThread(
        serialDevice=args.serialDevice,
        baudRate=args.baudRate,
        readSize=args.bytesPerRead,
        readTmo=1,
        outputQueue=uartQueue)

    persister = FsMessagePersisterThread(
        targetDirectory=args.outputDirectory,
        inputQueue=uartQueue)

    for thread in [uart, persister]:
        thread.start()
        running_threads.append(thread)

    for byte in bytes('M3v1TESTTESTTEST;M3v1TESTTESTTEST;M3v1TESTTESTTEST;M3v1TESTTESTTEST;M3v1TESTTESTTEST;', 'UTF-8'):
        uartQueue.put(byte)

    while True:
        time.sleep(100)
