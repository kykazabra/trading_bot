from sqlalchemy import create_engine
from data_model import Base

engine = create_engine("sqlite:///bot.db", echo=True)

Base.metadata.create_all(engine)