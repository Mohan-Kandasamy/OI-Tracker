Create a simple web application and host it on GitHub Pages.

Objective:
Build an OI tracker for index options on NSE and SENSEX.

Functional Requirements:
- Provide a dropdown to select the underlying index: Nifty or Sensex.
- Allow the user to select an expiry date.
- Allow the user to choose a time interval. The default options should include 1 minute, 3 minutes, 5 minutes, 15 minutes, 1 hour, 4 hours, 1 day, and 1 week; the default selection should be 5 minutes.
- Provide a connection configuration popup on the front-end so the user can enter their own 5Paisa connection details for the current session.
  - The popup should collect app source, app name, user ID, password, user key, encryption key, and an optional access token/market-data URL.
  - The form should post the values to the backend, which should store the configuration in session state and use it for subsequent requests while the browser session is active.
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



Create a new page (ORB Dashbaord) with below information and use below architecture
and existing index.html page should be in a menu option

Recommended Architecture
                   yfinance (Python)
                          │
          Fetch NIFTY/SENSEX every minute
                          │
          Calculate ORB + Intrinsic Value
                          │
                 Generate data.json
                          │
           GitHub Actions (every minute*)
                          │
                  Push data.json
                          │
                  GitHub Repository
                          │
                  GitHub Pages Site
                          │
      HTML + CSS + JavaScript Dashboard


Use yfinance (seprate python file)

Example
import yfinance as yf

nifty = yf.Ticker("^NSEI")

data = nifty.history(
    period="1d",
    interval="1m"
)

print(data.tail())

Calculate First 30-Minute High
first30 = data.between_time("09:15", "09:44")

high = first30["High"].max()
low = first30["Low"].min()

print(high, low)
Current Spot Price
spot = data.iloc[-1]["Close"]
ATM Strike
atm = round(spot / 50) * 50

For example:

Spot = 25183

ATM = 25200
Intrinsic Value
spot = 25183
strike = 25200

call_intrinsic = max(spot - strike, 0)
put_intrinsic = max(strike - spot, 0)

print(call_intrinsic)
print(put_intrinsic)

show the results in list view with color code.

for every refresh, based on spot, calculate orb for thre strike price (ATM,  ITM, OTM), based on market movement, update  ORB values  for the existing strike price instead of deleting it.

on a initial load, based on spot price add a strike on both the side (spot = 25183
strike 1 = 25200, strike 2 = 25150)

Example:
At 9:30 AM

spot = 25183
ATM = 25200
strike = 25200

At 9:35 AM

update the value for strike price 25200 and add a new record for 25250.
spot = 25239
ATM = 25250
strike = 25250


Dashboard Layout (with sample data)
------------------------------------------------------
         NIFTY ORB OPTION DASHBOARD
------------------------------------------------------

Spot Price        : 25,183.45
ATM Strike        : 25,200

ORB High          : 25,220
ORB Low           : 25,110

Current Candle    : Breakout ▲

Recommendation

🟢 BUY 25200 CE

--------------------------------------

Intrinsic Value   : ₹83
Time Value        : ₹41
Break-even        : 25,241

Risk Reward       : 1 : 2.5

--------------------------------------

Status

✔ Above VWAP
✔ Above EMA21
✔ Volume Confirmed
✔ RSI = 63

Confidence : 84%

--------------------------------------

Last Updated

09:46:03



Technologies
Frontend
HTML
CSS
JavaScript
Chart.js (candlestick or line charts)
Bootstrap or Tailwind CSS (optional)

Hosted on:

GitHub Pages
Backend

Python

Libraries:

yfinance
pandas
numpy

Output:

{
  "spot": 25183.45,
  "orbHigh": 25220,
  "orbLow": 25110,
  "atmStrike": 25200,
  "intrinsic": 83,
  "timeValue": 41,
  "recommendation": "BUY CE",
  "confidence": 84,
  "updated": "09:46"
}
JavaScript Example
fetch("data.json")
  .then(response => response.json())
  .then(data => {
    document.getElementById("spot").innerText = data.spot;
    document.getElementById("orbHigh").innerText = data.orbHigh;
    document.getElementById("signal").innerText = data.recommendation;
  });
Future Enhancements

As your dashboard evolves, you could add:

Live NIFTY and SENSEX cards
ORB breakout signals
ATM, ITM, and OTM strike suggestions
Intrinsic and time value
Break-even calculator
Daily P&L tracker
Trade history
Win-rate analytics
EMA 9/21, VWAP, RSI, Supertrend
Volume confirmation
Support and resistance levels
Risk/reward calculator
Dark mode