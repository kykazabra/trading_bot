from tg.ticker_update import get_ticker_users


def allert_buy_ticker(bot, ticker_sid):
    diag_ids = get_ticker_users(ticker_sid)
    text = f'Необходимо купить {ticker_sid}❕'
    for id in diag_ids:
        bot.send_message(id, text)


def allert_sell_ticker(bot, ticker_sid):
    diag_ids = get_ticker_users(ticker_sid)
    text = f'Необходимо продать {ticker_sid}❗'
    for id in diag_ids:
        bot.send_message(id, text)