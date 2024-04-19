import threading
import time

class Minority_Ants():
    def __init__(self, G):
        self.G = G
        self.thread = threading.Thread(target=self.run)
        self.stop_event = threading.Event()

    def start(self):
        self.thread.start()

    def stop(self):
        self.stop_event.set()

    def run(self):
        while not self.stop_event.is_set():
            # print(self.G)
            time.sleep(2)