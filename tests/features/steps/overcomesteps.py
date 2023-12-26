import numpy as np
from behave import *
from pandas import DataFrame

from overcome.overcome import Overcome


@given("any data frame with a few rows")
def step_impl(context):
    context.df = DataFrame(
        [
            ["a1", "b1", 1.0, 0, 0],
            ["a2", "b2", 2.0, 0, 0],
            ["a3", "b3", 3.0, 0, 0]],
        index=["2020", "2021", "2022"],
        columns=["a", "b", "close", "high", "low"])


@when("I apply the overcome to the data frame")
def step_impl(context):
    overcome = Overcome(
            context.position_threshold,
            context._take_profit,
            context._stop_loss,
            context.buying_limit if "buying_limit" in context else -1
    )
    context.result = context.df
    high_low_close = context.df[["high", "low", "close"]].to_numpy(dtype=np.float32)
    (
        context.result["earn_buying"],
        context.result["earn_selling"]
    ) = overcome.apply(high_low_close)
    context.overcome = overcome


@when("I apply the overcome with counters to the data frame")
def step_impl(context):
    overcome = Overcome(
            context.position_threshold,
            context._take_profit,
            context._stop_loss,
            positions_limit=context.buying_limit if "buying_limit" in context else -1,
            has_counters=True,
            max_delay=context.max_delay if "max_delay" in context else 0
    )
    context.result = context.df
    high_low_close = context.df[["high", "low", "close"]].to_numpy(dtype=np.float32)
    (
        context.result["earn_buying"],
        context.result["earn_selling"],
        context.result["buying_lengths"],
        context.result["selling_lengths"],
    ) = overcome.apply(high_low_close)
    context.overcome = overcome


@given("any data frame with one row only")
def step_impl(context):
    context.df = DataFrame(
        [[1.111, 2.222, 0.001]], columns=["low", "high", "close"])


@then("there is a new value as 0 in a new column about buying earnings")
def step_impl(context):
    assert 0 == context.df["earn_buying"][0]


@step("there is a new value as 0 in a new column about selling earnings")
def step_impl(context):
    assert 0 == context.df["earn_selling"][0]


@then(
    "the starting position earnings for buying value is equal to the take profit")
def step_impl(context):
    assert context._take_profit == context.df["earn_buying"][0]


@then("the starting position earnings for buying value is still nothing")
def step_impl(context):
    assert 0 == context.df["earn_buying"][0]


@then(
    "the starting position earnings for selling value is equal to the take profit")
def step_impl(context):
    assert context._take_profit == context.df["earn_selling"][0]


@then(
    "the starting position earnings for buying value is equal to the negative value of stop loss")
def step_impl(context):
    assert context._stop_loss == context.df["earn_buying"][0] * (-1)


@then(
    "the starting position earnings for selling value is equal to the negative value of stop loss")
def step_impl(context):
    assert context._stop_loss == context.df["earn_selling"][0] * (-1)


@then("the expected earnings match the results")
def step_impl(context):
    assert np.array_equal(
        np.sign(np.array(context.df["earn_buying"])),
        np.sign(np.array(context.expected_buy_earn))
    )
    assert np.array_equal(
        np.sign(np.array(context.df["earn_selling"])),
        np.sign(np.array(context.expected_sell_earn))
    )


@then("the expected lengths match the results")
def step_impl(context):
    assert np.array_equal(
        np.sign(np.array(context.df["buying_lengths"])),
        np.sign(np.array(context.expected_buy_lengths))
    )
    assert np.array_equal(
        np.sign(np.array(context.df["selling_lengths"])),
        np.sign(np.array(context.expected_buy_lengths))
    )


@given("a data frame with a few rows with a non-numerical index")
def step_impl(context):
    context.df = DataFrame(
        [
            ["a1", "b1", 1.0, 0, 0],
            ["a2", "b2", 2.0, 0, 0],
            ["a3", "b3", 3.0, 0, 0]],
        index=["2020-11-01", "2021-12-01", "2022-04-30"],
        columns=["a", "b", "close", "high", "low"])
    context.original_index = context.df.index


@then("the result dataframe index is the same as the input dataframe")
def step_impl(context):
    assert 0 == len(context.original_index.difference(context.result.index))


@step("a limit at {:d} positions")
def step_impl(context, count):
    context.buying_limit = int(count)


@step("there is a new value as 0 in a new column about buying length")
def step_impl(context):
    assert 0 == context.df["buying_lengths"][0]


@step('the buying length is {:d}')
def step_impl(context, expected_length):
    assert expected_length == context.df["buying_lengths"][0]


@step('the selling length is {:d}')
def step_impl(context, expected_length):
    assert expected_length == context.df["selling_lengths"][0]


@step("there is a new value as 0 in a new column about selling length")
def step_impl(context):
    assert 0 == context.df["selling_lengths"][0]


@when("I apply the overcome over the smoothed values from the target")
def step_impl(context):
    overcome = Overcome(
            context.position_threshold,
            context._take_profit,
            context._stop_loss,
            positions_limit=context.buying_limit if "buying_limit" in context else -1,
            has_counters=True
    )
    context.result = context.df
    high_low_close = context.df[["high", "low", "close"]].rolling(window=3).mean().to_numpy(dtype=np.float32)
    (
        context.result["earn_buying"],
        context.result["earn_selling"],
        context.result["buying_lengths"],
        context.result["selling_lengths"],
    ) = overcome.apply(high_low_close)
    context.overcome = overcome


@given("a maximum delay of {:d} steps")
def step_impl(context, max_delay):
    context.max_delay = max_delay


@step("the last row value is ignored by the second row due to delay")
def step_impl(context):
    assert np.isclose(0, context.df["earn_buying"][1], 0.00001)


@step("the last row value is not ignored by the second row due to delay")
def step_impl(context):
    assert context._take_profit == context.df["earn_buying"][1]
