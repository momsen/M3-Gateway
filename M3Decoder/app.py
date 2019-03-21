import signal
import sys
import time
import queue

from broker import MessageBrokerThread
from discovery import DiscoveryMessageProcessorThread
from client import ClientDataMessageProcessingThread
from decoder import MessageDecoderThread

decoderQueue = queue.Queue()
discoveryQueue = queue.Queue()
clientQueues = []

broker = MessageBrokerThread()
decoders = [MessageDecoderThread()  for x in range(0, 3) ]
discovery = DiscoveryMessageProcessorThread()
clients = [ClientDataMessageProcessingThread()  for x in range(0, 3) ]

all_threads = []
all_threads.extend(decoders)
all_threads.extend(clients)
all_threads.append(broker)
all_threads.append(discovery)

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

    for thread in all_threads:
        thread.start()
        running_threads.append(thread)

    while True:
        time.sleep(100)
