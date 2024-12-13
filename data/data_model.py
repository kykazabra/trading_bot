import sqlalchemy as sql
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Ticker(Base):
    __tablename__ = "ticker"

    id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)
    secid = sql.Column(sql.String, nullable=False)
    date = sql.Column(sql.Date, nullable=False)
    close = sql.Column(sql.Float, nullable=False)
    volume = sql.Column(sql.Float)
    signal = sql.Column(sql.Integer)

    def __repr__(self):
        return f'Ticker(id={self.id}, secid={self.secid}, date={self.date}, close={self.close}, volume={self.volume}, signal={self.signal})'


class UserTickers(Base):
    __tablename__ = "user_ticker"

    id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)
    user_id = sql.Column(sql.Integer, sql.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    ticker_secid = sql.Column(sql.String, sql.ForeignKey("ticker.secid", ondelete="CASCADE"), nullable=False)

    def __repr__(self):
        return f'UserTickers(id={self.id}, user_id={self.user_id}, ticker_secid={self.ticker_secid})'


class User(Base):
    __tablename__ = "user"

    id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)
    nickname = sql.Column(sql.String, unique=True, nullable=False)

    def __repr__(self):
        return f'User(id={self.id}, nickname={self.nickname}'