from collections import deque
from ground_truth.base_truth import BaseTruth


class DecayingTruth(BaseTruth):
    def __init__(self, window_size=10000):
        self.window_size = window_size
        self.data = deque()  # list of items
        self.counts = {}
        self.window_item_count = 0

    def add(self, item):
        self.data.append(item)
        self.counts[item] = self.counts.get(item, 0) + 1
        self.window_item_count += 1

        if len(self.data) > self.window_size:
            old_item = self.data.popleft()
            self.counts[old_item] -= 1
            self.window_item_count -= 1
            if self.counts[old_item] == 0:
                del self.counts[old_item]

    def query(self, item):
        return self.counts.get(item, 0)

    def get_top_k(self, k):
        return sorted(self.counts.items(), key=lambda x: -x[1])[:k]

    def get_all(self):
        return dict(self.counts)
