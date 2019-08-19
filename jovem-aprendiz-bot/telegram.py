import logging
from aiogram import Bot, Dispatcher, executor, types
from conf.settings import TELEGRAM_TOKEN

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'twitter'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/twitter` command
    """

    # Insert keyboard to user
    add_account_btn = types.InlineKeyboardButton('Adicionar nova conta', url='https://github.com/perifa-io')
    show_tweets_btn = types.InlineKeyboardButton('Ver tweets recentes', url='https://github.com/perifa-io')
    reply_markup = types.InlineKeyboardMarkup(row_width=2).add(add_account_btn, show_tweets_btn)


    await message.reply(
        "Olá! Eu sou o Jovem Aprendiz, tô aqui pra te ajudar a monitorar perfis e realizar postagens.\nComo posso te ajudar?",
        reply_markup=reply_markup,
    )


@dp.message_handler()
async def echo(message: types.Message):
    await message.reply(message.text, reply=True)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
