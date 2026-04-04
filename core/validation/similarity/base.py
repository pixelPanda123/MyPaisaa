class BaseCheck:
    def __init__(self, weight: float):
        self.weight = weight

    def compute(self, data):
        raise NotImplementedError