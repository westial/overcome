Overcome and Analysis
=====================

While Overcome provides the operation that fits for every OHLCV row, in a history
input data set; Analysis provides the profits and number of overlapped opened
positions for a given data set, with fulfilled operations.

Given a constant take profit and a stop loss, and a time base sorted data vector 
with the "high", "low", and "close" values from a stock market product, Overcome 
calculates the potential earnings in both, buying and selling for every step in 
the timeline.

Analysis by the other hand is a calculation after an operation has been already
set. It counts the overlapped buying and selling positions, separately, and the
profits for both as well.

## Install ##

Install from Pypi repository from at least a Python 3.7.

```shell
pip install overcome
```

## Overcome usage ##

Instantiate Overcome with the constant value for take profit and stop loss. 
A value for the precision threshold is required as well. The precision threshold
applies on whether a "close" value is close to the take profit or stop loss 
boundaries.

```python
outcome = Overcome(
        threshold=np.float32(0.00001),
        take_profit=np.float32(0.001),
        stop_loss=np.float32(0.001)
    )
```

Call `apply` method with the input and wait for the output. The required input
structure is a numpy array with a shape of (LENGTH, 3).

The order of the 3 columns is very strict. The first one is for the "high" 
values, the second one for the "low" values and the third one for "close" values.

```python
earn_buying, earn_selling = outcome.apply(high_low_close)
```

It returns a tuple of two arrays with the same number of items than the input,
indeed matching the same timeline. The first array is for the earnings from 
buying positions and the second one for the selling ones.

#### Opened positions limit ####

Opening all positions without limiting their number may be pretty risky. 
Overcome Simulation supports to set a predefined positions number limit in each
direction, buying and selling. So, for example, if the positions limit is set to
10, when the first 10 positions will be opened in the simulated outcome, the
following ones won't open, and then they are not accountable for profit or loss.

Creating an Overcome instance with opened positions limited at 10 for buying and 
10 for selling is as follows.

```python
outcome = Overcome(
        threshold=np.float32(0.00001),
        take_profit=np.float32(0.001),
        stop_loss=np.float32(0.001),
        positions_limit=10
    )
```

#### Counters and maximum delay ####

Boolean `has_counters` is an optional constructor argument to ask for a counter
for each, buying and selling positions, with the number of steps between the
position starting and closing steps. These optional information comes in the
returning tuple as two new items.

```python
outcome = Overcome(
        threshold=np.float32(0.00001),
        take_profit=np.float32(0.001),
        stop_loss=np.float32(0.001),
        positions_limit=10,
        has_counters=True
    )
earn_buying, earn_selling, buying_lengths, selling_lengths = \
    outcome.apply(high_low_close)
```

Having the number of steps of every operation lets us filter out the longer
operations in order to get only the fastest ones, apparently the most accurate 
ones. The integer type optional argument `max_delay` makes to ignore the earnings
from the operations longer than the maximum steps set in this value. In the
following example, the earnings from the positions with more than 10 steps will
be ignored and set to 0.

Setting a value over 0 to `max_delay` forces `has_counters` to enable in order
to get the required counts. So, the returning tuple length is 4 as well.

```python
outcome = Overcome(
        threshold=np.float32(0.00001),
        take_profit=np.float32(0.001),
        stop_loss=np.float32(0.001),
        positions_limit=10,
        max_delay=10
    )
earn_buying, earn_selling, buying_lengths, selling_lengths = \
    outcome.apply(high_low_close)
```

### Input from a dataframe ###

Starting with a Dataframe as `df` from any product historical data, convert the 
columns into the required input by the following expression.

```python
high_low_close = df[["high", "low", "close"]].to_numpy(dtype=np.float32)
```
        
Then apply the calculation and merge the result into the original Dataframe as 
follows.

```python
(df["earn_buying"], df["earn_selling"]) = outcome.apply(high_low_close)
```

## Example ##

The following table is an example of dataframe with the new columns for
buying and selling earnings already calculated. This table is part of a test
suite, so the data is not real, it is just prepared to achieve a scenario with
a variety of positive and negative earnings in both operations, buying and 
selling.

The configuration for take profit for this example is 0.001 and the stop loss is
0.0007. 

|timestamp|close|high|low|earn_buying|earn_selling|
|:----|:----|:----|:----|:----|:----|
|2022-04-01 00:01:00|1.0|1.0|1.0|0.001|-0.0007|
|2022-04-01 00:02:00|1.0|1.0|1.0|0.001|-0.0007|
|2022-04-01 00:03:00|1.0005|1.0007|1.0|0.001|-0.0007|
|2022-04-01 00:04:00|1.0005|1.001|1.0001|0.001|-0.0007|
|2022-04-01 00:05:00|1.0006|1.001|1.0002|-0.0007|-0.0007|
|2022-04-01 00:06:00|1.0007|1.0011|1.0|-0.0007|-0.0007|
|2022-04-01 00:07:00|1.0008|1.0012|1.0004|-0.0007|-0.0007|
|2022-04-01 00:08:00|1.0009|1.0013|1.0005|-0.0007|0.001|
|2022-04-01 00:09:00|1.001|1.0015|1.0006|-0.0007|0.001|
|2022-04-01 00:10:00|1.001|1.0015|0.9995|-0.0007|0.001|
|2022-04-01 00:11:00|1.001|1.0015|0.9993|-0.0007|0.001|
|2022-04-01 00:12:00|1.001|1.0016|0.999|0.0|0.0|

## Analysis usage ##

Instantiate Analysis by giving an integer type constant for every distinct
operation: relax, selling, buying.

```python
analysis = Analysis(
        threshold=np.float32(0.00001),
        take_profit=np.float32(0.001),
        stop_loss=np.float32(0.001),
        categories={
            "relax": 0,
            "sell": 1,
            "buy": 2
        }
)
results = analysis.apply(predictions, ohlcv_dataframe)
```

### Minimizing costs ###

There is a service that in a regular alternate way, sets off the given active
positions like buying or selling. This service is an optional dependency of 
Analysis, so it allow to analyze the given operations, by minimizing them in 
the way on.

The following example, sets off 2 of 3 positions. Starting at the second row of 
the given operations due to the RegularCostMinimizer's offset optional argument.

```python
RELAX_CATEGORY = 0

analysis = Analysis(
        threshold=np.float32(0.00001),
        take_profit=np.float32(0.001),
        stop_loss=np.float32(0.001),
        categories={
            "relax": RELAX_CATEGORY,
            "sell": 1,
            "buy": 2
        },
        minimizer=RegularCostMinimizer(RELAX_CATEGORY, 2, offset=1)
)
results = analysis.apply(predictions, ohlcv_dataframe)
```

## Test and development ## 

This project is based on BDD development. Any change starts here [tests/features](tests/features).

Moreover, you can find the most specific documentation about any module and
package of this project.

Tests require [behave](https://behave.readthedocs.io/) and [pandas](https://pandas.pydata.org/).
Execute the command below from the source code root directory to install the 
extra requirements to start developing on this project.

```
pip install -e ".[dev]"
```

PYTHONPATH must contain the main source directory [./src](./src) to execute the 
tests. Use the fantastic  command as 
follows.

```
PYTHONPATH=./src behave tests/features
```

There are a few integration tests as well. Execute as follows.

```
PYTHONPATH=./src python tests/integration/test_overcome.py
```

## Author ##

Jaume Mila Bea <jaume@westial.com>