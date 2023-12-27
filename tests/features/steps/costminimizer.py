import pandas as pd
from behave import *
import numpy as np

from overcome.minimizer.invalidminimization import InvalidMinimization
from overcome.minimizer.regularcostminimizer import RegularCostMinimizer


@given("a series of buying and selling operations along a timeline")
def step_impl(context):
    time_range = pd.date_range('1/1/2022', periods=60, freq='T')
    context.operations = pd.Series(
        np.random.choice(
            [context.BUY_CATEGORY, context.SELL_CATEGORY],
            len(time_range)
        ),
        index=time_range
    )


@when("I minimize the cost of the operations with a relaxing interval of {:d}")
def step_impl(context, interval: int):
    try:
        cost_minimizer = RegularCostMinimizer(
            context.RELAX_CATEGORY,
            int(interval),
            offset=context.offset
        )
        context.results = cost_minimizer.minimize(context.operations)
    except Exception as exc:
        context.exception = exc


@then("I get an invalid minimization error")
def step_impl(context):
    assert isinstance(context.exception, InvalidMinimization)


@then("I get the half of the operations from the given ones")
def step_impl(context):
    assert np.count_nonzero(context.results != context.RELAX_CATEGORY) == int(len(context.operations) / 2)


@then("I get the third of the operations from the given ones")
def step_impl(context):
    assert np.count_nonzero(context.results != context.RELAX_CATEGORY) == int(len(context.operations) / 3)


@step("the first given operation matches the first from the result")
def step_impl(context):
    assert context.results.index[0] == context.operations.index[0]
    assert context.results[0] == context.operations[0]


@step("a required offset of {:d}")
def step_impl(context, offset: int):
    context.offset = int(offset)


@step("no offset")
def step_impl(context):
    context.offset = 0


@step("the first given operation does not match the first from the result")
def step_impl(context):
    assert context.results.index[0] == context.operations.index[0]
    assert context.results[0] != context.operations[0]


@step("the first result is for relaxing")
def step_impl(context):
    assert context.RELAX_CATEGORY == context.results[0]
