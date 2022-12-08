Feature: Overcome data addition

  Background: Default values
    Given a take profit configuration as 0.0100
    And a position precision threshold of 0.00001
    And a stop loss configuration as 0.0010

  Scenario: It initializes earnings columns for buying and selling at 0 by default
    Given any data frame with one row only
    When I apply the overcome to the data frame
    Then there is a new value as 0 in a new column about buying earnings
    And there is a new value as 0 in a new column about selling earnings

  Scenario: It sets up the take profit as earnings value on buying
    Given a data frame with the following rows
      | close  | high   | low    | comment  |
      | 1.0000 | 1.0000 | 1.0000 | starting |
      | 1.0000 | 1.0010 | 1.0000 |          |
    And a take profit configuration as 0.0010
    When I apply the overcome to the data frame
    Then the starting position earnings for buying value is equal to the take profit

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
    When I apply the overcome to the data frame
    Then the starting position earnings for selling value is equal to the take profit

  Scenario: It sets up a negative stop loss value as earnings value on buying
    Given a data frame with the following rows
      | close  | high   | low    | comment  |
      | 1.0000 | 1.0000 | 1.0000 | starting |
      | 1.0000 | 1.0000 | 0.9990 |          |
    And a stop loss configuration as 0.0010
    When I apply the overcome to the data frame
    Then the starting position earnings for buying value is equal to the negative value of stop loss

  Scenario: It sets up a negative stop loss value as earnings value on selling
    Given a data frame with the following rows
      | close  | high   | low    | comment  |
      | 1.0000 | 1.0000 | 1.0000 | starting |
      | 1.0000 | 1.0010 | 1.0000 |          |
    And a stop loss configuration as 0.0010
    When I apply the overcome to the data frame
    Then the starting position earnings for selling value is equal to the negative value of stop loss

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

  Scenario: It keeps the original index
    Given a data frame with a few rows with a non-numerical index
    When I apply the overcome to the data frame
    Then the result dataframe index is the same as the input dataframe

