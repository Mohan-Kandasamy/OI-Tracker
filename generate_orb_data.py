import json
import os
from datetime import datetime
from pathlib import Path


def round_to_strike(value, step=50):
    return int(round(value / step) * step)


def build_payload():
    spot = 25183.45
    orb_high = 25220
    orb_low = 25110
    atm_strike = round_to_strike(spot)
    intrinsic = max(spot - atm_strike, 0)
    time_value = 41
    break_even = atm_strike + max(20, time_value)
    recommendation = f"BUY {atm_strike} CE"
    confidence = 84
    updated = datetime.now().strftime("%H:%M:%S")
    strikes = [
        {
            "strike": atm_strike,
            "side": "ATM",
            "signal": "BUY CE",
            "signalColor": "positive",
            "orbHigh": orb_high,
            "orbLow": orb_low,
            "intrinsic": intrinsic,
            "timeValue": time_value,
            "breakEven": break_even,
            "status": "Momentum",
        },
        {
            "strike": atm_strike - 50,
            "side": "OTM",
            "signal": "WAIT",
            "signalColor": "neutral",
            "orbHigh": orb_high,
            "orbLow": orb_low,
            "intrinsic": 0,
            "timeValue": max(20, time_value - 3),
            "breakEven": atm_strike - 50 + max(20, time_value),
            "status": "Watch",
        },
        {
            "strike": atm_strike + 50,
            "side": "ITM",
            "signal": "BUY PE",
            "signalColor": "negative",
            "orbHigh": orb_high,
            "orbLow": orb_low,
            "intrinsic": max(spot - (atm_strike + 50), 0),
            "timeValue": max(20, time_value + 3),
            "breakEven": atm_strike + 50 + max(20, time_value),
            "status": "Range",
        },
    ]
    return {
        "symbol": "^NSEI",
        "spot": spot,
        "orbHigh": orb_high,
        "orbLow": orb_low,
        "atmStrike": atm_strike,
        "intrinsic": intrinsic,
        "timeValue": time_value,
        "breakEven": break_even,
        "riskReward": "1 : 2.5",
        "recommendation": recommendation,
        "confidence": confidence,
        "updated": updated,
        "candle": "Breakout ▲",
        "signal": "BUY",
        "status": [
            {"label": "Above VWAP", "active": True},
            {"label": "Above EMA21", "active": True},
            {"label": "Volume Confirmed", "active": True},
            {"label": "RSI = 63", "active": True},
        ],
        "strikes": strikes,
    }


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    payload = build_payload()
    output_path = root / "data.json"
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Updated {output_path}")
