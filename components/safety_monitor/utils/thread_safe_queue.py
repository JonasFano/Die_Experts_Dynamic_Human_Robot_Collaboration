import threading
from collections import deque

class ThreadSafeQueue:
    def __init__(self, max_size=10):
        self.queue = deque(maxlen=max_size)
        self.lock = threading.Lock()

    def get(self):
        """Returns the latest element without removing it."""
        with self.lock:
            if self.queue:
                return self.queue[-1]
            return None  # Return None if the queue is empty

    def put(self, element):
        """Adds an element to the queue at the front."""
        with self.lock:
            self.queue.appendleft(element)

    def clear(self):
        """Clears the queue."""
        with self.lock:
            self.queue.clear() 
    def all(self):
        return list(self.queue)
