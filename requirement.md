Create a simple web application and host it on GitHub Pages.

Objective:
Build an OI tracker for index options on NSE and SENSEX.

Functional Requirements:
- Provide a dropdown to select the underlying index: Nifty or Sensex.
- Allow the user to select an expiry date.
- Allow the user to choose a time interval. The default options should include 1 minute, 3 minutes, 5 minutes, 15 minutes, 1 hour, 4 hours, 1 day, and 1 week; the default selection should be 5 minutes.
- Populate the page with option-chain data from a configurable 5Paisa API endpoint.
  - The application should call the endpoint with the selected underlying, expiry date, and interval.
  - The integration should be flexible enough to support a JSON response with rows under common fields such as data, rows, records, optionChain, result, or similar.
  - If the API is not configured or returns an error, the page should keep the interface usable by falling back to locally generated sample rows.
- Once the user selects the index, expiry date, and interval, display the spot price and the available strike rows. The UI should render the returned data into the existing table and summary cards.

Columns to display:
- Sl. No.
- Date (current date)
- Time (based on the selected interval; default 5 minutes, Ex: 9:15, 9:20, 9:30, ... 3:25, 3:30)
- LTP (Ex: Nifty Last trade price)
- Day High / Day Low Break (Ex: D.H.B(Nifty Day High value))
- Change in put OI
- Change in call OI
- Difference in OI
- Difference in OI (%)
- Strength (strength should be in percentage with *)
- Net PCR
- Day High / Low Difference in OI
- Sentiment (Bullish / Bearish / Neutral)
- O=H / O=L

Logic for Strength and Net PCR:
- Strength should represent the intensity of the market bias based on the difference between the change in put OI and the change in call OI.
- Formula:
  - strength_score = abs(change_in_put_OI - change_in_call_OI)
  - If the strength score is very high and the difference points to call-side activity, the sentiment should be shown as Strong Bullish.
  - If the strength score is very high and the difference points to put-side activity, the sentiment should be shown as Strong Bearish.
  - If the score is low or the values are nearly balanced, the strength should be shown as Neutral or Weak.
- Net PCR should indicate the overall put-call balance.
- Formula:
  - net_pcr = (change_in_put_OI - change_in_call_OI) / (change_in_put_OI + change_in_call_OI), if the denominator is not zero
  - If net_pcr > 0, it suggests put dominance and a slightly bearish bias.
  - If net_pcr < 0, it suggests call dominance and a slightly bullish bias.
  - If net_pcr is close to 0, it indicates a balanced or neutral market condition.
