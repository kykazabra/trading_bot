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


class UserTickers(Base):
    __tablename__ = "user_ticker"

    id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)
    user_id = sql.Column(sql.Integer, sql.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    ticker_secid = sql.Column(sql.String, sql.ForeignKey("ticker.secid", ondelete="CASCADE"), nullable=False)


class User(Base):
    __tablename__ = "user"

    id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)
    nickname = sql.Column(sql.String, unique=True, nullable=False)