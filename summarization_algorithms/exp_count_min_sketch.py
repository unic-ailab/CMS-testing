import hashlib
from summarization_algorithms.count_min_sketch_base import CountMinSketchBase


class Bucket:
    def __init__(self, exponent=-1, start=-1, end=-1):
        self.exponent = exponent
        self.start = start
        self.end = end


class Counter:
    def __init__(self):
        self.bucket = [Bucket() for _ in range(100)]
        self.number = -1


class ExpCountMinSketch(CountMinSketchBase):
    def __init__(self, width, depth, window_size=1, counter_size=4):
        super().__init__(width, depth)
        self.window_size = window_size
        self.counter_size = counter_size
        self.counter = [[Counter() for _ in range(self.width)] for _ in range(self.depth)]
        self.mem_acc = 0
        self.MAX_CNT = (1 << counter_size) - 1

    def _hash(self, x):
        """
        Generate multiple hash values for a given input item using SHA-256
        """
        base = str(x)
        for i in range(self.depth):
            h = hashlib.sha256((base + str(i)).encode('utf-8'))
            yield int(h.hexdigest(), 16) % self.width

    def _expire_bucket(self, i, j, t):
        z = self.counter[i][j].number - 1
        if z >= -1:
            for q in range(z, -1, -1):
                if self.counter[i][j].bucket[q].end <= (t - self.window_size):
                    self.counter[i][j].bucket[q] = Bucket()
                    self.counter[i][j].number -= 1
                else:
                    break

    def _insert_bucket(self, i, j, t):
        c = self.counter[i][j]
        z = c.number

        if z == -1:
            c.bucket[0] = Bucket(0, t, t)
            c.number = 1
            return

        p = -1
        value = 0
        first = 0

        while True:
            if p + 2 >= 100 or c.bucket[p + 2].exponent != value:
                # Insert a new bucket of exponent 0
                for q in range(z + 1, 0, -1):
                    c.bucket[q] = c.bucket[q - 1]
                c.bucket[0] = Bucket(0, c.bucket[1].end if z >= 0 else t, t)
                c.number += 1
                break
            else:
                # Merge two buckets
                if p == -1:
                    c.bucket[p + 2].exponent += 1
                    c.bucket[p + 2].end = c.bucket[p + 1].end
                    c.bucket[p + 1].start = c.bucket[p + 2].end
                    c.bucket[p + 1].end = t
                    for q in range(p + 1, first, -1):
                        c.bucket[q] = c.bucket[q - 1]
                    first += 1
                    c.number -= 1
                    p += 2
                    value = c.bucket[p].exponent
                else:
                    c.bucket[p + 2].exponent += 1
                    c.bucket[p + 2].end = c.bucket[p].end
                    c.bucket[p].start = c.bucket[p + 2].end
                    c.bucket[p].end = t
                    for q in range(p, first, -1):
                        c.bucket[q] = c.bucket[q - 1]
                    first += 1
                    c.number -= 1
                    p += 2
                    value = c.bucket[p].exponent

        # Final shift of active bucket window
        if first != 0:
            new_bucket = [c.bucket[q] for q in range(first, first + c.number)]
            new_bucket += [Bucket() for _ in range(100 - len(new_bucket))]
            c.bucket = new_bucket

    def add(self, item, count=1):
        """
        Add item with optional count (must be 1 for this sketch).
        Uses current time as the timestamp.
        """
        if count != 1:
            raise NotImplementedError("ECMSketch only supports count=1 per add.")
        t = self.totalCount
        for i, j in enumerate(self._hash(item)):
            self._expire_bucket(i, j, t)
            self._insert_bucket(i, j, t)
            self.mem_acc += 1
        self.totalCount += count

    def _bucket_sum(self, i, j, t):
        c = self.counter[i][j]
        if c.number == -1:
            return 0
        count = 0
        for q in range(c.number - 1):
            count += 2 ** c.bucket[q].exponent
        count += (2 ** c.bucket[c.number - 1].exponent) // 2
        return count

    def query(self, item, t=None):
        if t is None:
            t = self.totalCount
        min_val = self.MAX_CNT
        for i, j in enumerate(self._hash(item)):
            self._expire_bucket(i, j, t)
            temp = self._bucket_sum(i, j, t)
            min_val = min(min_val, temp)
        return min_val

    def reset(self):
        self.counter = [[Counter() for _ in range(self.width)] for _ in range(self.depth)]
        self.totalCount = 0
        self.mem_acc = 0

    def get_load_factor(self):
        """
        Return the maximum number of non-zero counters in any row divided by width.
        """
        max_nonzero = 0
        for row in self.counter:
            row_nonzero = sum(1 for c in row if c.number > 0)
            max_nonzero = max(max_nonzero, row_nonzero)
        return max_nonzero / self.width if self.width else 0
