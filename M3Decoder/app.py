import signal
import sys
import time
import queue
import argparse

from broker import MessageBrokerThread
from decoder import MessageDecoderThread
from discovery import DiscoveryMessageProcessorThread
from client import ClientDataMessageProcessingThread

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
    parser.add_argument("-ct", "--numClientThreads", type=int, default=3, help="Number of client handler threads. Default is 3")
    parser.add_argument("-dt", "--numDecoderThreads", type=int, default=3, help="Number of decoder threads, Default is 3")
    parser.add_argument("messageInputDirectory", type=str, help="Directory where m3.msg-files are read from.")
    parser.add_argument("loadingDirectory", type=str, help="Directory currently loaded files should be stored.")
    parser.add_argument("processingDirectory", type=str, help="Directory currently processed files should be stored.")
    parser.add_argument("masterApiUrl", type=str, help="URL to the M3 master data rest interface")
    args = parser.parse_args()

    decoderQueue = queue.Queue(maxsize=args.numDecoderThreads)
    discoveryQueue = queue.Queue()
    clientQueues = []

    broker = MessageBrokerThread(inputDirectory=args.messageInputDirectory, loadingDirectory=args.loadingDirectory, processingDirectory=args.processingDirectory, decoderQueue=decoderQueue)
    decoders = [MessageDecoderThread(inputQueue=decoderQueue, discoveryQueue=discoveryQueue, clientQueues=clientQueues)  for x in range(0, args.numDecoderThreads) ]
    discovery = DiscoveryMessageProcessorThread(inputQueue=discoveryQueue, sensorApiUrl=args.masterApiUrl)
    clients = [ClientDataMessageProcessingThread(inputQueues=clientQueues, sensorApiUrl=args.masterApiUrl) for x in range(0, args.numClientThreads) ]

    all_threads = []
    all_threads.extend(decoders)
    all_threads.extend(clients)
    all_threads.append(broker)
    all_threads.append(discovery)

    for thread in all_threads:
        thread.start()
        running_threads.append(thread)

    while True:
        time.sleep(100)
