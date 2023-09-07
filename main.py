from conf import TOKEN, GPT_TOKEN
from keybords import get_ikb, get_kb_start, get_ikb2, get_ikb3, get_kb_chat
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.filters import Text
from aiogram.utils import executor, markdown
from aiogram.types import ParseMode, BotCommand
import aiohttp
from aiogram import Bot, types


# Создание объекта aiohttp.ClientTimeout с необходимыми параметрами
timeout = aiohttp.ClientTimeout(total=10, connect=10, sock_read=10, sock_connect=10)

# Создание сессии aiohttp с установленным таймаутом
aiohttp_session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit_per_host=10), timeout=timeout)


import sqlity
import openai

from menu import set_main_menu

openai.api_key = GPT_TOKEN
storage = MemoryStorage()
bot = Bot(TOKEN, loop=aiohttp_session.loop)


class ProfileStatesGroup(StatesGroup):
    model = State()
    prompt = State()
    chat = State()
    info = State()
    generate = State()

dp = Dispatcher(bot, storage=storage)

async def on_startup(dp):
    await sqlity.db_start()
    await set_main_menu(bot)
    print('Подключение к БД выполнено успешно')


async def cmd_start(message: types.Message, state: FSMContext) -> None:

    async with state.proxy() as data:
        prof = await sqlity.get_profile(message.from_user.id,'profile')
        if not prof:
            await bot.send_message(
                chat_id=message.from_id,
                text='Добро пожаловать в бот! Чтобы создать чат с ChatGPT, введите /create',
                reply_markup=get_kb_start()
            )
        else:
            await message.answer('У вас уже существует чат. Для нового чата введите /reset или продолжите текущий чат.')


async def cmd_help(message: types.Message, state: FSMContext) -> None:
    text = ("Список команд:\n"
            "/start - Начало чата с ботом\n"
            "/create - Создание чата с ботом\n"
            "/reset - Удаление чата\n"
            "/profile - Информация о профиле\n"
            "/info - Информация о моделях и промптах")
    await message.answer(text, parse_mode=ParseMode.MARKDOWN)

async def cmd_info(message: types.Message, state: FSMContext) -> None:
    await  message.reply(
        text='О чем вы хотите узнать?',
        reply_markup=get_ikb3()
    )
    await ProfileStatesGroup.info.set()

async def get_info(message: types.Message, state: FSMContext) -> None:
    prof = await sqlity.get_profile(message.from_user.id,'profile')
    cash = await sqlity.get_profile(message.from_user.id,'cash_acc')
    if prof:
        await message.answer(
            f"Профиль {message.from_user.first_name}\n"
            f"Выбранная модель - {prof[1]}\n"
            f"Промпт для модели - {prof[2]}\n"
            f"Баланс: {round(cash[1], 5)}$ / 1$")
    else:
        if cash:
            await message.answer(
                f"У вас нету чатов, воспользуйтесь командой /create \n"
                f"Баланс: {round(cash[1],5)}$ / 1$")
        else:
            await message.answer(
                'У вас нету чат, если хотите создать введите /create')

        await ProfileStatesGroup.chat.set()


@dp.callback_query_handler(state=ProfileStatesGroup.info)
async def info(callback: types.CallbackQuery, state: FSMContext):

    if callback.data == 'Промт':
       await callback.message.delete()
       await bot.send_message(
            chat_id=callback.message.chat.id,
            text='Промпт (или промт) — это начальная фраза или текст, который вы предоставляете искусственному интеллекту, чтобы он мог на его основе генерировать ответы. Промпт играет роль ведущего вопроса или инструкции для модели, чтобы она поняла, какой тип ответа ожидается. В данном боте вы можете использовать следующие промпты:\n\n'
                '1. "Учитель" - для генерации ответов в роли учителя.\n'
                '2. "Помощник IT" - для генерации ответов в роли помощника.\n'
                '3. "Мудрый советчик" - для генерации советов в сфере психологии.\n'
                '4. "Эксперт русского языка" - для генерации ответов на вопросы о русском языке.'
        )
       await state.finish()
    elif callback.data == 'Модели':
        await callback.message.delete()
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text='Модель — это предварительно обученная нейронная сеть, способная генерировать текст на основе введенных данных. В данном боте доступны две модели:\n\n'
            '1. Модель "gpt-3.5-turbo" - это мощная модель для генерации текста с хорошим качеством ответов.\n'
            '2. Модель "text-davinci-003" - более компактная модель, специализированная на генерации текста с упором на конкретные запросы.'
            )
        await state.finish()
    else:
        await callback.message.delete()
        await state.finish()

