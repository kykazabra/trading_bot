import time
from env import Config
from ticker_update import increment_update_tickers, get_ticker_last_date, update_available_tickers
from strategy import get_last_signals
from data.utils import Session
from data.data_model import Ticker
from sqlalchemy import update
from allerts import allert_buy_ticker, allert_sell_ticker
import pandas as pd


def raise_proactive_bot():
    while True:
        update_available_tickers()
        df = pd.DataFrame(increment_update_tickers())

        signals = get_last_signals(df)

        for ticker, signal in signals.items():
            if signal == 1:
                allert_buy_ticker(ticker)

            elif signal == -1:
                allert_sell_ticker(ticker)

        time.sleep(Config.TIME_SLEEP)