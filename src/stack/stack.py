HEAD = 0
TAIL = 1


class Node:
    after = None
    before = None
    priority = None
    content = None


def create():
    return [None, None]


def __move_down(previous, from_this, in_stack):
    if None is from_this:
        return
    if from_this.after:
        previous.after = from_this.after
        previous.after.before = previous
    else:
        __set_tail(in_stack, previous)
        previous.after = None
    if previous.before:
        from_this.before = previous.before
        from_this.before.after = from_this
    else:
        __set_head(in_stack, from_this)
        from_this.before = None
    from_this.after = previous
    previous.before = from_this


def __replace(that, by_previous):
    by_previous.before = that.before
    that.before.after = by_previous
    by_previous.after = that
    that.before = by_previous


def __place(previous, from_this, in_stack):
    if None is from_this:
        return
    if from_this.priority < previous.priority:
        __move_down(previous, from_this, in_stack)
        __place(previous, previous.after, in_stack)


def __create_node(content, priority):
    node = Node()
    node.priority = priority
    node.content = content
    return node


def add(stack, content, priority):
    node = __create_node(content, priority)
    if empty(stack):
        __set_head(stack, node)
        __set_tail(stack, node)
    else:
        __push(stack, node)
        __place(node, node.after, stack)


def empty(stack):
    return None is stack[HEAD]


def head(stack):
    return stack[HEAD]


def __push(stack, node):
    last = head(stack)
    last.before = node
    node.after = last
    __set_head(stack, node)


def __set_head(stack, node):
    stack[HEAD] = node


def tail(stack):
    return stack[TAIL]


def __set_tail(stack, node):
    stack[TAIL] = node


def after(node):
    return node.after


def before(node):
    return node.before


def shift(stack):
    node = head(stack)
    __set_head(stack, node.after)
    if None is node.after:
        __set_tail(stack, None)
    else:
        node.after.before = None
    return node


def pop(stack):
    node = tail(stack)
    __set_tail(stack, node.before)
    if None is node.before:
        __set_head(stack, node.before)
    else:
        node.before.after = None
    return node
