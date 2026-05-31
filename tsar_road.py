import relics as rel
from data_structures.deque import Deque

class TsarRoad:

    def __init__(self):
        self._deque = Deque()
        self._gen = rel.relic_cycle()
        for i in range(5):
            self._deque.push_front(next(self._gen))

    def get_front(self):
        result = self._deque.pop_front()
        self.backfill()
        return result

    def get_rear(self):
        result = self._deque.pop_rear()
        self.backfill()
        return result
    
    def peek_front(self):
        return self._deque.peek_front()
    
    def peek_rear(self):
        return self._deque.peek_rear()

    def backfill(self):
        if self._deque.size < 5:
            self._deque.push_front(next(self._gen))
        elif self._deque.size == 5:
            self._deque.push_front(next(self._gen))
            self._deque.pop_rear()

