import telebot
from env import Config
from threading import Thread
from tg.proactive import raise_proactive_bot
from tg.reactive import raise_reactive_bot


def run():
    bot = telebot.TeleBot(Config.TG_BOT_TOKEN)
    #cog = __import__("tg.reactive")
    #cog.run(bot) #add handlers
    raise_reactive_bot(bot)

    proactive = Thread(target=lambda: raise_proactive_bot(bot), daemon=True).start() #start allerts

    bot.polling()

    proactive.join()