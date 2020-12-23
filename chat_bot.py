import telebot
bot = telebot.TeleBot(token) #insert token from BotFather

import random

import pandas as pd
d = {'city': ['Москва','Санкт-Петербург'], 'сегодня': [-2, 1], 'завтра': [0,2]}
df = pd.DataFrame(data=d)
df.index = df['city']

from natasha import (Segmenter,
                     NewsEmbedding,
                     NewsMorphTagger,
                     NewsSyntaxParser,
                     Doc)
segmenter = Segmenter()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
syntax_parser = NewsSyntaxParser(emb)


import datetime
today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)

today = "month={}, day={}".format(today.month, today.day)
tomorrow = "month={}, day={}".format(tomorrow.month, tomorrow.day)

def get_city(text):
  msk = ["москв", "мск"]
  spb = ["петербур", "спб", "питер", "петроград"]
  text = text.lower()
  city = None
  for word in spb:
    for i in msk:
      if word in text and not i in text:
        city = "Санкт-Петербург"
      elif i in text and not word in text:
        city = "Москва"
  return city

def get_date(text):
  text = text.lower()
  doc = Doc(text)

  doc.segment(segmenter)
  doc.tag_morph(morph_tagger)
  doc.parse_syntax(syntax_parser)

  from natasha import MorphVocab
  morph_vocab = MorphVocab()

  from natasha import DatesExtractor
  dates_extractor = DatesExtractor(morph_vocab)

  if 'завтр' in text or tomorrow in str(list(dates_extractor(text))):
    return "завтра"
  elif 'сегодня' in text or 'сейчас' in text or today in str(list(dates_extractor(text))):
    return "сегодня"
  else:
    return None

def hello():
	hello = ['Привет! Хочешь узнать погоду?', "Рад тебя видеть! Спроси меня что-нибудь.", "Готов помочь тебе узнать погоду!", "Привет. Что хочешь узнать?"]
	return random.choice(hello)

def goodbye():
	goodbye = ['Пока!', "Приходи ко мне еще!", "Уже уходишь? :(", "Пока! Надеюсь, я тебе помог!"]
	return random.choice(goodbye)

def thanks():
	thanks = ['Обращайся!', "Не за что.", "Всегда пожалуйста!", "Надеюсь, я тебе помог!"]
	return random.choice(thanks) + ' Хочешь узнать что-то еще? Если нет, попрощайся со мной :)'

def undefined():
	undefined = ['Не понимаю тебя :(', "О чем ты?"]
	return random.choice(undefined) + " Для ответа мне нужно знать город и день. Пришли это в следующем письме, если не сложно."

def intent(text):
	text = text.lower()
	if get_city(text) is not None:
		city = get_city(text)
		if get_date(text) == 'завтра':
			return('Завтра в городе {} {}°С'.format(city, df['завтра'][city]))
		elif get_date(text) == 'сегодня':
			return('Сегодня в городе {} {}°С'.format(city, df['сегодня'][city]))
		else:
			return 'Я понял, что ты хочешь узнать погоду в городе {}. Пришли мне город и дату (сегодня или завтра), пожалуйста.'.format(city)

	for word in ['погод',"градус", "на улице"]:
		if word in text:
			return('Погода в каком городе тебя интересует: Москва или Санкт-Петербург?')

	for word in ['прив', 'здравствуй', 'добр']:
		if word in text:
			return hello()

	for word in ['пок', 'до свидан', 'спокойной', "увидимся"]:
		if word in text:
			return goodbye()

	for word in ["спасибо", "спс", "благодарю"]:
		if word in text:
			return thanks()

	return undefined()

@bot.message_handler(commands=['start'])
def welcome_start(message):
    bot.send_message(message.chat.id, 'Привет! Я вижу будущее!\nP.S. Только погоду, только в Москве и Санкт-Петербурге, только на сегодня и завтра :)\nПроверь меня.')
 
# Тут работаем с командой help
@bot.message_handler(commands=['help'])
def welcome_help(message):
    bot.send_message(message.chat.id, 'Пришли мне город (Москва или Санкт-Петербург) и день (сегодня или завтра), и я скажу тебе погоду.')

@bot.message_handler(content_types=['text'])
def get_messages(message):
	bot.send_message(message.from_user.id, intent(message.text))

# Запускаем постоянный опрос бота в Телеграме
bot.polling(none_stop=True, interval=0)
