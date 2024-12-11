import yaml
import os
from dataclasses import dataclass


with open(os.path.dirname(__file__) + '\config.yaml', 'r') as f:
    file_config = yaml.load(f, Loader=yaml.FullLoader)


def get_env_config(name):
    if name in os.environ:
        val = os.environ.get(name)
    elif name in file_config:
        val = file_config.get(name)
    else:
        raise ValueError(f'Параметра {name} в конфиге нет')

    return val


@dataclass
class Config:
    DB_CONNECT_URL = get_env_config('DB_CONNECT_URL')
    TG_BOT_TOKEN = get_env_config('TG_BOT_TOKEN')
    TIME_SLEEP = int(get_env_config('TIME_SLEEP'))
