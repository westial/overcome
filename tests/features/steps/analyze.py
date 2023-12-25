import numpy as np
import pandas as pd
from behave import *

from overcome.analysis import Analysis


@step('predictions as "{values}"')
def step_impl(context, values: str):
    context.predictions = pd.Series([int(v) for v in values.split()])


@when("I analyze the predictions")
def step_impl(context):
    analysis = Analysis(
            context.position_threshold,
            context._take_profit,
            context._stop_loss,
            categories={
                "relax": context.RELAX_CATEGORY,
                "sell": context.SELL_CATEGORY,
                "buy": context.BUY_CATEGORY
            }
    )
    context.results = analysis.apply(
        context.predictions,
        context.df
    )


@then("I get a cumulated profit of {:f}")
def step_impl(context, expected: float):
    profits = context.results["profits_buying"].add(context.results["profits_selling"])
    cumulated_result = profits.cumsum().iloc[-1]
    assert np.isclose(expected, cumulated_result)


@then("I get a cumulated loss of {:f}")
def step_impl(context, expected: float):
    profits = context.results["profits_buying"].add(context.results["profits_selling"])
    cumulated_result = profits.cumsum().iloc[-1]
    assert np.isclose(-expected, cumulated_result)


@step("a relaxing label as {:d}")
def step_impl(context, value):
    context.RELAX_CATEGORY = int(value)


@step("a selling label as {:d}")
def step_impl(context, value):
    context.SELL_CATEGORY = int(value)


@step("a buying label as {:d}")
def step_impl(context, value):
    context.BUY_CATEGORY = int(value)


@then("I get all expected sell earnings")
def step_impl(context):
    profits = context.results["profits_selling"]
    cumulated_result = profits.cumsum().iloc[-1]
    expected = context.expected_sell_earn.cumsum()[-1]
    assert np.isclose(expected, cumulated_result)


@then("I get all expected buy earnings")
def step_impl(context):
    profits = context.results["profits_buying"]
    cumulated_result = profits.cumsum().iloc[-1]
    expected = context.expected_buy_earn.cumsum()[-1]
    assert np.isclose(expected, cumulated_result)


@then("I get nothing because I am a fucking coward")
def step_impl(context):
    profits = context.results["profits_buying"].add(context.results["profits_selling"])
    cumulated_result = profits.cumsum().iloc[-1]
    assert np.isclose(0, cumulated_result)


@step("I get the amount of overlapped buying positions")
def step_impl(context):
    assert np.array_equal(
        context.expected_overlapped_buying,
        context.results["overlapped_buying"]
    )


@step("I get the amount of overlapped selling positions")
def step_impl(context):
    assert np.array_equal(
        context.expected_overlapped_selling,
        context.results["overlapped_selling"]
    )
