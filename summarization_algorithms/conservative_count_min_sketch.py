"""
conservative_count_min_sketch.py
Conservative update Count-Min Sketch implementation.
"""
from summarization_algorithms.count_min_sketch_base import CountMinSketchBase
import numpy as np
import hashlib


class ConservativeCountMinSketch(CountMinSketchBase):
    """
    Conservative Count-Min Sketch implementation.
    """
    def __init__(self, width, depth):
        """
        Initialize sketch with width and depth.
        """
        super().__init__(width, depth)
        self.counters = np.zeros((self.depth, self.width), dtype=int)

    def _hash(self, x):
        """
        Generate multiple hash values for a given input item using SHA-256
        """
        base = str(x)
        for i in range(self.depth):
            h = hashlib.sha256((base + str(i)).encode('utf-8'))
            yield int(h.hexdigest(), 16) % self.width

    def add(self, item, count=1):
        """
        Add the item with frequency `count` using conservative update.
        Only increment positions that hold the current minimum estimate.
        """
        indices = list(self._hash(item))
        current_vals = [self.counters[i][idx] for i, idx in enumerate(indices)]
        current_min = min(current_vals)

        for i, idx in enumerate(indices):
            self.counters[i][idx] = max(self.counters[i][idx], current_min + count)

        self.totalCount += count

    def query(self, item):
        """
        Return an estimation of the amount of times `item` has ocurred.
        The returned value always overestimates the real value.
        """
        return min(table[i] for table, i in zip(self.counters, self._hash(item)))

    def reset(self):
        """
        Reset the sketch by clearing all tables and setting the count to 0.
        """
        self.totalCount = 0
        self.counters.fill(0)

    def get_load_factor(self):
        """
        Return the load factor: maximum number of non-zero counters in any row, divided by width.
        """
        return max(sum(1 for cell in row if cell > 0) for row in self.counters) / self.width
