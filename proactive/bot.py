import time
from env import Config
from ticker_update import increment_update_tickers
from strategy import calc_signals


def raise_proactive_bot():
    while True:
        increment_update_tickers()

        signals = calc_signals()

        time.sleep(Config.TIME_SLEEP)