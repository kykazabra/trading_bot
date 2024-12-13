import pandas as pd
from data.utils import Session
from sqlalchemy import select
from data.data_model import Ticker
from env import Config


def calculate_rsi(close, period=14):
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return {
        'now': rsi.iloc[-1],
        'prev': rsi.iloc[-2]
    }


def calculate_macd(close, fast_period=12, slow_period=26, signal_period=9):
    fast_ema = close.ewm(span=fast_period, adjust=False).mean()
    slow_ema = close.ewm(span=slow_period, adjust=False).mean()

    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    macd_histogram = macd_line - signal_line

    return {
        'line': macd_line.iloc[-1],
        'signal': signal_line.iloc[-1],
        'hist': macd_histogram.iloc[-1]
    }


def calc_signal(rsi, macd):
    # Условия на покупку
    if (
        rsi['now'] > 50 >= rsi['prev'] and  # Пересечение уровня 50
        macd['hist'] > 0 and
        macd['line'] > macd['signal']
    ):
        return 1

        # Условия на продажу
    elif (
        rsi['now'] < 50 <= rsi['prev'] and  # Пересечение уровня 50 вниз
        macd['hist'] < 0 and
        macd['line'] < macd['signal']
    ):
        return -1

    # Закрытие позиции при экстремальных уровнях RSI
    if rsi['now'] >= 70:
        return -1
    elif rsi['now'] <= 30:
        return -1

    return 0


def calc_signal_auto(ticker, date_end=None, date_start=None):
    query = select(Ticker.close).filter(Ticker.secid == ticker)

    with Session() as session:
        if date_start:
            query = query.filter(Ticker.date >= date_start)

        if date_end:
            query = query.filter(Ticker.date <= date_end)

        if Config.STRATEGY_WINDOW:
            ticker_data = reversed(session.execute(query.order_by(Ticker.date.desc()).limit(Config.STRATEGY_WINDOW)).all())
        else:
            ticker_data = session.execute(query.order_by(Ticker.date)).all()

        close = pd.Series([tcr[0] for tcr in ticker_data])

        if len(close) < 26:
            return 0

        rsi = calculate_rsi(close)
        macd = calculate_macd(close)

        signal = calc_signal(rsi, macd)

        return signal


def calc_signals():
    from .ticker_update import get_unique_tickers

    signals = {}

    for ticker in get_unique_tickers():
        signals[ticker] = calc_signal_auto(ticker)

    return signals