async def cmd_create(message: types.Message, state: FSMContext) -> None:
    prof_cash = await sqlity.get_profile(message.from_user.id, 'cash_acc')
    if not prof_cash:
        await sqlity.insert_prof(message.from_id, 0.0000, 1.0000, 'cash_acc')
    prof = await sqlity.get_profile(message.from_user.id,'profile')
    if not prof:
        await state.update_data(id=message.from_user.id)
        await  message.reply(
            text='Выберите версию GPT, которую хотите использовать',
            reply_markup=get_ikb()
        )
        await ProfileStatesGroup.model.set()
    else:
        await message.answer(
            'У вас уже существует чат, если хотите создать новый введите /reset или можете продолжить чат')

        await ProfileStatesGroup.chat.set()

async def cmd_reset(message: types.Message, state: FSMContext) -> None:
    prof = await sqlity.get_profile(message.from_user.id, 'profile')
    if prof:
        await state.finish()
        await sqlity.del_prof(message.from_user.id)
        await bot.send_message(
            chat_id=message.from_id,
            text='Профиль успешно удалён, можете создать новый с помощью команды /create',
            reply_markup=get_kb_start()
        )
    else:
        await message.answer('Ошибка, у вас нету аккаунта')

def register_command(dp: Dispatcher):
    dp.register_message_handler(cmd_create, commands='create', state='*')
    dp.register_message_handler(cmd_start, commands='start', state='*')
    dp.register_message_handler(cmd_info, commands='info', state='*')
    dp.register_message_handler(get_info, commands='profile', state='*')
    dp.register_message_handler(cmd_help, commands='help', state='*')
    dp.register_message_handler(cmd_reset, commands='reset', state='*')



register_command(dp)

@dp.message_handler(Text(startswith='/'))
async def cmd_non(message: types.Message, state: FSMContext) -> None:
    await message.answer('Неизвестная команда попробуйте ввести /help')
    await ProfileStatesGroup.chat.set()

@dp.callback_query_handler(state=ProfileStatesGroup.model)
async def model_callback(callback: types.CallbackQuery, state: FSMContext):
    model_data = {
        'gpt-3.5-turbo': 'Модель gpt-3.5-turbo выбрана',
        'text-davinci-003': 'Модель text-davinci-003 выбрана'
    }
    if callback.data == 'text-davinci-003':
        await callback.message.answer(f'Напишите фразу или текст которую нужно продолжить')
        data = await state.get_data()
        await sqlity.insert_prof(data['id'], 'text-davinci-003', 'Non', 'profile')
        await ProfileStatesGroup.chat.set()
    elif callback.data in model_data:
        await callback.message.delete()
        await state.update_data(model=callback.data)
        await callback.message.answer(f'Вы выбрали модель {callback.data}')
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text='Выберите промпт, который хотите использовать',
            reply_markup=get_ikb2()
        )
        await ProfileStatesGroup.prompt.set()
    else:
        await callback.answer()
        await callback.message.delete()
        await state.finish()
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text='Добро пожаловать в бот! Чтобы создать чат с ChatGPT, введите /create',
            reply_markup=get_kb_start()
        )


