import random

import numpy as np
from behave import *

from src.overcome.position.stack import add, empty, head, tail, after, \
    create, before, shift, pop

THRESHOLD = 0.01

POSITION_INDEX = 1
POSITION_CLOSE_VALUE = 0


@given("a position with close value as {:f} and index as {:d}")
def step_impl(context, close, index):
    pair = np.float32(close), int(index)
    if not hasattr(context, "pairs"):
        context.pairs = []
    context.pairs.append(pair)


@then("the stack is not empty")
def step_impl(context):
    assert not empty(context.stack)


def __fill_up(stack, with_pairs):
    for pair in with_pairs:
        add(stack, pair[POSITION_INDEX], pair[POSITION_CLOSE_VALUE])


@step("I add all pairs to the stack")
def step_impl(context):
    stack = create()
    __fill_up(stack, context.pairs)
    context.stack = stack


@then("the stack head close value is {:f}")
def step_impl(context, expected):
    assert np.isclose(expected, head(context.stack).priority, THRESHOLD)


@step("the stack tail close value is {:f}")
def step_impl(context, expected):
    assert np.isclose(expected, tail(context.stack).priority, THRESHOLD)


@step("the close value after head is {:f}")
def step_impl(context, expected):
    assert np.isclose(expected, after(head(context.stack)).priority, THRESHOLD)


@step("the close value before tail is {:f}")
def step_impl(context, expected):
    assert np.isclose(expected, before(tail(context.stack)).priority, THRESHOLD)


@when("I shift the stack")
def step_impl(context):
    context.result = shift(context.stack)


@then("I get the node with value as {:f}")
def step_impl(context, expected):
    assert np.isclose(expected, context.result.priority, THRESHOLD)


@step("the node with value as {:f} is removed from the head")
def step_impl(context, expected):
    assert not np.isclose(expected, head(context.stack).priority, THRESHOLD)


@step("the stack is empty")
def step_impl(context):
    assert empty(context.stack)


@when("I pop the stack")
def step_impl(context):
    context.result = pop(context.stack)


@then("I get the tail node with value as {:f}")
def step_impl(context, expected):
    assert np.isclose(expected, context.result.priority, THRESHOLD)


@step("the node with value as {:f} is removed from the tail")
def step_impl(context, expected):
    assert not np.isclose(expected, tail(context.stack).priority, THRESHOLD)


def __node_provider_factory(get_first: callable, attr_for_next, stack):
    def provide(node):
        nonlocal get_first, attr_for_next, stack
        if node:
            return getattr(node, attr_for_next)
        return get_first(stack)

    return provide


def __assert_match(nodes: callable, expected_list):
    node = None
    for expected_index in range(0, len(expected_list)):
        node = nodes(node)
        assert int(expected_list[expected_index]) == int(node.priority)


@then('the close values from head to tail are "{raw_list}"')
def step_impl(context, raw_list: str):
    provide = __node_provider_factory(head, "after", context.stack)
    expected_list = raw_list.split(",")
    __assert_match(provide, expected_list)


@then('the close values from tail to head are "{raw_list}"')
def step_impl(context, raw_list: str):
    provide = __node_provider_factory(tail, "before", context.stack)
    expected_list = raw_list.split(",")
    __assert_match(provide, expected_list)


@given("several randomly sorted lists of close values")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(
        u'STEP: Given several randomly sorted lists of close values')


@given('several randomly sorted lists of values as "{raw_list}"')
def step_impl(context, raw_list: str):
    values = list(map(lambda value: (float(value), 0), raw_list.split(",")))
    pairs_sets = []
    for i in range(0, 100):
        pairs_sets.append(random.sample(values, k=len(values)))
    context.pairs_sets = pairs_sets


@when("I add every sorted list into a different stack")
def step_impl(context):
    stacks = []
    for pairs in context.pairs_sets:
        stack = create()
        __fill_up(stack, pairs)
        stacks.append(stack)
    context.stacks = stacks


@then('all close values from head to tail for every stack are "{raw_list}"')
def step_impl(context, raw_list: str):
    expected_list = raw_list.split(",")
    for stack in context.stacks:
        provide = __node_provider_factory(head, "after", stack)
        __assert_match(provide, expected_list)


@then('all close values from tail to head for every stack are "{raw_list}"')
def step_impl(context, raw_list: str):
    expected_list = raw_list.split(",")
    for stack in context.stacks:
        provide = __node_provider_factory(tail, "before", stack)
        __assert_match(provide, expected_list)
