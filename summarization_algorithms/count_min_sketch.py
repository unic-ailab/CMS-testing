"""
count_min_sketch.py
Regular Count-Min Sketch implementation.
"""
from summarization_algorithms.count_min_sketch_base import CountMinSketchBase
import numpy as np
import hashlib


class CountMinSketch(CountMinSketchBase):
    """
    Regular Count-Min Sketch implementation.
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
        Add the element 'item' as if it had appeared 'count' times
        """
        self.totalCount += count
        for table, i in zip(self.counters, self._hash(item)):
            table[i] += count

    def query(self, item):
        """
        Return an estimation of the amount of times `item` has occurred.
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


if __name__ == '__main__':
    from ground_truth.truth import Truth
    cms = CountMinSketch(width=10, depth=4)
    truth = Truth()
    for item in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]:
        print(f"----------------------------------")

        print(f"Being inserted: {item}")
        cms.add(item)
        truth.add(item)
        print(cms.counters)

        print(f"Being queried: {item}")
        print(f"CMS: {cms.query(item)}")
        print(f"Truth: {truth.query(item)}")

