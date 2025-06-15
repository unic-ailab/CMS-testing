import csv
import os
import time
from input_stream.stream_simulator_base import StreamSimulator


class DatasetStreamSimulator(StreamSimulator):
    """
    Simulates a real-time data stream from a CSV dataset.
    """
    def __init__(self, dataset_path, field_name, sleep_time=0.01):
        super().__init__(sleep_time)
        self.dataset_path = dataset_path
        self.field_name = field_name
        self.file_ext = os.path.splitext(dataset_path)[1].lower()

    def simulate_stream(self):
        if self.file_ext == ".csv":
            return self._stream_from_csv()
        elif self.file_ext == ".txt":
            return self._stream_from_txt()
        else:
            raise ValueError(f"Unsupported file type: {self.file_ext}")

    def _stream_from_csv(self):
        with open(self.dataset_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            if not self.field_name:
                raise ValueError("field_name must be specified for CSV files.")
            for row in reader:
                data = row.get(self.field_name)
                if data:
                    for word in data.split():
                        yield word
                        time.sleep(self.sleep_time)

    def _stream_from_txt(self):
        with open(self.dataset_path, "r", encoding="utf-8") as file:
            for line in file:
                tokens = line.strip().split()
                for token in tokens:
                    yield token
                    time.sleep(self.sleep_time)
