from unittest.mock import Mock, call

import numpy as np
from behave import *
from pandas import DataFrame

from src.overcome.overcome import Overcome
from src.overcome.position.buying import Buying
from src.overcome.position.factory import Factory
from src.overcome.position.position import Position
from src.overcome.position.precisefactory import PreciseFactory
from src.overcome.position.selling import Selling


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
    def create_position_stub(*args):
        return Position(*args, context.position_threshold)

    buying = Buying()
    selling = Selling()
    position_factory = Mock(spec=Factory)
    position_factory.create = Mock(side_effect=create_position_stub)
    overcome = Overcome(
        position_factory,
        context.take_profit,
        context.stop_loss,
        buying,
        selling)
    context.result = overcome.apply(context.df)
    context.overcome = overcome
    context.position_factory = position_factory


@then("there is a buying and selling position pointing to every row")
def step_impl(context):
    calls = []
    for index in range(0, len(context.df) - 1):
        call_ = call(index, context.df.iloc[index]["close"])
        calls.append(call_)
    context.position_factory.create.assert_has_calls(calls)


@step("there is a selling position pointing to every row")
def step_impl(context):
    for index in context.df.index:
        assert isinstance(context.overcome.get_sell_position(index), Position)


@given("any data frame with one row only")
def step_impl(context):
    context.df = DataFrame(
        [[2.222, 1.111, 0.001]], columns=["high", "low", "close"])


@then("there is a new value as 0 in a new column about buying earnings")
def step_impl(context):
    assert 0 == context.df["earn_buying"][0]


@step("there is a new value as 0 in a new column about selling earnings")
def step_impl(context):
    assert 0 == context.df["earn_selling"][0]


def __append_expected_earnings(context, row):
    if "expected_to_earn_buying" not in context:
        context.expected_to_earn_buying = np.array([])
    if "expected_to_earn_selling" not in context:
        context.expected_to_earn_selling = np.array([])
    if "expected_buy_earn" in row.headings:
        context.expected_to_earn_buying = np.append(
            context.expected_to_earn_buying,
            np.float32(row["expected_buy_earn"]))
    if "expected_sell_earn" in row.headings:
        context.expected_to_earn_selling = np.append(
            context.expected_to_earn_selling,
            np.float32(row["expected_sell_earn"]))


@given("a data frame with the following rows")
def step_impl(context):
    table = {
        "close": [],
        "high": [],
        "low": [],
    }
    for index, row in enumerate(context.table):
        if "starting" == row["comment"]:
            context.starting_index = index
        table["close"].append(np.float32(row["close"]))
        table["high"].append(np.float32(row["high"]))
        table["low"].append(np.float32(row["low"]))
        __append_expected_earnings(context, row)
    context.df = DataFrame(table)


@step("a take profit configuration as {tp}")
def step_impl(context, tp):
    context.take_profit = np.float32(tp)


@then(
    "the starting position earnings for buying value is equal to the take profit")
def step_impl(context):
    assert context.take_profit == context.df["earn_buying"][0]


@step("a position precision threshold of {threshold}")
def step_impl(context, threshold):
    context.position_threshold = float(threshold)


@then("the starting position earnings for buying value is still nothing")
def step_impl(context):
    assert 0 == context.df["earn_buying"][0]


@then(
    "the starting position earnings for selling value is equal to the take profit")
def step_impl(context):
    assert context.take_profit == context.df["earn_selling"][0]


@step("a stop loss configuration as {sl}")
def step_impl(context, sl):
    context.stop_loss = np.float32(sl)


@then(
    "the starting position earnings for buying value is equal to the negative value of stop loss")
def step_impl(context):
    assert context.stop_loss == context.df["earn_buying"][0] * (-1)


@then(
    "the starting position earnings for selling value is equal to the negative value of stop loss")
def step_impl(context):
    assert context.stop_loss == context.df["earn_selling"][0] * (-1)


@then("the expected earnings match the results")
def step_impl(context):
    assert np.array_equal(
        np.sign(np.array(context.df["earn_buying"])),
        np.sign(np.array(context.expected_to_earn_buying))
    )
    assert np.array_equal(
        np.sign(np.array(context.df["earn_selling"])),
        np.sign(np.array(context.expected_to_earn_selling))
    )


@when("I apply the real overcome to the data frame")
def step_impl(context):
    position_factory = PreciseFactory(context.position_threshold)
    buying = Buying()
    selling = Selling()
    overcome = Overcome(
        position_factory,
        context.take_profit,
        context.stop_loss,
        buying,
        selling)
    context.result = overcome.apply(context.df)
    context.overcome = overcome


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
