from collections import defaultdict

import telebot


# db

def read_conf():
    config = configparser.ConfigParser()
    config.read('.env')
    return config




# bot
TOKEN = '621947128:AAF6O0J0VynvDb3Bi-AewMIig_RxVSA9yQI'
bot = telebot.TeleBot(TOKEN)

actions = ['add place', 'my list', 'reset']

ADD_START, ADD_PHOTO, ADD_LOCATION, ADD_CONFIRMATION = range(4)
user_state = defaultdict(lambda:ADD_START)
draft_places = defaultdict(lambda: {})


def get_state(message):
	return user_state[message.chat.id]


def update_state(message, state):
	user_state[message.chat.id] = state


def get_draft_place(user_id):
	return draft_places[user_id]


def update_draft_place(user_id, key, value):
	draft_places[user_id][key] = value


@bot.message_handler(commands=['stop'])
def handle_stop(message):
	update_state(message, ADD_START)
	bot.reply_to(message, 'Adding has been stopped.')


@bot.message_handler(commands=['add'])
def handle_add_start(message):
	bot.reply_to(
		message,
		'Please, load a photo of a place you want to add. (/stop to interrupt adding)'
	)
	update_state(message, ADD_PHOTO)


@bot.message_handler(content_types=['photo'] ,func=lambda msg: get_state(msg) == ADD_PHOTO)
def handle_add_photo(message):
	update_draft_place(message.chat.id, 'photo', message.photo)
	bot.reply_to(message, 'Please, load your location.')
	update_state(message, ADD_LOCATION)


@bot.message_handler(content_types=['location'], func=lambda msg: get_state(msg) == ADD_LOCATION)
def handle_add_location(message):
	update_draft_place(message.chat.id, 'location', message.location)
	bot.reply_to(message, 'Please, confirm the adding: yes/no')
	update_state(message, ADD_CONFIRMATION)


@bot.message_handler(func=lambda msg: get_state(msg) == ADD_CONFIRMATION)
def handle_add_confirmation(message):
	if 'yes' in message.text.lower():
		bot.reply_to(message, f'{draft_places[message.chat.id]} has been stored')
		update_state(message, ADD_START)
	elif 'no' in message.text.lower():
		del draft_places[message.chat.id]
		bot.reply_to(message, 'Adding canceled.')
		update_state(message, ADD_START)


@bot.message_handler(commands=['list'])
def reply_places_list(message):
	bot.reply_to(message, 'here will be a list of top closest places')


@bot.message_handler(commands=['reset'])
def reset_places(message):
	bot.reply_to(message, 'Your places have been deleted')


def create_inline_keyboard():
	keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
	buttons = [telebot.types.InlineKeyboardButton(
		text=action,
		callback_data=action) for action in actions[:2]
	]
	keyboard.add(*buttons)
	return keyboard


@bot.callback_query_handler(func=lambda x: x.data == 'add place')
def add_callback_handler(callback_query):
	print(callback_query.message)


@bot.callback_query_handler(func=lambda x: x.data == 'my list')
def add_callback_handler(callback_query):
	bot.answer_callback_query(callback_query.id, 'here wil be list of your favorite places')


@bot.callback_query_handler(func=lambda x: x.data == 'reset')
def add_callback_handler(callback_query):
	print('delete my stored data')


@bot.message_handler(commands=['start'])
def send_welcome(message):
	keyboard = create_inline_keyboard()
	bot.reply_to(message, "Save a place you would like to visit", reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def send_help(message):
	bot.reply_to(message, "Command list: /add, /list, /reset")


bot.polling()
