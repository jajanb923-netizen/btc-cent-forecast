#!/usr/bin/env python3
"""Forecast Bitcoin's price 4 hours ahead from the last 72 hours of
1-minute closes.

Model (momentum-damped persistence):
    forecast = close + clamp(0.10 * (close - close_60min_ago), -25, +25)

The checkpoint close is the honest middle estimate of the price 4 hours
later. The last hour's move is a weak signal of where the price is
heading, so only a tenth of it is carried forward, and the adjustment is
clamped to +/- $25 so a single sharp hour cannot drag the guess far.

Input contract (makefun/btc-cent-case/v1): read every ``*.in`` file in
$MAKEFUN_INPUT_DIR (default /input) in name order. Each file is one
case: ``{"case": <id>, "markets": [{"prices": [4320 closes]}]}``.
Output contract: write /output/<id>.out (or $MAKEFUN_OUTPUT_DIR) as
``{"forecasts": [{"case": <id>, "price": <forecast>]}``.

Python 3.13, standard library only, no network, deterministic: the same
case always produces the same output byte for byte.
"""

import json
import os
from pathlib import Path

DAMPING = 0.10        # fraction of the last hour's move carried forward
CLAMP_USD = 25.0      # largest adjustment allowed, in dollars
LOOKBACK_MINUTES = 60  # how far back the "last hour" reaches


def forecast(prices):
    """Return the 4-hour-ahead forecast for one list of minute closes."""
    close = prices[-1]
    if len(prices) > LOOKBACK_MINUTES:
        hour_ago = prices[-1 - LOOKBACK_MINUTES]
    else:
        hour_ago = prices[0]
    adjustment = DAMPING * (close - hour_ago)
    if adjustment > CLAMP_USD:
        adjustment = CLAMP_USD
    elif adjustment < -CLAMP_USD:
        adjustment = -CLAMP_USD
    guess = close + adjustment
    # Keep the guess inside the range the rules accept (0, 10_000_000),
    # and round it to the price grid's own scale of 5 decimals.
    if guess <= 0.0:
        guess = 0.01
    elif guess >= 10_000_000.0:
        guess = 9_999_999.99
    return round(guess, 5)


def main():
    in_dir = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    for in_file in sorted(in_dir.glob("*.in")):
        case = json.loads(in_file.read_text(encoding="utf-8"))
        prices = case["markets"][0]["prices"]
        price = forecast(prices)
        out = {"forecasts": [{"case": case["case"], "price": price}]}
        out_file = out_dir / (in_file.stem + ".out")
        out_file.write_text(
            json.dumps(out, separators=(",", ":")), encoding="utf-8"
        )


if __name__ == "__main__":
    main()
