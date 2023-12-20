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
