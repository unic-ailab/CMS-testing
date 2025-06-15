from ground_truth.base_truth import BaseTruth


class Truth(BaseTruth):
    def __init__(self):
        self.counts = {}

    def add(self, item):
        self.counts[item] = self.counts.get(item, 0) + 1

    def query(self, item):
        return self.counts.get(item, 0)

    def get_all(self):
        return dict(self.counts)
