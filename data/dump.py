from data_model import User, \
    UserTickers, \
    Ticker
from utils import Session
import datetime


with Session() as session:
    session.add(
        User(
            nickname='Tcar'
        )
    )

    session.add(
        Ticker(
            secid='SBER',
            date=datetime.datetime.strptime('2024-11-12', "%Y-%m-%d").date(),
            close=3.2
        )
    )

    session.add(
        UserTickers(
            user_id='Tcar',
            ticker_secid='SBER',
        )
    )

