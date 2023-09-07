from aiogram import Bot
from aiogram.types import BotCommand


async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/help',
                   description='Справка по работе бота'),
        BotCommand(command='/info',
                   description='Информация о боте'),
        BotCommand(command='/create',
                   description='Создание чата'),
        BotCommand(command='/profile',
                   description='Информация о профиле'),
        BotCommand(command='/reset',
                   description='Удаление чата')]

    await bot.set_my_commands(main_menu_commands)
