import logging

import aiogram.utils.markdown as md

from aiogram.utils.emoji import emojize
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.mongo import MongoStorage
from twitter import Twitter
from validations import is_auth_verifier
from conf.settings import TELEGRAM_TOKEN, MONGO_HOST, MONGO_PORT, MONGO_DB_NAME

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_TOKEN)
storage = MongoStorage(host=MONGO_HOST, port=MONGO_PORT, db_name=MONGO_DB_NAME)
dp = Dispatcher(bot, storage=storage)


# States
class Form(StatesGroup):
    credentials = State()
    targets = State()


@dp.message_handler(commands=['start', 'entrar'], state='*')
async def send_welcome(message: types.Message, state: FSMContext):
    """
    This handler will be called when user sends `/start` or `/entrar` command
    """

    initial_msg = (
        'Eu sou o Jovem Aprendiz, tô aqui pra te ajudar a '
        'monitorar perfis e realizar postagens no twitter.'
        'Por favor acesse o link abaixo para autorizar o acesso.'
        '\n\n Qualquer problema com o link só digitar /start novamente'
    )

    twitter = Twitter()
    credentials = twitter.login()

    auth_btn = types.InlineKeyboardButton(
        'Autorizar Twitter', url=credentials['auth_url'])
    reply_markup = types.InlineKeyboardMarkup(
        row_width=1).add(auth_btn)

    async with state.proxy() as data:
        data['credentials'] = credentials

        await bot.send_message(
            message.from_user.id,
            'Olá!'
        )

        await bot.send_message(
            message.from_user.id,
            initial_msg,
            reply_markup=reply_markup
        )

        await Form.credentials.set()
        await bot.send_message(
            message.from_user.id,
            'Ok, agora digite o código de confirmação de 7 dígitos: '
        )


@dp.message_handler(lambda message: not is_auth_verifier(message.text), state=Form.credentials)
async def get_wrong_login_code(message: types.Message):
    """
    If auth verifier is invalid
    """
    await bot.send_message(
        message.from_user.id,
        'Digite o código de confirmação, ele é composto de 7 dígitos: '
    )


@dp.message_handler(lambda message: is_auth_verifier(message.text), state=Form.credentials)
async def get_login_code(message: types.Message, state: FSMContext):
    """
    If auth verifier is valid
    Do the login and store twitter credentials
    """

    async with state.proxy() as data:
        oauth_token = data['credentials']['oauth_token']
        oauth_token_secret = data['credentials']['oauth_token_secret']

        print('Credentials: ', data['credentials'])
        twitter = Twitter(oauth_token=oauth_token,
                          oauth_token_secret=oauth_token_secret)
        twitter.confirm_login(message.text)
        user_info = twitter.get_user_info()
        resp_message = (
            'Oi {}!!!'.format(user_info['name'])
        )
        await bot.send_message(
            message.from_user.id,
            resp_message
        )

    # @dp.message_handler(commands=['start', 'twitter'], state='*')
    # async def send_welcome(message: types.Message):
    #     """
    #     This handler will be called when user sends `/start` or `/twitter` command
    #     """

    #     # Insert keyboard to user
    #     add_account_btn = types.InlineKeyboardButton(
    #         'Adicionar nova conta', callback_data='new_account')
    #     show_tweets_btn = types.InlineKeyboardButton(
    #         'Ver contas cadastradas', callback_data='accounts')
    #     reply_markup = types.InlineKeyboardMarkup(
    #         row_width=2).add(add_account_btn, show_tweets_btn)

    #     initial_msg = ('Olá!\n\n'
    #                    'Eu sou o Jovem Aprendiz, tô aqui pra te ajudar a '
    #                    'monitorar perfis e realizar postagens no twitter.'
    #                    '\n\nComo posso te ajudar?')

    #     await message.reply(
    #         initial_msg,
    #         reply_markup=reply_markup,
    #     )

    # @dp.message_handler(commands=['new'])


@dp.callback_query_handler(lambda c: c.data == 'new_account', state='*')
async def new_target(callback_query: types.CallbackQuery):
    """
    This handler will be called when user click
    to add new account or sends `/new`
    """
    # usr = User(callback_query.from.id)
    await Form.targets.set()
    await bot.send_message(
        callback_query.from_user.id,
        'Qual o @ do usuário que você deseja monitorar?'
    )


@dp.callback_query_handler(lambda c: c.data == 'accounts', state='*')
async def show_targets(callback_query: types.CallbackQuery, state: FSMContext):
    """
    This handler will be called when user click to show their accounts
    """
    # usr = User(callback_query.from.id)
    async with state.proxy() as data:
        if 'targets' not in data:
            await bot.send_message(
                callback_query.from_user.id,
                'Não existe nenhum usuário cadastrado')
            return

        user_list = list(map(
            lambda targ: targ['user'], data['targets']
        ))

        user_markdown = ''
        for user in user_list:
            user_markdown = user_markdown + '- @{}\n'.format(user)
        logging.info('User markdown:  %r',
                     user_markdown)
        await bot.send_message(
            callback_query.from_user.id,
            user_markdown
        )


@dp.message_handler(state=Form.targets)
async def process_name(message: types.Message, state: FSMContext):
    """
    Process username
    """

    async with state.proxy() as data:
        new_target = {'type': 'twitter',
                      'user': message.text}

        # If targets already exists, append the new target,
        # in other case, create the target list
        if 'targets' in data:
            if new_target not in data['targets']:
                data['targets'].append(new_target)
            else:
                await message.reply('Você já está monitorando esse usuário')
        else:
            data['targets'] = [new_target]

        await message.reply(
            md.text(
                emojize('Pode deixar, estaremos de :eyes: em'),
                md.bold('@{}'.format(message.text))
            ),
            parse_mode=types.ParseMode.MARKDOWN
        )
        logging.info('New target to user %r:  %r',
                     message.from_user.id, data['targets'])

        await state.finish()


@dp.message_handler()
async def echo(message: types.Message):
    await message.reply(message.text, reply=True)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
