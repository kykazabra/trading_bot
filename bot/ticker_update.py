from data.utils import Session
from data.data_model import Ticker, AvailableTickers
from sqlalchemy import select, update, exists
import requests
import apimoex
import pandas as pd
from env import Config


def get_unique_tickers():
    with Session() as session:
        return [a[0] for a in session.execute(select(Ticker.secid).distinct()).all()]


def get_ticker_last_date(secid):
    with Session() as session:
        return session.execute(select(Ticker.date).where(Ticker.secid == secid).order_by(Ticker.date.desc())).first()[0]


def get_all_ticker_data(name):
    with requests.Session() as rses:
        data = apimoex.get_board_history(rses, name)
        df = pd.DataFrame(data)
        df['TRADEDATE'] = pd.to_datetime(df['TRADEDATE'], format='%Y-%m-%d')

        return df


def all_available_tickers():
    request_url = ('https://iss.moex.com/iss/engines/stock/'
                   'markets/shares/boards/TQBR/securities.json')
    arguments = {'securities.columns': ('SECID,'
                                        'REGNUMBER,'
                                        'LOTSIZE,'
                                        'SHORTNAME')}
    with requests.Session() as session:
        iss = apimoex.ISSClient(session, request_url, arguments)
        data = iss.get()
        df = pd.DataFrame(data['securities'])

    return df['SECID'].tolist()


def update_available_tickers():
    with Session() as session:
        session.query(AvailableTickers).delete()

    for ticker in all_available_tickers():
        session.add(
            AvailableTickers(
                secid=ticker
            )
        )


def dump_tickers(ticker_list):
    from .strategy import calc_signal_manual

    rows = []

    with Session() as session:
        for ticker in ticker_list:
            ticker_data = get_all_ticker_data(ticker)

            for _, row in ticker_data.iterrows():
                if row['CLOSE'] > 0:
                    dbrow = Ticker(
                        secid=ticker,
                        date=row['TRADEDATE'],
                        close=row['CLOSE'],
                        volume=row['VOLUME'],
                        signal=calc_signal_manual(ticker_data[ticker_data['TRADEDATE'] <= row['TRADEDATE']]['CLOSE'].iloc[-Config.STRATEGY_WINDOW:])
                    )

                    d = dbrow.__dict__.copy()
                    d.pop('_sa_instance_state')

                    rows.append(d)

                    session.add(dbrow)

                    print(f'В таблицу Ticker добавлена строка {dbrow}')

    return row


def increment_update_tickers():
    from .strategy import calc_signal_manual

    rows = []

    with Session() as session:
        unique_tickers = get_unique_tickers()

        for ticker in unique_tickers:
            ticker_data = get_all_ticker_data(ticker)

            last_date_in_db = get_ticker_last_date(ticker)

            increment = ticker_data[ticker_data['TRADEDATE'].dt.date > last_date_in_db]

            for _, row in increment.iterrows():
                if row['CLOSE'] > 0:
                    dbrow = Ticker(
                        secid=ticker,
                        date=row['TRADEDATE'],
                        close=row['CLOSE'],
                        volume=row['VOLUME'],
                        signal=calc_signal_manual(ticker_data[ticker_data['TRADEDATE'] <= row['TRADEDATE']]['CLOSE'].iloc[-Config.STRATEGY_WINDOW:])
                    )
                    d = dbrow.__dict__.copy()
                    d.pop('_sa_instance_state')

                    rows.append(d)

                    session.add(dbrow)

                    print(f'В таблицу Ticker добавлена строка {dbrow}')

    return rows