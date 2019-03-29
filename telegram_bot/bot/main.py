import requests
import logging
from logging.handlers import RotatingFileHandler
from collections import defaultdict

import telebot

from pg_conn import pgConn


log_file = 'bot.log'
handlers = []
file_handler = logging.FileHandler(log_file)
rotate_handler = RotatingFileHandler(filename=log_file, maxBytes=1024,backupCount=1)
handlers.append(file_handler)
handlers.append(rotate_handler)

logging.basicConfig(
	level=logging.DEBUG,
	format="%(asctime)s %(levelname)s %(message)s",
	handlers=handlers
)

db = pgConn()


TOKEN = '621947128:AAF6O0J0VynvDb3Bi-AewMIig_RxVSA9yQI'
bot = telebot.TeleBot(TOKEN)

actions = ['add place', 'my list', 'reset']

ADD_START, ADD_NAME, ADD_PHOTO, ADD_LOCATION, ADD_CONFIRMATION, RELATIVE_LOCATION = range(6)
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
	bot.reply_to(message, 'Executed command has been stopped.')


@bot.message_handler(commands=['add'])
def handle_add_start(message):
	bot.reply_to(
		message,
		'Please, input a title of the place.'
	)
	update_state(message, ADD_NAME)


@bot.message_handler(func=lambda msg: get_state(msg) == ADD_NAME)
def handle_add_name(message):
	update_draft_place(
		message.chat.id, 'name', message.text)
	bot.reply_to(message, 'Please, load a photo of a place you want to add. (/stop to interrupt adding)')
	update_state(message, ADD_PHOTO)


@bot.message_handler(content_types=['photo'] ,func=lambda msg: get_state(msg) == ADD_PHOTO)
def handle_add_photo(message):
	file_info = bot.get_file(message.photo[-1].file_id)
	url = 'https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_info.file_path)
	downloaded_file = requests.get(url, stream=True)
	update_draft_place(message.chat.id, 'photo', downloaded_file.raw.read())
	bot.reply_to(message, 'Please, load your location.')
	update_state(message, ADD_LOCATION)


@bot.message_handler(content_types=['location'], func=lambda msg: get_state(msg) == ADD_LOCATION)
def handle_add_location(message):
	update_draft_place(
		message.chat.id, 'location',
		f'({message.location.latitude},'
		f' {message.location.longitude})'
	)
	bot.reply_to(message, 'Please, confirm the adding: yes/no')
	update_state(message, ADD_CONFIRMATION)


@bot.message_handler(func=lambda msg: get_state(msg) == ADD_CONFIRMATION)
def handle_add_confirmation(message):
	if 'yes' in message.text.lower():
		db.add_user_data(
			message.chat.id,
			draft_places[message.chat.id]['name'],
			draft_places[message.chat.id]['photo'],
			draft_places[message.chat.id]['location']
		)
		bot.reply_to(message, f'The place has been successfully stored.')
		update_state(message, ADD_START)
		del draft_places[message.chat.id]
	elif 'no' in message.text.lower():
		del draft_places[message.chat.id]
		bot.reply_to(message, 'Adding canceled.')
		update_state(message, ADD_START)


@bot.message_handler(commands=['list'])
def reply_places_list(message):
	bot.reply_to(message, 'Please, load your location.')
	update_state(message, RELATIVE_LOCATION)


@bot.message_handler(content_types=['location'], func=lambda msg: get_state(msg) == RELATIVE_LOCATION)
def reply_places_list(message):
	longitude_ = message.location.longitude
	latitude_ = message.location.latitude
	stored_places = db.get_user_list(message.chat.id, longitude_, latitude_)

	if not stored_places:
		bot.reply_to(message, 'There are no good places around 500 meters.')
		update_state(message, ADD_START)
	else:
		bot.reply_to(message, 'There are the closest places:')
		for place in stored_places:
			user_telegram_id, place_name, place_photo, place_location, ts, distance = place
			distance = int(distance)

			bot.reply_to(message, f'\n{place_name} / distance: {distance} meters')
			bot.send_photo(message.chat.id, bytes(place_photo))
			latitude, longitude,  = place_location[1:-1].split(',')
			bot.send_location(message.chat.id, longitude=longitude, latitude=latitude)
		update_state(message, ADD_START)


@bot.message_handler(commands=['reset'])
def reset_places(message):
	db.reset_user_data(message.chat.id)
	bot.reply_to(message, 'Your places have been deleted!')


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Save a place you would like to visit\nCommand list: /add, /list, /reset")


bot.polling()
