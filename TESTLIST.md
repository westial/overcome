Test list for Overcome
======================

+ It starts a buying and a selling positions on every row. 
+ It initializes earnings columns for buying and selling at 0 by default.
+ It sets up the take profit value into the buying starting position when the
  starting position value plus the take profit result value is equal or under 
  the current high value.
+ It sets up the take profit value into the selling starting position when the
  starting position value minus the take profit result value is equal or over 
  the current low value.
+ It sets up the negatively signed stop loss value into the buying starting 
  position when the starting position value minus the stop loss result value 
  is equal or over the current low value.
+ It sets up the negatively signed stop loss value into the selling starting 
  position when the starting position value plus the stop loss result value 
  is equal or under the current high value.