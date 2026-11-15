# btc-cent-forecast-01

Forecast Bitcoin's US-dollar price 4 hours ahead, from the last 72 hours
of 1-minute closes (make.fun competition `btc-cent-forecast-01`).

## Model

Momentum-damped persistence. For each case, take the checkpoint close
(the last price in the case), look at how much the price moved over the
most recent 60 minutes, carry forward one tenth of that move, and clamp
the adjustment to ±$25:

```
forecast = close + clamp(0.10 * (close - close_60min_ago), -25, +25)
```

The checkpoint close alone is the baseline (persistence). The last
hour's direction is a weak signal, so only a fraction of it is used,
and the clamp keeps one sharp hour from dragging the guess far. The
forecast is the honest middle estimate of the close 240 minutes after
the checkpoint.

## Running it

`main.py` is Python 3.13, standard library only, no network. It reads
every `*.in` file in `$MAKEFUN_INPUT_DIR` (default `/input`) in name
order and writes one `{"forecasts": [{"case": <id>, "price": <guess>}]}`\
file per case to `$MAKEFUN_OUTPUT_DIR` (default `/output`). The same
case always produces the same output byte for byte.

```sh
mkdir -p out
MAKEFUN_INPUT_DIR=<kit>/input MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## License

MIT — see `LICENSE`.
