from data.utils import Session
from data.data_model import Ticker, AvailableTickers, User, UserTickers
from sqlalchemy import select, func, update, exists
import requests
import apimoex
import pandas as pd
from env import Config


def get_unique_tickers():
    with Session() as session:
        return [a[0] for a in session.execute(select(Ticker.secid).distinct()).all()]


def get_len_n_user_tickets(si, n, diag_id):
    # diag_id = check_nd_add_user(diag_id)
    # приходится так т.к тут функция получает только si+n записей
    with Session() as session:
        len_ = session.execute(select(func.count(UserTickers.ticker_secid)).distinct().where(
            UserTickers.user_id == get_user_id(diag_id))).scalar_one()
        return len_, [a[0] for a in session.execute(
            select(UserTickers.ticker_secid).distinct().where(UserTickers.user_id == get_user_id(diag_id)).order_by(
                UserTickers.ticker_secid.asc()).offset(si).limit(n)).all()]


def get_len_n_not_user_tickets(si, n, diag_id):
    # diag_id = check_nd_add_user(diag_id)
    # приходится так т.к тут функция получает только si+n записей
    with Session() as session:
        len_ = session.execute(select(func.count(AvailableTickers.secid)).where(AvailableTickers.secid \
                                                                                .not_in(
            select(UserTickers.ticker_secid).distinct().where(
                UserTickers.user_id == get_user_id(diag_id))))).scalar_one()
        return len_, [a[0] for a in session.execute(select(AvailableTickers.secid).where(AvailableTickers.secid \
                                                                                         .not_in(
            select(UserTickers.ticker_secid).distinct().where(UserTickers.user_id == get_user_id(diag_id)))) \
                                                    .order_by(AvailableTickers.secid.asc()).offset(si).limit(n)).all()]


def get_ticker_users(ticker_secid):
    with Session() as session:
        return [get_user_diagid(id[0]) for id in session.execute(
            select(UserTickers.user_id).distinct().where(UserTickers.ticker_secid == ticker_secid)).all()]


'''
def get_total_len():
    with Session() as session:
        return session.execute(select(func.count(AvailableTickers.secid)).distinct()).scalar_one()
'''


def get_ticker_last_date(secid):
    with Session() as session:
        return session.execute(select(Ticker.date).where(Ticker.secid == secid).order_by(Ticker.date.desc())).first()[0]


def check_nd_add_user(diag_id):
    with Session() as session:
        if session.execute(select(func.count(User.id)).where(User.diag_id == diag_id)).scalar_one() == 0:
            dbrow = User(diag_id=diag_id)
            d = dbrow.__dict__.copy()
            d.pop('_sa_instance_state')
            session.add(dbrow)
    return diag_id


def get_user_id(diag_id):
    with Session() as session:
        return session.execute(select(User.id).where(User.diag_id == diag_id)).scalar_one()


def get_user_diagid(user_id):
    with Session() as session:
        return session.execute(select(User.diag_id).where(User.id == user_id)).scalar_one()


def get_user_tickers(diag_id):
    user_id = get_user_id(diag_id)

    with Session() as session:
        return [a[0] for a in session.execute(select(UserTickers.ticker_secid).where(UserTickers.user_id == user_id)).all()]


def get_ticker_info(secid):
    with Session() as session:
        return [i for i in session.execute(select(Ticker.close, Ticker.date, Ticker.signal, Ticker.secid).where(Ticker.secid == secid))]


def add_ticker_to_user(ticker_secid, diag_id):
    # diag_id = check_nd_add_user(diag_id)
    with Session() as session:
        dbrow = UserTickers(user_id=get_user_id(diag_id), ticker_secid=ticker_secid)
        d = dbrow.__dict__.copy()
        d.pop('_sa_instance_state')
        session.add(dbrow)

    if ticker_secid not in get_unique_tickers():
        dump_tickers([ticker_secid])


def remove_ticker_from_user(ticker_secid, diag_id):
    # diag_id = check_nd_add_user(diag_id)
    with Session() as session:
        session.query(UserTickers).where(
            (UserTickers.user_id == get_user_id(diag_id)) & (UserTickers.ticker_secid == ticker_secid)).delete()

        if ticker_secid not in [x[0] for x in session.execute(select(UserTickers.ticker_secid).distinct()).all()]:
            session.query(Ticker).where(Ticker.secid == ticker_secid).delete()


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
            ticker_data = get_all_ticker_data(ticker)[0:-30]  # DEMO

            for _, row in ticker_data.iterrows():
                if row['CLOSE'] > 0:
                    dbrow = Ticker(
                        secid=ticker,
                        date=row['TRADEDATE'],
                        close=row['CLOSE'],
                        volume=row['VOLUME'],
                        signal=calc_signal_manual(
                            ticker_data[ticker_data['TRADEDATE'] <= row['TRADEDATE']]['CLOSE'].iloc[
                            -Config.STRATEGY_WINDOW:])
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
                        signal=calc_signal_manual(
                            ticker_data[ticker_data['TRADEDATE'] <= row['TRADEDATE']]['CLOSE'].iloc[
                            -Config.STRATEGY_WINDOW:])
                    )
                    d = dbrow.__dict__.copy()
                    d.pop('_sa_instance_state')

                    rows.append(d)

                    session.add(dbrow)

                    print(f'В таблицу Ticker добавлена строка {dbrow}')
    return rows