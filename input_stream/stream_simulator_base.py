import abc


class StreamSimulator(abc.ABC):
    """
    Abstract base class for simulating data streams.
    """
    def __init__(self, sleep_time=0.01):
        """
        Initialize the stream simulator.

        Args:
            sleep_time: Time delay between yielding each item.
        """
        self.sleep_time = sleep_time

    @abc.abstractmethod
    def simulate_stream(self):
        """
        Abstract method to simulate a real-time data stream.
        Should yield one item at a time.
        """
        pass
