import telebot
from telebot import types
from env import Config

bot = telebot.TeleBot(Config.TG_BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start_command(message):
    text = 'Привет!\nЯ бот - трейдер.\n\nВыбирай акции с помощью команды /add_ticker, а я буду следить за ними и ' \
           'сообщать, когда их лучше купить или продать!\n\nУдалить акцию ты можешь с помощью /drop_ticker '

    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['add_ticker'])
def add_ticker_command(message):
    text = 'Какую акцию из предложенных ты хочешь добавить?'

    markup = types.InlineKeyboardMarkup()

    for _ in range(5):
      buttons = [
        
      ]

      markup.row()




    bot.send_message(message.chat.id, text)