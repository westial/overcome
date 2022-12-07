"""
This is an attempt to move the stack module to cython.
DISCARDED. I definitively gave up with cython because:
    * There is no IDE debugging support.
    * `Cannot convert 'CStack' to Python object` is a very big obstacle to work
        with both python and cython together.
"""

from cython.operator cimport dereference as deref

HEAD = 0
TAIL = 1


cdef struct CNode:
    CNode *after
    CNode *before
    float priority
    int content

cdef struct CStack:
    CNode *head
    CNode *tail
    int cnodes_index
    CNode[1000] cnodes


cdef class Stack:
    def __init__(self, cstack):
        self.__cstack = cstack

    @property
    def cstack(self):
        return self.__cstack


class Node:
    after = None
    before = None
    priority = None
    content = None


def create():
    return Stack(_c_create())


cdef Stack _c_create():
    return Stack(CStack(NULL, NULL, 0, []))


cdef void __move_down(CNode *previous, CNode *from_this, CStack *in_stack):
    if NULL != deref(from_this).after:
        deref(previous).after = from_this.after
        deref(deref(previous).after).before = previous
    else:
        __set_tail(in_stack, previous)
        deref(previous).after = NULL
    if NULL != deref(previous).before:
        deref(from_this).before = previous.before
        deref(deref(from_this).before).after = from_this
    else:
        __set_head(in_stack, from_this)
        deref(from_this).before = NULL
    deref(from_this).after = previous
    deref(previous).before = from_this


cdef void __place(CNode *previous, CNode *from_this, CStack *in_stack):
    if NULL == deref(from_this):
        return void
    if deref(from_this).priority < deref(previous).priority:
        __move_down(previous, from_this, in_stack)
        __place(previous, previous.after, in_stack)


cdef CNode __create_node(int content, float priority):
    return CNode(NULL, NULL, priority, content)


def add(stack, content, priority):
    _c_add(&stack.cstack, content, priority)


cdef _c_add(CStack *stack, int content, float priority):
    cdef CNode node = __create_node(content, priority)
    deref(stack).cnodes[deref(stack).cnodes_index] = node
    deref(stack).cnodes_index += 1
    if _c_empty(stack):
        __set_head(stack, &node)
    else:
        __push(stack, node)
        __place(node, node.after, stack)


def empty(stack):
    return _c_empty(&stack.cstack)


cdef bint _c_empty(CStack *stack):
    return NULL == deref(stack).head


def head(stack):
    return deref(_c_head(&stack.cstack))


cdef CNode *_c_head(CStack *stack):
    return deref(stack).head


cdef void __push(CStack *stack, CNode *node):
    cdef CNode *last = _c_head(stack)
    deref(last).before = node
    deref(node).after = last
    __set_head(stack, node)


cdef void __set_head(CStack *stack, CNode *node):
    deref(stack).head = node


def tail(stack):
    return deref(_c_tail(&stack.cstack))


cdef CNode *_c_tail(CStack *stack):
    if NULL == deref(stack).tail:
        return _c_head(stack)
    return deref(stack).tail


cdef void __set_tail(CStack *stack, CNode *node):
    deref(stack).tail = node


def after(node):
    return deref(_c_after(&node))


cdef CNode *_c_after(CNode *node):
    return deref(node).after


def before(node):
    return deref(_c_before(&node))


cdef CNode *_c_before(CNode *node):
    return deref(node).before


def shift(stack):
    return deref(_c_shift(&stack.cstack))


cdef CNode *_c_shift(CStack *stack):
    node = _c_head(stack)
    __set_head(stack, deref(node).after)
    if NULL == deref(node).after:
        __set_tail(stack, NULL)
    else:
        deref(deref(node).after).before = NULL
    # TODO delete cnode from stack memory
    return node


def pop(stack):
    return deref(_c_pop(&stack.cstack))


cdef CNode *_c_pop(stack):
    node = _c_tail(stack)
    __set_tail(stack, deref(node).before)
    if NULL == deref(node).before:
        __set_head(stack, NULL)
    else:
        deref(deref(node).before).after = NULL
    # TODO delete cnode from stack memory
    return node
