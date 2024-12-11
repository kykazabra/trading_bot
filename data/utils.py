from env import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def Session():
    engine = create_engine(Config.DB_CONNECT_URL)
    return sessionmaker(engine).begin()