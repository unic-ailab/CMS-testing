import abc


class BaseTruth(abc.ABC):
    @abc.abstractmethod
    def add(self, item):
        pass

    @abc.abstractmethod
    def get_all(self):
        pass

    @abc.abstractmethod
    def query(self, item):
        pass

    def __getitem__(self, item):
        return self.query(item)
    