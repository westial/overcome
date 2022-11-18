Feature: Overcome data addition

  Background: Default values
    Given a take profit configuration as 0.0100
    And a position precision threshold of 0.0001
    And a stop loss configuration as 0.0010

  Scenario: It starts a buying and a selling positions on every row
    Given any data frame with a few rows
    When I apply the overcome to the data frame
    Then there is a buying and selling position pointing to every row

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
