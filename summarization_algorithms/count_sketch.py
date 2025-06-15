from summarization_algorithms.count_min_sketch_base import CountMinSketchBase
import numpy as np
import hashlib
import random


class CountSketch(CountMinSketchBase):
    """
    Fast-AGMS / Count Sketch implementation.
    This sketch provides unbiased frequency estimation.
    """
    def __init__(self, width, depth):
        super().__init__(width, depth)
        self.counters = np.zeros((self.depth, self.width), dtype=int)

    def _hash_index(self, x):
        """
        Generate multiple hash values for a given input item using SHA-256
        """
        base = str(x)
        for i in range(self.depth):
            h = hashlib.sha256((base + str(i)).encode('utf-8'))
            yield int(h.hexdigest(), 16) % self.width

    def _hash_sign(self, x):
        base = str(x)
        for i in range(self.depth):
            h = hashlib.sha256((base + "_sign" + str(i)).encode('utf-8'))
            yield 1 if int(h.hexdigest(), 16) % 2 == 0 else -1

    def add(self, item, count=1):
        self.totalCount += abs(count)
        for row, idx, sign in zip(self.counters, self._hash_index(item), self._hash_sign(item)):
            row[idx] += sign * count

    def query(self, item):
        estimates = []
        for row, idx, sign in zip(self.counters, self._hash_index(item), self._hash_sign(item)):
            estimates.append(sign * row[idx])
        return int(np.median(estimates))

    def reset(self):
        self.totalCount = 0
        self.counters.fill(0)

    def get_load_factor(self):
        return max(np.count_nonzero(row) for row in self.counters) / self.width
