import telebot
from telebot import types
import os
from text2speech import TTS
import json
import time
from requests.exceptions import ReadTimeout


with open('config.json', 'r') as f:
    config = json.load(f)
API_TOKEN = config.get('bot_token')

bot = telebot.TeleBot(API_TOKEN)
models = {"Нурай": TTS("Нурай", 48), "Нурбек": TTS("Нурбек", 48)}
user_choices = {}
#"Клара": TTS("Клара", 47), "Жолдошбек": TTS("Жолдошбек", 48)
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for i in models:
        markup.add(types.KeyboardButton(i))
    bot.send_message(message.chat.id, "Саламатсызбы! Бул бот кызматы сизге санарип текстти үнгө айландырууга жардам берет.  \n Алгач төмөнкү үндөрдөн бирөөнү тандаңыз.", reply_markup=markup)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text(message):
    if message.text in models:
        user_id = message.from_user.id
        user_choices[user_id] = message.text
        text = f"Сиздин тандооңуз: {message.text}"
        bot.send_message(message.chat.id, text)
        bot.send_message(message.chat.id, "Эми, текст жазып, жибериңиз.  \n")
    else:
        bot.send_message(message.chat.id, "Күтө туруңуз, аудио дайындалып жатат. \n")
        user_id = message.from_user.id
        selected_option = user_choices.get(user_id, "Тандоо жок")
        audio_text = f"Сиздин тандооңуз: {selected_option}"
        if selected_option == "Тандоо жок":
            selected_option = "Нурай"
        model = models[selected_option]
        audio_file_path=""
        try:
            audio_file_path = model.convert(message.text) + ".mp3"
        except ReadTimeout:  # Обрабатываем исключение ReadTimeout
            bot.send_message(message.chat.id, "Кечиресиз, Суроо көпкө созулду. Сураныч, кайра аракет кылыңыз.")
        except Exception as e:
            bot.send_message(message.chat.id, "Аудио иштеп жатканда ката кетти. Кайра аракет кылып көрүңүз же администраторуңузга кайрылыңыз.")
        if os.path.exists(audio_file_path):
            with open(audio_file_path, 'rb') as audio_file:
                audio_data = audio_file.read()
                bot.send_audio(message.chat.id, audio_data, caption=audio_text)
        else:
            bot.send_message(message.chat.id, "Аудио файл табылган жок.")

if __name__ == "__main__":
    bot.infinity_polling(timeout=100, long_polling_timeout = 5)
    #bot.polling(none_stop=True)

