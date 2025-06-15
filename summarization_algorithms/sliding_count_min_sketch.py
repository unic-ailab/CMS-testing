import numpy as np
import hashlib
from summarization_algorithms.count_min_sketch_base import CountMinSketchBase


class SlidingCountMinSketch(CountMinSketchBase):
    def __init__(self, width, depth):
        super().__init__(width, depth)
        self.total_slots = width * depth  # m
        self.window_size = self.total_slots  # N
        self.mN = 1  # how many buckets scanned per arrival
        self.counters = np.zeros((depth, width, 2), dtype=int)  # Two fields per counter: A[i][0] and A[i][1]
        self.scan_pointer = 0  # flat index in total_slots

    def _hash(self, item, i):
        """
        Return the i-th hash value for an item using SHA-256.
        """
        h = hashlib.sha256((str(item) + str(i)).encode('utf-8'))
        return int(h.hexdigest(), 16) % self.width

    def _scan_step(self):
        """
        Perform a scan step over the sliding window:
        - Copy current counter (A[i][0]) to backup (A[i][1]).
        - Reset current counter to 0.
        - Advance scan pointer.
        """
        for _ in range(self.mN):
            d = self.scan_pointer // self.width
            w = self.scan_pointer % self.width

            # Scanning operation:
            # - delete A[i][1] (just reset it)
            # - copy A[i][0] to A[i][1]
            # - set A[i][0] to 0

            self.counters[d][w][1] = self.counters[d][w][0]
            self.counters[d][w][0] = 0

            self.scan_pointer = (self.scan_pointer + 1) % self.total_slots

    def add(self, item, count=1):
        """
        Add an item (possibly multiple times) to the sketch.
        Advances the scan pointer before each insertion to maintain window.
        """
        for _ in range(count):
            # Advance scan pointer before updating
            self._scan_step()
            for i in range(self.depth):
                pos = self._hash(item, i)
                self.counters[i][pos][0] += 1
            self.totalCount += 1

    def query(self, item):
        """
        Query the estimated frequency of an item over the current window.
        Combines both active and backup counters.
        """
        est = float('inf')
        for i in range(self.depth):
            pos = self._hash(item, i)
            val = self.counters[i][pos][0] + self.counters[i][pos][1]
            est = min(est, val)
        return est

    def reset(self):
        """Reset the sketch to an empty state."""
        self.counters.fill(0)
        self.scan_pointer = 0
        self.totalCount = 0

    def get_load_factor(self):
        """
        Return the load factor: maximum number of non-zero counters in any row, divided by width.
        """
        max_nonzero = 0
        for d in range(self.depth):
            row = self.counters[d]
            nonzero_count = sum(1 for cell in row if cell.any())
            max_nonzero = max(max_nonzero, nonzero_count)
        return max_nonzero / self.width
