import signal
import sys
import time

import queue

from uartreceiver import UartReceiverThread
from fspersister import FsMessagePersisterThread

uartQueue = queue.Queue()

uart = UartReceiverThread(
    serialDevice='/dev/serial0',
    baudRate=9600,
    readSize=8,
    readTmo=1,
    outputQueue=uartQueue)

persister = FsMessagePersisterThread(
    targetDirectory='../messages',
    inputQueue=uartQueue)

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

    for thread in [uart, persister]:
        thread.start()
        running_threads.append(thread)

    while True:
        time.sleep(100)
