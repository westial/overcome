import numpy as np
from behave import *
from pandas import DataFrame


@step("a stop loss configuration as {sl}")
def step_impl(context, sl):
    context._stop_loss = np.float32(sl)


@step("a take profit configuration as {tp}")
def step_impl(context, tp):
    context._take_profit = np.float32(tp)


@step("a position precision threshold of {threshold}")
def step_impl(context, threshold):
    context.position_threshold = float(threshold)


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
        __append_expected_lengths(context, row)
        __append_expected_overlapped(context, row)
    context.df = DataFrame(table)


def __append_expected_overlapped(context, row):
    if "expected_overlapped_buying" not in context:
        context.expected_overlapped_buying = np.array([])
    if "expected_overlapped_buying" in row.headings:
        context.expected_overlapped_buying = np.append(
            context.expected_overlapped_buying,
            np.int16(row["expected_overlapped_buying"]))
    if "expected_overlapped_selling" not in context:
        context.expected_overlapped_selling = np.array([])
    if "expected_overlapped_selling" in row.headings:
        context.expected_overlapped_selling = np.append(
            context.expected_overlapped_selling,
            np.int16(row["expected_overlapped_selling"]))


def __append_expected_earnings(context, row):
    if "expected_buy_earn" not in context:
        context.expected_buy_earn = np.array([])
    if "expected_sell_earn" not in context:
        context.expected_sell_earn = np.array([])
    if "expected_buy_earn" in row.headings:
        context.expected_buy_earn = np.append(
            context.expected_buy_earn,
            np.float32(row["expected_buy_earn"]))
    if "expected_sell_earn" in row.headings:
        context.expected_sell_earn = np.append(
            context.expected_sell_earn,
            np.float32(row["expected_sell_earn"]))


def __append_expected_lengths(context, row):
    if "expected_buy_lengths" not in context:
        context.expected_buy_lengths = np.array([])
    if "expected_sell_lengths" not in context:
        context.expected_sell_lengths = np.array([])
    if "expected_buy_lengths" in row.headings:
        context.expected_buy_lengths = np.append(
            context.expected_buy_lengths,
            np.float32(row["expected_buy_lengths"]))
    if "expected_sell_lengths" in row.headings:
        context.expected_sell_lengths = np.append(
            context.expected_sell_lengths,
            np.float32(row["expected_sell_lengths"]))