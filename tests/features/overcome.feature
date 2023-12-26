Feature: Overcome data addition

  Background: Default values
    Given a take profit configuration as 0.0100
    And a position precision threshold of 0.00001
    And a stop loss configuration as 0.0010

  Scenario: It initializes earnings columns for buying and selling at 0 by default
    Given any data frame with one row only
    When I apply the overcome with counters to the data frame
    Then there is a new value as 0 in a new column about buying earnings
    And there is a new value as 0 in a new column about selling earnings
    And there is a new value as 0 in a new column about buying length
    And there is a new value as 0 in a new column about selling length

  Scenario: It sets up the take profit as earnings value on buying
    Given a data frame with the following rows
      | close  | high   | low    | comment  |
      | 1.0000 | 1.0000 | 1.0000 | starting |
      | 1.0000 | 1.0010 | 1.0000 |          |
    And a take profit configuration as 0.0010
    When I apply the overcome with counters to the data frame
    Then the starting position earnings for buying value is equal to the take profit
    And the buying length is 1

  Scenario: It ignores to take profit on buying after reaching the maximum delay
    Given a maximum delay of 3 steps
    And a data frame with the following rows
      | close  | high   | low    | comment         |
      | 1.0000 | 1.0000 | 1.0000 | starting        |
      | 1.0005 | 1.0010 | 1.0000 | delayed         |
      | 1.0010 | 1.0011 | 1.0000 |                 |
      | 1.0000 | 1.0012 | 1.0000 |                 |
      | 1.0000 | 1.0013 | 1.0000 |                 |
      | 1.0000 | 1.0015 | 1.0000 | high is ignored |
    And a take profit configuration as 0.0010
    When I apply the overcome with counters to the data frame
    Then the starting position earnings for buying value is equal to the take profit
    And the last row value is ignored by the second row due to delay

  Scenario: It has no maximum delay
    Given a data frame with the following rows
      | close  | high   | low    | comment         |
      | 1.0000 | 1.0000 | 1.0000 | starting        |
      | 1.0005 | 1.0010 | 1.0000 | delayed         |
      | 1.0010 | 1.0011 | 1.0000 |                 |
      | 1.0000 | 1.0012 | 1.0000 |                 |
      | 1.0000 | 1.0013 | 1.0000 |                 |
      | 1.0000 | 1.0015 | 1.0000 | high is ignored |
    And a take profit configuration as 0.0010
    When I apply the overcome with counters to the data frame
    Then the starting position earnings for buying value is equal to the take profit
    And the last row value is not ignored by the second row due to delay

  Scenario: It ignores the starting point high to check the earnings value on buying for the same starting point row
    Given a data frame with the following rows
      | close  | high   | low    | comment  |
      | 1.0000 | 1.0010 | 1.0000 | starting |
      | 1.0000 | 1.0005 | 1.0000 |          |
    And a take profit configuration as 0.0010
    When I apply the overcome to the data frame
    Then the starting position earnings for buying value is still nothing

  Scenario: It sets up the take profit as earnings value on selling
    Given a data frame with the following rows
      | close  | high   | low    | comment  |
      | 1.0000 | 1.0000 | 1.0000 | starting |
      | 1.0000 | 1.0000 | 0.9990 |          |
    And a take profit configuration as 0.0010
    When I apply the overcome with counters to the data frame
    Then the starting position earnings for selling value is equal to the take profit
    And the selling length is 1

  Scenario: It sets up a negative stop loss value as earnings value on buying
    Given a data frame with the following rows
      | close  | high   | low    | comment  |
      | 1.0000 | 1.0000 | 1.0000 | starting |
      | 1.0000 | 1.0000 | 0.9990 |          |
    And a stop loss configuration as 0.0010
    When I apply the overcome with counters to the data frame
    Then the starting position earnings for buying value is equal to the negative value of stop loss
    And the buying length is 1

  Scenario: It sets up a negative stop loss value as earnings value on selling
    Given a data frame with the following rows
      | close  | high   | low    | comment  |
      | 1.0000 | 1.0000 | 1.0000 | starting |
      | 1.0000 | 1.0010 | 1.0000 |          |
    And a stop loss configuration as 0.0010
    When I apply the overcome with counters to the data frame
    Then the starting position earnings for selling value is equal to the negative value of stop loss
    And the selling length is 1

  Scenario: It sets up the appropriate value as earnings along a mixed loss and profit scenarios
    Given a take profit configuration as 0.0010
    And a stop loss configuration as 0.0007
    And a data frame with the following rows
      | index | close  | high   | low    | expected_buy_earn | expected_sell_earn | comment                                                                                                                                                                                                                                                                                                                          |
      | 0     | 1.0000 | 1.0000 | 1.0000 | 0.0010            | -0.0007            | starting                                                                                                                                                                                                                                                                                                                         |
      | 1     | 1.0000 | 1.0000 | 1.0000 | 0.0010            | -0.0007            |                                                                                                                                                                                                                                                                                                                                  |
      | 2     | 1.0005 | 1.0007 | 1.0000 | 0.0010            | -0.0007            | sell 0 loses at 0.0007, sell 1 loses at 0.0007                                                                                                                                                                                                                                                                                   |
      | 3     | 1.0005 | 1.0010 | 1.0001 | 0.0010            | -0.0007            | buy 0 wins at 0.0010, buy 1 wins at 0.0010                                                                                                                                                                                                                                                                                       |
      | 4     | 1.0006 | 1.0010 | 1.0002 | -0.0007           | -0.0007            |                                                                                                                                                                                                                                                                                                                                  |
      | 5     | 1.0007 | 1.0011 | 1.0000 | -0.0007           | -0.0007            |                                                                                                                                                                                                                                                                                                                                  |
      | 6     | 1.0008 | 1.0012 | 1.0004 | -0.0007           | -0.0007            | sell 2 loses at 0.0007, sell 3 loses at 0.0007                                                                                                                                                                                                                                                                                   |
      | 7     | 1.0009 | 1.0013 | 1.0005 | -0.0007           | 0.0010             | sell 4 loses at 0.0007                                                                                                                                                                                                                                                                                                           |
      | 8     | 1.0010 | 1.0015 | 1.0006 | -0.0007           | 0.0010             | buy 2 wins at 0.0010, buy 3 wins at 0.0010, sell 5 loses at 0.0007, sell 6 loses at 0.0007                                                                                                                                                                                                                                       |
      | 9     | 1.0010 | 1.0015 | 0.9995 | -0.0007           | 0.0010             | sell 2 wins at 0.0010, sell 3 wins at 0.0010, sell 4 wins at 0.0010, sell 5 wins at 0.0010, sell 6 wins at 0.0010, sell 7 wins at 0.0010, sell 8 wins at 0.0010, buy 2 loses at 0.0007, buy 3 loses at 0.0007, buy 4 loses at 0.0007, buy 5 loses at 0.0007, buy 6 loses at 0.0007, buy 7 loses at 0.0007, buy 8 loses at 0.0007 |
      | 10    | 1.0010 | 1.0015 | 0.9993 | -0.0007           | 0.0010             | buy 0 loses at 0.0007, buy 1 loses at 0.0007, buy 9 loses at 0.0007, sell 9 wins at 0.0010                                                                                                                                                                                                                                       |
      | 11    | 1.0010 | 1.0016 | 0.9990 | 0                 | 0                  | sell 0 wins at 0.0010, sell 1 wins at 0.0010, buy 4 wins at 0.0010, sell 7 loses at 0.0007, buy 10 loses at 0.0007, sell 10 wins at 0.0010                                                                                                                                                                                       |
    When I apply the overcome to the data frame
    Then the expected earnings match the results

  Scenario: It sets up the appropriate value as earnings and operation lengths along a mixed loss and profit scenarios
    Given a take profit configuration as 0.0010
    And a stop loss configuration as 0.0007
    And a data frame with the following rows
      | index | close  | high   | low    | expected_buy_earn | expected_sell_earn | expected_buy_lengths | expected_sell_lengths | comment                                                                                                                                                                                                                                                                                                                          |
      | 0     | 1.0000 | 1.0000 | 1.0000 | 0.0010            | -0.0007            | 3                    | 2                     | starting                                                                                                                                                                                                                                                                                                                         |
      | 1     | 1.0000 | 1.0000 | 1.0000 | 0.0010            | -0.0007            | 2                    | 1                     |                                                                                                                                                                                                                                                                                                                                  |
      | 2     | 1.0005 | 1.0007 | 1.0000 | 0.0010            | -0.0007            | 6                    | 4                     | sell 0 loses at 0.0007, sell 1 loses at 0.0007                                                                                                                                                                                                                                                                                   |
      | 3     | 1.0005 | 1.0010 | 1.0001 | 0.0010            | -0.0007            | 5                    | 3                     | buy 0 wins at 0.0010, buy 1 wins at 0.0010                                                                                                                                                                                                                                                                                       |
      | 4     | 1.0006 | 1.0010 | 1.0002 | -0.0007           | -0.0007            | 5                    | 2                     |                                                                                                                                                                                                                                                                                                                                  |
      | 5     | 1.0007 | 1.0011 | 1.0000 | -0.0007           | -0.0007            | 4                    | 3                     |                                                                                                                                                                                                                                                                                                                                  |
      | 6     | 1.0008 | 1.0012 | 1.0004 | -0.0007           | -0.0007            | 3                    | 2                     | sell 2 loses at 0.0007, sell 3 loses at 0.0007                                                                                                                                                                                                                                                                                   |
      | 7     | 1.0009 | 1.0013 | 1.0005 | -0.0007           | 0.0010             | 2                    | 2                     | sell 4 loses at 0.0007                                                                                                                                                                                                                                                                                                           |
      | 8     | 1.0010 | 1.0015 | 1.0006 | -0.0007           | 0.0010             | 1                    | 1                     | buy 2 wins at 0.0010, buy 3 wins at 0.0010, sell 5 loses at 0.0007, sell 6 loses at 0.0007                                                                                                                                                                                                                                       |
      | 9     | 1.0010 | 1.0015 | 0.9995 | -0.0007           | 0.0010             | 1                    | 1                     | sell 2 wins at 0.0010, sell 3 wins at 0.0010, sell 4 wins at 0.0010, sell 5 wins at 0.0010, sell 6 wins at 0.0010, sell 7 wins at 0.0010, sell 8 wins at 0.0010, buy 2 loses at 0.0007, buy 3 loses at 0.0007, buy 4 loses at 0.0007, buy 5 loses at 0.0007, buy 6 loses at 0.0007, buy 7 loses at 0.0007, buy 8 loses at 0.0007 |
      | 10    | 1.0010 | 1.0015 | 0.9993 | -0.0007           | 0.0010             | 1                    | 1                     | buy 0 loses at 0.0007, buy 1 loses at 0.0007, buy 9 loses at 0.0007, sell 9 wins at 0.0010                                                                                                                                                                                                                                       |
      | 11    | 1.0010 | 1.0016 | 0.9990 | 0                 | 0                  | 0                    | 0                     | sell 0 wins at 0.0010, sell 1 wins at 0.0010, buy 4 wins at 0.0010, sell 7 loses at 0.0007, buy 10 loses at 0.0007, sell 10 wins at 0.0010                                                                                                                                                                                       |
    When I apply the overcome with counters to the data frame
    Then the expected earnings match the results
    And the expected lengths match the results

  Scenario: It keeps the original index
    Given a data frame with a few rows with a non-numerical index
    When I apply the overcome with counters to the data frame
    Then the result dataframe index is the same as the input dataframe

  Scenario: It limits to open up new buying positions
    Given a take profit configuration as 0.0010
    And a stop loss configuration as 0.0007
    And a limit at 1 positions
    And a data frame with the following rows
      | index | close  | high   | low    | expected_buy_earn | expected_sell_earn | comment                                                                                              |
      | 0     | 1.0000 | 1.0000 | 1.0000 | 0.0010            | -0.0007            | starting                                                                                             |
      | 1     | 1.0000 | 1.0000 | 1.0000 | 0                 | 0                  |                                                                                                      |
      | 2     | 1.0000 | 1.0010 | 1.0000 | 0                 | 0                  | buy 0 wins, buy 1 does not win due to the limit, sell 0 loses, sell 1 does not lose due to the limit |
    When I apply the overcome to the data frame
    Then the expected earnings match the results

  Scenario: It limits to open up new selling positions
    Given a take profit configuration as 0.0010
    And a stop loss configuration as 0.0007
    And a limit at 1 positions
    And a data frame with the following rows
      | index | close  | high   | low    | expected_buy_earn | expected_sell_earn | comment                                                                                              |
      | 0     | 1.0000 | 1.0000 | 1.0000 | -0.0007           | 0.0010             | starting                                                                                             |
      | 1     | 1.0000 | 1.0000 | 1.0000 | 0                 | 0                  |                                                                                                      |
      | 2     | 1.0000 | 1.0000 | 0.9990 | 0                 | 0                  | sell 0 wins, sell 1 does not win due to the limit, buy 0 loses, buy 1 does not lose due to the limit |
    When I apply the overcome to the data frame
    Then the expected earnings match the results

  Scenario: It sets up the appropriate value as earnings along a mixed scenarios with limited positions
    Given a take profit configuration as 0.0010
    And a stop loss configuration as 0.0007
    And a limit at 2 positions
    And a data frame with the following rows
      | index | close  | high   | low    | expected_buy_earn | expected_sell_earn | comment                                                                                                                                                                                                                                                                                                                                                                       |
      | 0     | 1.0000 | 1.0000 | 1.0000 | 0.0010            | -0.0007            | starting                                                                                                                                                                                                                                                                                                                                                                      |
      | 1     | 1.0000 | 1.0000 | 1.0000 | 0.0010            | -0.0007            |                                                                                                                                                                                                                                                                                                                                                                               |
      | 2     | 1.0005 | 1.0007 | 1.0000 | 0                 | -0.0007            | sell 0 loses at 0.0007, sell 1 loses at 0.0007                                                                                                                                                                                                                                                                                                                                |
      | 3     | 1.0005 | 1.0010 | 1.0001 | 0.0010            | -0.0007            | buy 0 wins at 0.0010, buy 1 wins at 0.0010                                                                                                                                                                                                                                                                                                                                    |
      | 4     | 1.0006 | 1.0010 | 1.0002 | -0.0007           | 0                  |                                                                                                                                                                                                                                                                                                                                                                               |
      | 5     | 1.0007 | 1.0011 | 1.0000 | 0                 | 0                  |                                                                                                                                                                                                                                                                                                                                                                               |
      | 6     | 1.0008 | 1.0012 | 1.0004 | 0                 | -0.0007            | sell 2 loses at 0.0007, sell 3 loses at 0.0007                                                                                                                                                                                                                                                                                                                                |
      | 7     | 1.0009 | 1.0013 | 1.0005 | 0                 | 0.0010             | sell 4 does not lose due to the limit                                                                                                                                                                                                                                                                                                                                         |
      | 8     | 1.0010 | 1.0015 | 1.0006 | -0.0007           | 0.0010             | buy 2 does not win due to the limit, buy 3 wins at 0.0010, sell 5 does not lose due to the limit, sell 6 loses at 0.0007                                                                                                                                                                                                                                                      |
      | 9     | 1.0010 | 1.0015 | 0.9995 | -0.0007           | 0.0010             | sell 2 wins at 0.0010, sell 3 wins at 0.0010, sell 4 wins at 0.0010, sell 5 wins at 0.0010, sell 6 wins at 0.0010, sell 7 wins at 0.0010, sell 8 wins at 0.0010, buy 2 loses at 0.0007, buy 3 loses at 0.0007, buy 4 loses at 0.0007, buy 5 does not lose due to the limit, buy 6 does not due lose to the limit, buy 7 does not lose due to the limit, buy 8 loses at 0.0007 |
      | 10    | 1.0010 | 1.0015 | 0.9993 | -0.0007           | 0.0010             | buy 0 loses at 0.0007, buy 1 loses at 0.0007, buy 9 loses at 0.0007, sell 9 wins at 0.0010                                                                                                                                                                                                                                                                                    |
      | 11    | 1.0010 | 1.0016 | 0.9990 | 0                 | 0                  | sell 0 wins at 0.0010, sell 1 wins at 0.0010, buy 4 wins at 0.0010, sell 7 loses at 0.0007, buy 10 loses at 0.0007, sell 10 wins at 0.0010                                                                                                                                                                                                                                    |
    When I apply the overcome to the data frame
    Then the expected earnings match the results

  Scenario: It ignores the NaN values in the column
    Given a data frame with the following rows
      | close  | high   | low    | expected_buy_earn | expected_sell_earn | comment  |
      | 1.0000 | 1.0000 | 1.0000 | 0                 | 0                  | starting |
      | 1.0000 | 1.0005 | 1.0000 | 0                 | 0                  |          |
      | 1.0000 | 1.0010 | 1.0000 | 0.0010            | -0.0007            |          |
      | 1.0000 | 1.0015 | 1.0000 | 0.0010            | -0.0007            |          |
      | 1.0015 | 1.0015 | 1.0015 | 0.0010            | -0.0007            |          |
      | 1.0015 | 1.0015 | 1.0010 | -0.0007           | 0.0010             |          |
      | 1.0015 | 1.0015 | 1.0005 | -0.0007           | 0.0010             |          |
      | 1.0015 | 1.0015 | 1.0000 | -0.0007           | 0.0010             |          |
      | 1.0015 | 1.0015 | 1.0000 | -0.0007           | 0.0010             |          |
      | 1.0015 | 1.0015 | 1.0000 | 0                 | 0                  |          |
    And a take profit configuration as 0.0010
    And a stop loss configuration as 0.0007
    When I apply the overcome over the smoothed values from the target
    Then the expected earnings match the results

