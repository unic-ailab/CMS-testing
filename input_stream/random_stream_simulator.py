import time
import numpy as np
from input_stream.stream_simulator_base import StreamSimulator


class RandomStreamSimulator(StreamSimulator):
    """
    Simulates a simple data stream by generating items at a controlled rate.
    """
    def __init__(self, sleep_time=0.00001, stream_size=500000, zipf_param=1.3):
        super().__init__(sleep_time)
        self.stream_size = stream_size
        self.zipf_param = zipf_param

    def simulate_stream(self):
        """
        Simulate a real-time data stream by yielding one item at a time.
        Yields:
            One item at a time from the generated stream.
        """
        data_stream = np.random.zipf(a=self.zipf_param, size=self.stream_size).tolist()
        for item in data_stream:
            yield item
            time.sleep(self.sleep_time)
