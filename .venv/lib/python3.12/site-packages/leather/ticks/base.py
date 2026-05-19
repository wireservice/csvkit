class Ticker:
    """
    Base class for ticker implementations.
    """
    @property
    def ticks(self):
        raise NotImplementedError

    @property
    def min(self):
        raise NotImplementedError

    @property
    def max(self):
        raise NotImplementedError
