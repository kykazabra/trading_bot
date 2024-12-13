from data.utils import Session
from data.data_model import Ticker
from sqlalchemy import select
import requests
import apimoex
import pandas as pd


def get_unique_tickers():
    with Session() as session:
        return [a[0] for a in session.execute(select(Ticker.secid).distinct()).all()]


def get_ticker_last_date(secid):
    with Session() as session:
        return session.execute(select(Ticker.date).where(Ticker.secid == secid).order_by(Ticker.date)).one()[0]


def get_all_ticker_data(name):
    with requests.Session() as rses:
        data = apimoex.get_board_history(rses, name)
        df = pd.DataFrame(data)
        df['TRADEDATE'] = pd.to_datetime(df['TRADEDATE'], format='%Y-%m-%d')

        return df


def increment_update_tickers():
    with Session() as session:
        unique_tickers = get_unique_tickers()

        for ticker in unique_tickers:
            data = get_all_ticker_data(ticker)

            last_date_in_db = get_ticker_last_date(ticker)

            increment = data[data['TRADEDATE'].dt.date > last_date_in_db]

            for _, row in increment.iterrows():
                dbrow = Ticker(
                    secid=ticker,
                    date=row['TRADEDATE'],
                    close=row['CLOSE'],
                    volume=row['VOLUME']
                )

                session.add(dbrow)

                print(f'В таблицу Ticker добавлена строка {dbrow}')