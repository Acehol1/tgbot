from aiogram.types import KeyboardButton, InlineKeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup

def get_kb_start() -> ReplyKeyboardMarkup:

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('/create'))
    kb.add(KeyboardButton('/profile'))
    kb.add(KeyboardButton('/help'))
    kb.add(KeyboardButton('/info'))
    return kb

def get_kb_chat() -> ReplyKeyboardMarkup:

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('/reset'))
    kb.add(KeyboardButton('/profile'))
    kb.add(KeyboardButton('/help'))
    return kb
def get_ikb() -> InlineKeyboardMarkup:

    ikb = InlineKeyboardMarkup(row_width=2)
    ikb.add(InlineKeyboardButton(text='gpt-3.5-turbo',callback_data="gpt-3.5-turbo"),
            InlineKeyboardButton(text='text-davinci-003',callback_data="text-davinci-003")).add(InlineKeyboardButton(text='<--',callback_data="<--"))
    return ikb
def get_ikb2() -> InlineKeyboardMarkup:

    ikb = InlineKeyboardMarkup(row_width=3)
    ikb.add(InlineKeyboardButton(text='Учитель',callback_data="Учитель"),
            InlineKeyboardButton(text='Помощник IT',callback_data="Помощник IT"),
            InlineKeyboardButton(text='Мудрый советчик',callback_data="Мудрый советчик")
    ).add(InlineKeyboardButton(text='Эксперт русского языка', callback_data="Эксперт русского языка")
    ).add(InlineKeyboardButton(text='<--',callback_data="<--"))
    return ikb
def get_ikb3() -> InlineKeyboardMarkup:

    ikb = InlineKeyboardMarkup(row_width=3)
    ikb.add(InlineKeyboardButton(text='Промт',callback_data="Промт"),
            InlineKeyboardButton(text='Модели',callback_data="Модели")).add(InlineKeyboardButton(text='<--',callback_data="<--"))
    return ikb
