import time
from env import Config
from ticker_update import increment_update_tickers, get_ticker_last_date
from strategy import calc_signals
from data.utils import Session
from data.data_model import Ticker
from sqlalchemy import update
from allerts import allert_buy_ticker, allert_sell_ticker


def raise_proactive_bot():
    while True:
        increment_update_tickers()

        signals = calc_signals()

        for ticker, signal in signals.items():
            if signal == 1:
                allert_buy_ticker(ticker)

            if signal == -1:
                allert_sell_ticker(ticker)

            with Session() as session:
                session.execute(update(Ticker).where(Ticker.secid == ticker, Ticker.date == get_ticker_last_date(ticker)).values(signal=signal))

        time.sleep(Config.TIME_SLEEP)