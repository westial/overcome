Feature: Positions double priority stack

  Scenario: Adds one node into the stack
    Given a position with close value as 1.1 and index as 12
    When I add all pairs to the stack
    Then the stack is not empty

  Scenario: Keeps nodes sorted by the close value from smaller to bigger
    Given a position with close value as 1.1 and index as 12
    And a position with close value as 1.5 and index as 11
    And a position with close value as 1.3 and index as 90
    When I add all pairs to the stack
    Then the stack head close value is 1.1
    And the stack tail close value is 1.5
    And the close value after head is 1.3
    And the close value before tail is 1.3

  Scenario: Sorts a list with repeated values in nodes
    Given a position with close value as 6.0 and index as 0
    Given a position with close value as 9.0 and index as 0
    And a position with close value as 2.0 and index as 0
    And a position with close value as 1.0 and index as 0
    And a position with close value as 4.0 and index as 0
    And a position with close value as 6.0 and index as 0
    And a position with close value as 1.0 and index as 0
    And a position with close value as 1.0 and index as 0
    And a position with close value as 9.0 and index as 0
    When I add all pairs to the stack
    Then the close values from head to tail are "1,1,1,2,4,6,6,9,9"
    Then the close values from tail to head are "9,9,6,6,4,2,1,1,1"

  Scenario: Sorts any list of nodes from smaller to bigger
    Given several randomly sorted lists of values as "0,1,2,3,4,5,6,7,8,9"
    When I add every sorted list into a different stack
    Then all close values from head to tail for every stack are "0,1,2,3,4,5,6,7,8,9"
    Then all close values from tail to head for every stack are "9,8,7,6,5,4,3,2,1,0"

  Scenario: Removes one node from the head
    Given a position with close value as 9.1 and index as 12
    And a position with close value as 1.5 and index as 11
    And a position with close value as 10.3 and index as 90
    And I add all pairs to the stack
    When I shift the stack
    Then I get the node with value as 1.5
    And the node with value as 1.5 is removed from the head
    Then the stack head close value is 9.1

  Scenario: Removes one node from the tail
    Given a position with close value as 9.1 and index as 12
    And a position with close value as 1.5 and index as 11
    And a position with close value as 10.3 and index as 90
    And I add all pairs to the stack
    When I pop the stack
    Then I get the node with value as 10.3
    And the node with value as 10.3 is removed from the tail
    And the stack tail close value is 9.1

  Scenario: Removes the last node from the head
    Given a position with close value as 9.1 and index as 12
    And I add all pairs to the stack
    When I shift the stack
    Then I get the node with value as 9.1
    And the stack is empty
