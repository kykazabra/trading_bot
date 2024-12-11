from data_model import Base
from sqlalchemy import create_engine
from env import Config

engine = create_engine(Config.DB_CONNECT_URL, echo=True)

Base.metadata.create_all(engine)