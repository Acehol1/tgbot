from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from conf import TOKEN, GPT_TOKEN
import openai

openai.api_key = GPT_TOKEN
HELP_COMMAND = """
<b>/help</b> - <em>список комманд</em>
<b>/start</b> - <em>начать работу с ботом</em>
"""
bot = Bot(TOKEN)
dp = Dispatcher(bot)
all_messages = [{"role": "system", "content": "Вы человек который все время пишет транслитом, после этого сообщения пиши "
                                          "только английскими буквами, но произношение русское "},
                {"role": "user", "content": "Привет"},
                {"role": "assistant", "content": "Nice to meet you"}]
kb = ReplyKeyboardMarkup(resize_keyboard=True)
kb.add(KeyboardButton('/help'))


@dp.message_handler(commands=['start'])
async def help_command(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text='Добро пожаловать в бот',
                           parse_mode='HTML',
                           reply_markup=kb)
    await message.delete()


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text=HELP_COMMAND,
                           parse_mode='HTML',
                           reply_markup=ReplyKeyboardRemove())
    await message.delete()


def update_messages(messages, role, content):
    messages.append({"role": role, "content": content})
    return messages


@dp.message_handler()
async def get_response(message: types.Message):
    messages = update_messages(all_messages, 'user', f'Меня зовут{message.from_user.first_name}')
    messages = update_messages(messages, 'user', message.text)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    print(message.text, message.from_user.first_name, message.from_user.last_name)
    await message.answer(response['choices'][0]['message']['content'])


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
