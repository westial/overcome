Overcome
========

Given a constant take profit and a stop loss, and a time base sorted data vector 
with the "high", "low", and "close" values from a stock market product, Overcome 
calculates the potential earnings in both, buying and selling for every step in 
the timeline.

## Usage ##

Instantiate the Overcome with the constant value for take profit and stop loss. 
A value for the precision threshold is required as well. The precision threshold
applies on whether a "close" value is close to the take profit or stop loss 
boundaries.
```
overcome = Overcome(
        threshold=np.float32(0.00001),
        take_profit=np.float32(0.001),
        stop_loss=np.float32(0.001)
    )
```

Call `apply` method with the input and wait for the output. The required input
structure is a numpy array with a shape of (LENGTH, 3).

The order of the 3 columns is very strict. The first one is for the "high" 
values, the second one for the "low" values and the third one for "close" values.

```
earn_buying, earn_selling = overcome.apply(high_low_close)
```

It returns a tuple of two arrays with the same number of items than the input,
indeed matching the same timeline. The first array is for the earnings from 
buying positions and the second one for the selling ones.

#### Opened positions limit ####

Opening all positions without limiting their number may be pretty risky. 
Overcome simulation supports to set a predefined positions number limit in each
direction, buying and selling. So, for example, if the positions limit is set to
10, when the first 10 positions will be opened in the simulated overcome, the
following ones won't open, and then they are not accountable for profit or loss.

Creating an Overcome instance with opened positions limited at 10 for buying and 
10 for selling is as follows.

```
overcome = Overcome(
        threshold=np.float32(0.00001),
        take_profit=np.float32(0.001),
        stop_loss=np.float32(0.001),
        positions_limit=10
    )
```



### Input from a dataframe ###

Starting with a Dataframe as `df` from any product historical data, convert the 
columns into the required input by the following expression.

```
high_low_close = df[["high", "low", "close"]].to_numpy(dtype=np.float32)
```
        
Then apply the calculation and merge the result into the original Dataframe as 
follows.

```
(df["earn_buying"], df["earn_selling"]) = overcome.apply(high_low_close)
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