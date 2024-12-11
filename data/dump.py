from sqlalchemy import create_engine
from data_model import User, \
    UserTickers, \
    Ticker
from sqlalchemy.orm import Session

engine = create_engine("sqlite:///bot.db", echo=True)

with Session(engine) as session:
    User.create(
        fields={
            'nickname': 'Tcar'
        },
        commit=True,
        session=session
    )

    Ticker.create(
        fields={
            'secid': 'SBER',
            'date': '2024-11-12',
            'close': 3.2
        },
        commit=True,
        session=session
    )

    UserTickers.create(
        fields={
            'user_id': 'Tcar',
            'ticker_secid': 'SBER',
        },
        commit=True,
        session=session
    )

