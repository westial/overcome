Feature: Cost Minimizer

  Background: Default values
    Given a relaxing label as 0
    And a selling label as 1
    And a buying label as 2
    And no offset

  Scenario: Fails when there is no minimization
    Given a series of buying and selling operations along a timeline
    When I minimize the cost of the operations with a relaxing interval of 0
    Then I get an invalid minimization error

  Scenario: Reduces the number of the operations to half
    Given a series of buying and selling operations along a timeline
    When I minimize the cost of the operations with a relaxing interval of 1
    Then I get the half of the operations from the given ones
    And the first given operation matches the first from the result

  Scenario: Reduces the number of the operations to a third
    Given a series of buying and selling operations along a timeline
    When I minimize the cost of the operations with a relaxing interval of 2
    Then I get the third of the operations from the given ones
    And the first given operation matches the first from the result

  Scenario: Applies an offset to the minimized operations
    Given a series of buying and selling operations along a timeline
    And a required offset of 2
    When I minimize the cost of the operations with a relaxing interval of 2
    Then I get the third of the operations from the given ones
    And the first given operation does not match the first from the result
    And the first result is for relaxing

  Scenario: Fails when the offset is greater than the interval
    Given a series of buying and selling operations along a timeline
    And a required offset of 3
    When I minimize the cost of the operations with a relaxing interval of 2
    Then I get an invalid minimization error

