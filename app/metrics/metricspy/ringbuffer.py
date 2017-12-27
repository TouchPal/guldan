# -*- coding: utf-8 -*-
import logging
import threading

logger = logging.getLogger(__name__)


class RingBuffer(object):
    def __init__(self, name, max_length=1000):
        self.lock = threading.Lock()
        self.name = name
        self.buffer = [None] * max_length
        self._capacity = max_length
        self._size = 0
        self.head = 0
        self.tail = 0

    @property
    def size(self):
        return self._size

    @property
    def capacity(self):
        return self._capacity

    def offer(self, o):
        with self.lock:
            if self._size >= self._capacity:
                logger.error("RingBuffer {} is full".format(self.name))
                return False

            self.buffer[self.tail] = o
            if self.tail + 1 >= self._capacity:
                self.tail = 0
            else:
                self.tail += 1

            self._size += 1
            return True

    def pop(self):
        with self.lock:
            if self._size <= 0:
                return None

            result = self.buffer[self.head]
            self.buffer[self.head] = None
            if self.head + 1 >= self.capacity:
                self.head = 0
            else:
                self.head += 1

            self._size -= 1
            return result
