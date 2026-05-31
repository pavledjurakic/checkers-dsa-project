class Node:
    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None


class Deque:

    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def push_front(self, data):
        node = Node(data)
        if self.head is None:
            self.head = node
            self.tail = node
        else:
            node.next = self.head
            self.head.prev = node
            self.head = node
        self.size += 1

    def push_rear(self, data):
        node = Node(data)
        if self.tail is None:
            self.head = node
            self.tail = node
        else:
            node.prev = self.tail
            self.tail.next = node
            self.tail = node
        self.size += 1

    def pop_front(self):
        if self.head is None:
            return None
        data = self.head.data
        self.head = self.head.next
        if self.head is not None:
            self.head.prev = None
        else:
            self.tail = None
        self.size -= 1
        return data

    def pop_rear(self):
        if self.tail is None:
            return None
        data = self.tail.data
        self.tail = self.tail.prev
        if self.tail is not None:
            self.tail.next = None
        else:
            self.head = None
        self.size -= 1
        return data

    def peek_front(self):
        return self.head.data if self.head else None

    def peek_rear(self):
        return self.tail.data if self.tail else None

    def __len__(self):
        return self.size

    def __bool__(self):
        return self.size > 0
