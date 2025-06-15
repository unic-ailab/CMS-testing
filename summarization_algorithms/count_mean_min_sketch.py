"""
count_mean_min_sketch.py
Count-Mean-Min Sketch implementation.
"""
from summarization_algorithms.count_min_sketch_base import CountMinSketchBase
import numpy as np
import hashlib


class CountMeanMinSketch(CountMinSketchBase):
    """
    Implementation of Count-Mean-Min Sketch, a variation of Count-Min Sketch with noise adjustment.
    """
    def __init__(self, width, depth):
        """
        Initialize sketch with given width and depth.
        """
        super().__init__(width, depth)
        self.counters = np.zeros((self.depth, self.width), dtype=int)
        self.totalCount = 0

    def _hash(self, x):
        """
        Generate multiple hash values using SHA-256 with added seed for depth variation.
        """
        base = str(x)
        for i in range(self.depth):
            h = hashlib.sha256((base + str(i)).encode('utf-8'))
            yield int(h.hexdigest(), 16) % self.width

    def add(self, item, count=1):
        """
        Add the element 'item' to the sketch 'count' times.
        """
        self.totalCount += count
        for row, idx in zip(self.counters, self._hash(item)):
            row[idx] += count

    def _estimate_error(self, row_idx, col_idx):
        """
        Estimate the average noise in a particular row (excluding target cell).
        """
        row = self.counters[row_idx]
        target_value = row[col_idx]
        row_sum = np.sum(row)
        noise = (row_sum - target_value) / (self.width - 1) if self.width > 1 else 0
        return noise

    def query(self, item):
        """
        Return a corrected frequency estimate using the Count-Mean-Min algorithm.
        """
        estimates = []
        raw_values = []

        for i, (row, idx) in enumerate(zip(self.counters, self._hash(item))):
            raw = row[idx]
            noise = self._estimate_error(i, idx)
            estimates.append(raw - noise)
            raw_values.append(raw)

        return max(0, min(np.median(estimates), min(raw_values)))

    def reset(self):
        """
        Reset the sketch to its initial state.
        """
        self.totalCount = 0
        self.counters.fill(0)

    def get_load_factor(self):
        """
        Return the load factor: maximum number of non-zero counters in any row, divided by width.
        """
        return max(np.count_nonzero(row) for row in self.counters) / self.width
