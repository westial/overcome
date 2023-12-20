Feature: Overcome analysis

  Background: Default values
    Given a take profit configuration as 0.0020
    And a position precision threshold of 0.00001
    And a stop loss configuration as 0.0010
    And a relaxing label as 0
    And a selling label as 1
    And a buying label as 2

  Scenario: calculates a buying prediction profits
    Given a data frame with the following rows
      | close  | high   | low    | comment          |
      | 1.0000 | 1.0000 | 1.0000 | starting         |
      | 1.0000 | 1.0020 | 1.0000 | hits take profit |
    And predictions as "2 0"
    When I analyze the predictions
    Then I get a cumulated profit of 0.0020

  Scenario: calculates a buying prediction losses
    Given a data frame with the following rows
      | close  | high   | low    | comment        |
      | 1.0000 | 1.0000 | 1.0000 | starting       |
      | 1.0000 | 1.0000 | 0.9990 | hits stop loss |
    And predictions as "2 0"
    When I analyze the predictions
    Then I get a cumulated loss of 0.0010

  Scenario: calculates a selling prediction profits
    Given a data frame with the following rows
      | close  | high   | low    | comment        |
      | 1.0000 | 1.0000 | 1.0000 | starting       |
      | 1.0000 | 1.0000 | 0.9980 | hits stop loss |
    And predictions as "1 0"
    When I analyze the predictions
    Then I get a cumulated profit of 0.0020

  Scenario: calculates a selling prediction losses
    Given a data frame with the following rows
      | close  | high   | low    | comment          |
      | 1.0000 | 1.0000 | 1.0000 | starting         |
      | 1.0000 | 1.0010 | 1.0000 | hits take profit |
    And predictions as "1 0"
    When I analyze the predictions
    Then I get a cumulated loss of 0.0010

  Scenario: calculates losses and profits from all predictions set as selling
    Given a take profit configuration as 0.0010
    And a stop loss configuration as 0.0007
    And a data frame with the following rows
      | index | close  | high   | low    | expected_sell_earn | comment                                                                                                                                                                                                                                                                                                                          |
      | 0     | 1.0000 | 1.0000 | 1.0000 | -0.0007            | starting                                                                                                                                                                                                                                                                                                                         |
      | 1     | 1.0000 | 1.0000 | 1.0000 | -0.0007            |                                                                                                                                                                                                                                                                                                                                  |
      | 2     | 1.0005 | 1.0007 | 1.0000 | -0.0007            | sell 0 loses at 0.0007, sell 1 loses at 0.0007                                                                                                                                                                                                                                                                                   |
      | 3     | 1.0005 | 1.0010 | 1.0001 | -0.0007            | buy 0 wins at 0.0010, buy 1 wins at 0.0010                                                                                                                                                                                                                                                                                       |
      | 4     | 1.0006 | 1.0010 | 1.0002 | -0.0007            |                                                                                                                                                                                                                                                                                                                                  |
      | 5     | 1.0007 | 1.0011 | 1.0000 | -0.0007            |                                                                                                                                                                                                                                                                                                                                  |
      | 6     | 1.0008 | 1.0012 | 1.0004 | -0.0007            | sell 2 loses at 0.0007, sell 3 loses at 0.0007                                                                                                                                                                                                                                                                                   |
      | 7     | 1.0009 | 1.0013 | 1.0005 | 0.0010             | sell 4 loses at 0.0007                                                                                                                                                                                                                                                                                                           |
      | 8     | 1.0010 | 1.0015 | 1.0006 | 0.0010             | buy 2 wins at 0.0010, buy 3 wins at 0.0010, sell 5 loses at 0.0007, sell 6 loses at 0.0007                                                                                                                                                                                                                                       |
      | 9     | 1.0010 | 1.0015 | 0.9995 | 0.0010             | sell 2 wins at 0.0010, sell 3 wins at 0.0010, sell 4 wins at 0.0010, sell 5 wins at 0.0010, sell 6 wins at 0.0010, sell 7 wins at 0.0010, sell 8 wins at 0.0010, buy 2 loses at 0.0007, buy 3 loses at 0.0007, buy 4 loses at 0.0007, buy 5 loses at 0.0007, buy 6 loses at 0.0007, buy 7 loses at 0.0007, buy 8 loses at 0.0007 |
      | 10    | 1.0010 | 1.0015 | 0.9993 | 0.0010             | buy 0 loses at 0.0007, buy 1 loses at 0.0007, buy 9 loses at 0.0007, sell 9 wins at 0.0010                                                                                                                                                                                                                                       |
      | 11    | 1.0010 | 1.0016 | 0.9990 | 0                  | sell 0 wins at 0.0010, sell 1 wins at 0.0010, buy 4 wins at 0.0010, sell 7 loses at 0.0007, buy 10 loses at 0.0007, sell 10 wins at 0.0010
    And predictions as "1 1 1 1 1 1 1 1 1 1 1 1"
    When I analyze the predictions
    Then I get all expected sell earnings

  Scenario: calculates losses and profits from all predictions set as buying
    Given a take profit configuration as 0.0010
    And a stop loss configuration as 0.0007
    And a data frame with the following rows
      | index | close  | high   | low    | expected_buy_earn | comment                                                                                                                                                                                                                                                                                                                          |
      | 0     | 1.0000 | 1.0000 | 1.0000 | 0.0010            | starting                                                                                                                                                                                                                                                                                                                         |
      | 1     | 1.0000 | 1.0000 | 1.0000 | 0.0010            |                                                                                                                                                                                                                                                                                                                                  |
      | 2     | 1.0005 | 1.0007 | 1.0000 | 0.0010            | sell 0 loses at 0.0007, sell 1 loses at 0.0007                                                                                                                                                                                                                                                                                   |
      | 3     | 1.0005 | 1.0010 | 1.0001 | 0.0010            | buy 0 wins at 0.0010, buy 1 wins at 0.0010                                                                                                                                                                                                                                                                                       |
      | 4     | 1.0006 | 1.0010 | 1.0002 | -0.0007           |                                                                                                                                                                                                                                                                                                                                  |
      | 5     | 1.0007 | 1.0011 | 1.0000 | -0.0007           |                                                                                                                                                                                                                                                                                                                                  |
      | 6     | 1.0008 | 1.0012 | 1.0004 | -0.0007           | sell 2 loses at 0.0007, sell 3 loses at 0.0007                                                                                                                                                                                                                                                                                   |
      | 7     | 1.0009 | 1.0013 | 1.0005 | -0.0007           | sell 4 loses at 0.0007                                                                                                                                                                                                                                                                                                           |
      | 8     | 1.0010 | 1.0015 | 1.0006 | -0.0007           | buy 2 wins at 0.0010, buy 3 wins at 0.0010, sell 5 loses at 0.0007, sell 6 loses at 0.0007                                                                                                                                                                                                                                       |
      | 9     | 1.0010 | 1.0015 | 0.9995 | -0.0007           | sell 2 wins at 0.0010, sell 3 wins at 0.0010, sell 4 wins at 0.0010, sell 5 wins at 0.0010, sell 6 wins at 0.0010, sell 7 wins at 0.0010, sell 8 wins at 0.0010, buy 2 loses at 0.0007, buy 3 loses at 0.0007, buy 4 loses at 0.0007, buy 5 loses at 0.0007, buy 6 loses at 0.0007, buy 7 loses at 0.0007, buy 8 loses at 0.0007 |
      | 10    | 1.0010 | 1.0015 | 0.9993 | -0.0007           | buy 0 loses at 0.0007, buy 1 loses at 0.0007, buy 9 loses at 0.0007, sell 9 wins at 0.0010                                                                                                                                                                                                                                       |
      | 11    | 1.0010 | 1.0016 | 0.9990 | 0                 | sell 0 wins at 0.0010, sell 1 wins at 0.0010, buy 4 wins at 0.0010, sell 7 loses at 0.0007, buy 10 loses at 0.0007, sell 10 wins at 0.0010
    And predictions as "2 2 2 2 2 2 2 2 2 2 2 2"
    When I analyze the predictions
    Then I get all expected buy earnings

  Scenario: gets nothing from all predictions set as relaxing
    Given a take profit configuration as 0.0010
    And a stop loss configuration as 0.0007
    And a data frame with the following rows
      | index | close  | high   | low    | comment                                                                                                                                                                                                                                                                                                                          |
      | 0     | 1.0000 | 1.0000 | 1.0000 | starting                                                                                                                                                                                                                                                                                                                         |
      | 1     | 1.0000 | 1.0000 | 1.0000 |                                                                                                                                                                                                                                                                                                                                  |
      | 2     | 1.0005 | 1.0007 | 1.0000 | sell 0 loses at 0.0007, sell 1 loses at 0.0007                                                                                                                                                                                                                                                                                   |
      | 3     | 1.0005 | 1.0010 | 1.0001 | buy 0 wins at 0.0010, buy 1 wins at 0.0010                                                                                                                                                                                                                                                                                       |
      | 4     | 1.0006 | 1.0010 | 1.0002 |                                                                                                                                                                                                                                                                                                                                  |
      | 5     | 1.0007 | 1.0011 | 1.0000 |                                                                                                                                                                                                                                                                                                                                  |
      | 6     | 1.0008 | 1.0012 | 1.0004 | sell 2 loses at 0.0007, sell 3 loses at 0.0007                                                                                                                                                                                                                                                                                   |
      | 7     | 1.0009 | 1.0013 | 1.0005 | sell 4 loses at 0.0007                                                                                                                                                                                                                                                                                                           |
      | 8     | 1.0010 | 1.0015 | 1.0006 | buy 2 wins at 0.0010, buy 3 wins at 0.0010, sell 5 loses at 0.0007, sell 6 loses at 0.0007                                                                                                                                                                                                                                       |
      | 9     | 1.0010 | 1.0015 | 0.9995 | sell 2 wins at 0.0010, sell 3 wins at 0.0010, sell 4 wins at 0.0010, sell 5 wins at 0.0010, sell 6 wins at 0.0010, sell 7 wins at 0.0010, sell 8 wins at 0.0010, buy 2 loses at 0.0007, buy 3 loses at 0.0007, buy 4 loses at 0.0007, buy 5 loses at 0.0007, buy 6 loses at 0.0007, buy 7 loses at 0.0007, buy 8 loses at 0.0007 |
      | 10    | 1.0010 | 1.0015 | 0.9993 | buy 0 loses at 0.0007, buy 1 loses at 0.0007, buy 9 loses at 0.0007, sell 9 wins at 0.0010                                                                                                                                                                                                                                       |
      | 11    | 1.0010 | 1.0016 | 0.9990 | sell 0 wins at 0.0010, sell 1 wins at 0.0010, buy 4 wins at 0.0010, sell 7 loses at 0.0007, buy 10 loses at 0.0007, sell 10 wins at 0.0010
    And predictions as "0 0 0 0 0 0 0 0 0 0 0 0"
    When I analyze the predictions
    Then I get nothing because I am a fucking coward
