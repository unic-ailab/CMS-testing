"""
count_min_sketch_base.py
Count-Min Sketch Base Class.

This file contains the abstract base class for Count-Min Sketch (CMS) implementations.

Subclasses must implement the `add`, `query`, and `reset` methods.
Subclasses may implement the`__init__` method if additional parameters are needed.
"""
import abc


class CountMinSketchBase(abc.ABC):
    """
    Abstract base class for Count-Min Sketch implementations.
    Defines the core structure and methods of Count-Min Sketches.
    """
    def __init__(self, width, depth, *args, **kwargs):
        """
        Initialize sketch with width, depth, and seed.
        Subclasses may require additional parameters.
        """
        self.width = width
        self.depth = depth
        self.totalCount = 0

        pass  # Allow subclasses to handle additional parameters as necessary

    @abc.abstractmethod
    def add(self, item, count=1):
        """
        Add an item to the sketch.
        """
        pass

    @abc.abstractmethod
    def query(self, item):
        """
        Query the count of an item.
        """
        pass

    @abc.abstractmethod
    def reset(self):
        """
        Reset the sketch.
        """
        pass

    @abc.abstractmethod
    def get_load_factor(self):
        """
        Return the load factor: maximum number of non-zero counters in any row, divided by width.
        """
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(width={self.width}, depth={self.depth})"

    def __getitem__(self, x):
        """
        A convenience method to call `query`.
        """
        return self.query(x)

    def __len__(self):
        """
        Return number of distinct items counted.
        """
        return self.totalCount
