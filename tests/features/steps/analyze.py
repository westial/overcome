import numpy as np
import pandas as pd
from behave import *

from overcome.analysis import Analysis


@step('predictions as "{values}" from relaxing as {relaxing}, selling as {selling} and buying as {buying}')
def step_impl(context, values: str, relaxing: int, selling: int, buying: int):
    context.RELAX_CATEGORY = int(relaxing)
    context.SELL_CATEGORY = int(selling)
    context.BUY_CATEGORY = int(buying)
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
    last_profit_result = context.results.cumsum().iloc[-1]
    assert np.isclose(expected, last_profit_result)
