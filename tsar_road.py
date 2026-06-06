import relics as rel
from data_structures.deque import Deque

class TsarRoad:

    def __init__(self):
        self._deque = Deque()
        self._relic_list = [rel.RelicType.TOKA_OD_CELIKA, rel.RelicType.MESINA_RUJNOG_VINA, rel.RelicType.TOPUZ, rel.RelicType.SARAC, rel.RelicType.TRI_TOVARA_BLAGA]
        rel.random.shuffle(self._relic_list)
        self._index = 0
        for i in range(5):
            self._deque.push_front(self._next_relic())

    def _next_relic(self):
        relic = self._relic_list[self._index % len(self._relic_list)]
        self._index += 1
        return relic

    def get_front(self):
        return self._deque.pop_front()

    def get_rear(self):
        return self._deque.pop_rear()
    
    def peek_front(self):
        return self._deque.peek_front()
    
    def peek_rear(self):
        return self._deque.peek_rear()

    def backfill(self):
        if self._deque.size < 5:
            self._deque.push_front(self._next_relic())
        elif self._deque.size == 5:
            self._deque.push_front(self._next_relic())
            self._deque.pop_rear()

