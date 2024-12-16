import time
from env import Config
from tg.ticker_update import increment_update_tickers, get_ticker_last_date, update_available_tickers
from tg.strategy import get_last_signals
from tg.allerts import allert_buy_ticker, allert_sell_ticker
import pandas as pd


def raise_proactive_bot(bot):
    while True:
        update_available_tickers()
        df = pd.DataFrame(increment_update_tickers())
        if len(df) > 0:
            signals = get_last_signals(df)

            for ticker, signal in signals.items():
                if signal == 1:
                    allert_buy_ticker(bot, ticker)

                elif signal == -1:
                    allert_sell_ticker(bot, ticker)

        time.sleep(Config.TIME_SLEEP)