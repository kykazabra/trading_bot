from telebot import types
from env import Config
from tg.ticker_update import check_nd_add_user, \
    get_len_n_not_user_tickets, \
    get_len_n_user_tickets, \
    add_ticker_to_user, \
    remove_ticker_from_user, \
    get_user_tickers
import math


def create_page(buttons, page_idx, type_command='add'):
    keyboard = types.InlineKeyboardMarkup()

    for i in range(0, len(buttons), Config.BUTTONS_PER_ROW):
        keyboard.add(*[
            types.InlineKeyboardButton(text=buttons[j], callback_data=f'ticker_{type_command}_{page_idx}_{buttons[j]}')
            for j in range(i, min(i + Config.BUTTONS_PER_ROW, len(buttons)))]
        )
    return keyboard


def create_keyboard(data):
    splitted_data = data.split('_')

    idx, full_len, type_command, ticker_data = int(splitted_data[0]), \
                                               int(splitted_data[1]), \
                                               splitted_data[2], \
                                               splitted_data[3:]

    keyboard = create_page(ticker_data, idx, type_command)
    bottom_row = []

    if idx > 0:
        bottom_row.append(types.InlineKeyboardButton(text='<', callback_data=f'page_{type_command}_{idx - 1}'))

    bottom_row.append(types.InlineKeyboardButton(
        text=f'{idx + 1 if full_len > 0 else 0} / {max(1, math.ceil(full_len / Config.BUTTONS_PER_PAGE))}',
        callback_data=f' '
    ))

    if (idx + 1) * Config.BUTTONS_PER_PAGE < full_len:
        bottom_row.append(types.InlineKeyboardButton(text='>', callback_data=f'page_{type_command}_{idx + 1}'))

    keyboard.add(*bottom_row)

    return keyboard


def raise_reactive_bot(bot):
    @bot.message_handler(commands=['start'])
    def start_command(message):
        text = 'Привет!\nЯ бот - трейдер.\n\nВыбирай акции с помощью команды /add_ticker, а я буду следить за ними и ' \
               'сообщать, когда их лучше купить или продать!\n\nУдалить акцию ты можешь с помощью ' \
               '/drop_ticker.\n\nЧтобы посмотреть свой порфтель введите /my_portfolio '

        diag_id = check_nd_add_user(message.chat.id)

        bot.send_message(diag_id, text)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_query(call: types.CallbackQuery):
        if '_' in call.data:
            data_splitted = call.data.split('_')

            if data_splitted[0] == 'page':
                idx = int(data_splitted[-1])
                type_command = data_splitted[1]

            elif data_splitted[0] == 'ticker':
                if data_splitted[1] == 'add':
                    # TODO: check errors
                    add_ticker_to_user(data_splitted[-1], call.message.chat.id)
                    idx = int(data_splitted[2])
                    type_command = data_splitted[1]
                    #bot.answer_callback_query(call.id, f'Добавил {data_splitted[-1]}')
                    bot.send_message(call.message.chat.id, f'Добавил {data_splitted[-1]}!')
                    #call.message.delete()
                    bot.delete_message(call.message.chat.id, call.message.message_id)

                elif data_splitted[1] == 'del':
                    # TODO: check errors
                    remove_ticker_from_user(data_splitted[-1], call.message.chat.id)
                    idx = int(data_splitted[2])
                    type_command = data_splitted[1]
                    #bot.answer_callback_query(call.id, f'Удалил {data_splitted[-1]}')
                    bot.send_message(call.message.chat.id, f'Удалил {data_splitted[-1]}!')
                    #call.message.delete()
                    bot.delete_message(call.message.chat.id, call.message.message_id)

                else:
                    bot.answer_callback_query(call.id, f'IDK')

            # if type_command == 'add':
            #     full_len, tickers_data = get_len_n_not_user_tickets(idx * Config.BUTTONS_PER_PAGE,
            #                                                         Config.BUTTONS_PER_PAGE, call.message.chat.id)
            # elif type_command == 'del':
            #     full_len, tickers_data = get_len_n_user_tickets(idx * Config.BUTTONS_PER_PAGE, Config.BUTTONS_PER_PAGE,
            #                                                     call.message.chat.id)
            #
            # # full_len, tickers_data = 8, [f'SBER{idx}', f'BEBR{idx}']#, f'SER{idx}', f'LOH{idx}']
            # keyboard_data = '_'.join([str(idx), str(full_len), type_command] + tickers_data)
            #
            # try:
            #     bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
            #                                   reply_markup=create_keyboard(keyboard_data))
            # except:
            #     # Вылетает если ничего не поменялось
            #     pass
        else:
            bot.answer_callback_query(call.id, f'NOT BINDED: {call.data}')

    @bot.message_handler(commands=['add_ticker'])
    def add_ticker_command(message):
        text = 'Какую акцию из предложенных ты хочешь добавить?'
        # full_len, tickers_data = 8, [f'SBER0', f'BEBR0']#, f'SER{idx}', f'LOH{idx}']
        full_len, tickers_data = get_len_n_not_user_tickets(0, Config.BUTTONS_PER_PAGE, message.chat.id)

        keyboard_data = '_'.join(['0', str(full_len), 'add'] + tickers_data)

        bot.send_message(message.chat.id, text, reply_markup=create_keyboard(keyboard_data))

    @bot.message_handler(commands=['drop_ticker'])
    def add_ticker_command(message):
        text = 'Какую акцию из предложенных ты хочешь удалить?'
        # full_len, tickers_data = 8, [f'SBER0', f'BEBR0']#, f'SER{idx}', f'LOH{idx}']
        full_len, tickers_data = get_len_n_user_tickets(0, Config.BUTTONS_PER_PAGE, message.chat.id)
        keyboard_data = '_'.join(['0', str(full_len), 'del'] + tickers_data)
        bot.send_message(message.chat.id, text, reply_markup=create_keyboard(keyboard_data))

    @bot.message_handler(commands=['my_portfolio'])
    def my_portfolio_command(message: types.Message):
        tickers = "\n".join(get_user_tickers(message.from_user.id))
        bot.send_message(message.chat.id, f'Ваш портфель:\n{tickers}')