@dp.callback_query_handler(state=ProfileStatesGroup.prompt)
async def model_callback(callback: types.CallbackQuery, state: FSMContext):
    prompt_data = {
        'Учитель': 'Учитель',
        'Помощник IT': 'Помощник IT',
        'Эксперт русского языка': 'Эксперт русского языка',
        'Мудрый советчик': 'Мудрый советчик'

    }
    if callback.data in prompt_data:
        await callback.message.delete()
        await state.update_data(prompt=callback.data)
        data = await state.get_data()
        user_id = data['id']
        await callback.message.answer(f'Вы выбрали промт {callback.data}')
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text='Можете начать чат',
            reply_markup=get_kb_chat()
        )
        await sqlity.insert_prof(user_id, data['model'], data['prompt'],'profile')
        content = await sqlity.get_prompt(data['prompt'])
        for i in range(len(content)):
            await sqlity.insert_his(user_id, content[i][1], content[i][0])
        await ProfileStatesGroup.chat.set()
    else:
        await callback.message.delete()
        await callback.answer()
        await state.finish()
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text='Добро пожаловать в бот! Чтобы создать чат с ChatGPT, введите /create',
            reply_markup=get_kb_start()
        )

@dp.message_handler(state=ProfileStatesGroup.chat)
async def chat_handler(message: types.Message, state: FSMContext):
    id = message.from_id
    msg = await bot.send_message(id, 'Запрос обрабатывается...')
    inf = await sqlity.get_profile(id,'profile')
    usage = await sqlity.get_profile(id,'cash_acc')
    if inf[1] == 'gpt-3.5-turbo' and usage[1] < 1 :
        await sqlity.insert_his(id, 'user', message.text)
        messages = await create_message(message.from_id)
        response = openai.ChatCompletion.create(
            model=inf[1],
            messages=messages
        )
        answer = response['choices'][0]['message']['content']
        await sqlity.insert_his(id, "system", answer)
        usage = response.usage
        amount = 0.0015*(usage['prompt_tokens']/1000) + 0.002*(usage['prompt_tokens']/1000)
        profile = await sqlity.get_profile(id,'cash_acc')
        await sqlity.update_usage(id,profile[1] + amount)
        await msg.edit_text(
        f"Ответ:\n"
        f"{answer}\n"
        f"Использовано: {round(amount,5)}$\n"
        f"Остаток: {round(profile[2]-(amount+profile[1]),5)}$")

    else:
        response = openai.Completion.create(
            model=inf[1],
            prompt=message.text,
            temperature = 1,
            max_tokens = 1000,
            top_p = 1,
            frequency_penalty = 0,
            presence_penalty = 0.6
        )
        answer = response['choices'][0]['text']
        usage = response.usage
        amount = 0.030 * (usage['prompt_tokens'] / 1000) + 0.12 * (usage['prompt_tokens'] / 1000)
        profile = await sqlity.get_profile(id, 'cash_acc')
        await sqlity.update_usage(id, profile[1] + amount)
        await sqlity.insert_his(id, 'promt', f'{message.text}{answer}')
        await msg.edit_text(
            f"Ответ:\n"
            f"{message.text} {answer}\n"
            f"Использовано: {round(amount,5)}$\n"
            f"Остаток: {profile[2]-(amount+profile[1])}$")

@dp.message_handler()
async def check_message(message: types.Message, state: FSMContext) -> None:
    prof = await sqlity.get_profile(message.from_user.id,'profile')
    if not prof:
        await message.answer('Добро пожаловать в бот! Чтобы создать чат с ChatGPT, введите /create')
    else:
        await ProfileStatesGroup.chat.set()
        await chat_handler(message, ProfileStatesGroup.chat)


async def create_message(id):
    message = []
    content = await sqlity.get_content(id)
    for i in range(len(content)):
        message.append({'role': content[i][0], 'content': content[i][1]})
    return message


def update(messages, role, content):
    messages.append({"role": role, "content": content})


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

