# push(item)   — dodaj na vrh        (ti si koristio append)
# pop()        — ukloni i vrati vrh
# peek()       — vidi vrh bez uklanjanja  
# is_empty()   — da li je prazan
# __len__      — da if self.undo_stack: radi
# __bool__     — isto, za bool proveru

class Stack:

    def __init__(self):
        self._data = []

    def push(self, elem):
        self._data.append(elem)
    
    def pop(self):
        if len(self) == 0:
            return None
        else:
            return self._data.pop(-1)
    
    def peek(self):
        if len(self) == 0:
            return None
        else:
            return self._data[-1]
    
    def is_empty(self):
        return (len(self._data)==0)
    
    def __len__(self):
        return len(self._data)
    
    def __bool__(self):
        return len(self._data) > 0
    
