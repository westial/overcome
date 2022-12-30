HEAD = 0
TAIL = 1


class Node:
    after = None
    before = None
    priority = None
    content = None


class Stack:
    def __init__(self):
        self.__edges = [None, None]
        self.__length = 0

    def __len__(self):
        return self.__length

    def __move_down(self, previous, from_this):
        if from_this.after:
            previous.after = from_this.after
            previous.after.before = previous
        else:
            self.__set_tail(previous)
            previous.after = None
        if previous.before:
            from_this.before = previous.before
            from_this.before.after = from_this
        else:
            self.__set_head(from_this)
            from_this.before = None
        from_this.after = previous
        previous.before = from_this

    def __place(self, previous, from_this):
        if None is from_this:
            return
        if from_this.priority < previous.priority:
            self.__move_down(previous, from_this)
            self.__place(previous, previous.after)

    @staticmethod
    def __create_node(content, priority):
        node = Node()
        node.priority = priority
        node.content = content
        return node

    def add(self, content, priority):
        node = self.__create_node(content, priority)
        if self.empty():
            self.__set_head(node)
            self.__set_tail(node)
        else:
            self.__push(node)
            self.__place(node, node.after)
        self.__length += 1

    def empty(self):
        return None is self.__edges[HEAD]

    def head(self):
        return self.__edges[HEAD]

    def __push(self, node):
        last = self.head()
        last.before = node
        node.after = last
        self.__set_head(node)

    def __set_head(self, node):
        self.__edges[HEAD] = node

    def tail(self):
        if not self.__edges[TAIL]:
            return self.head()
        return self.__edges[TAIL]

    def __set_tail(self, node):
        self.__edges[TAIL] = node

    @staticmethod
    def after(node):
        return node.after

    @staticmethod
    def before(node):
        return node.before

    def shift(self):
        node = self.head()
        self.__set_head(node.after)
        if None is node.after:
            self.__set_tail(None)
        else:
            node.after.before = None
        self.__length -= 1
        return node

    def pop(self):
        node = self.tail()
        self.__set_tail(node.before)
        if None is node.before:
            self.__set_head(None)
        else:
            node.before.after = None
        self.__length -= 1
        return node
