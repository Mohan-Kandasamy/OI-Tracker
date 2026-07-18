Create a simple web application and host it on GitHub Pages.

Objective:
Build an OI tracker for index options on NSE/SENSEX.

Option Analysis (with appropriate color coding):
- Provide a dropdown to select the underlying index: Nifty or Sensex.
- Allow the user to select an expiry date.
- Allow the user to choose a time interval. Default options: 1 minute, 3 minutes, 5 minutes, 15 minutes, 1 hour, 4 hours, 1 day, and 1 week (default: 5 minutes).
- Once the selections are made, display the spot price and a list of strike prices around it, including +20 and -20 legs from the selected spot price.
  - Example: Nifty spot price: 24000
  - +20 legs: 24050, 24100, 24150, 24200, 24250, 24300, and so on
  - -20 legs: 23950, 23900, 23850, 23800, 23750, 23700, 23650, 23600, and so on

Columns to display:
- Time interval (day)
- Strike price
- Put LTP
- Probability
- Triggered price
- O=H / O=L
- Call LTP
- Change in put OI
- Change in call OI
- Difference in OI
- Difference in OI (%)
- Direction of change (up/down)
- Change in direction

