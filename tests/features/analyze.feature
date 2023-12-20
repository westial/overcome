Feature: Overcome analysis

  Background: Default values
    Given a take profit configuration as 0.0020
    And a position precision threshold of 0.00001
    And a stop loss configuration as 0.0010

  Scenario: calculates a prediction profits
    Given a data frame with the following rows
      | close  | high   | low    | comment  |
      | 1.0000 | 1.0000 | 1.0000 | starting |
      | 1.0000 | 1.0020 | 1.0000 |          |
    And predictions as "2 0" from relaxing as 0, selling as 1 and buying as 2
    When I analyze the predictions
    Then I get a cumulated profit of 0.0020
