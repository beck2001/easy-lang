from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User

from mainApp.models import *

from telebot import TeleBot
from telebot import types
import random




# Объявление переменной бота
bot = TeleBot(settings.TELEGRAM_API_TOKEN, threaded=False)


# Название класса обязательно - "Command"
class Command(BaseCommand):
  	# Используется как описание команды обычно
    help = 'Just a command for launching a Telegram bot.'


    def handle(self, *args, **kwargs):
        bot.enable_save_next_step_handlers(delay=2) # Сохранение обработчиков
        bot.load_next_step_handlers()				# Загрузка обработчиков
        bot.remove_webhook()						# Удаление вебхука
        
        bot.polling(none_stop=True)					# Запуск бота
    
def get_kb():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text='/start'))
    keyboard.add(types.KeyboardButton(text='/changename'))
    keyboard.add(types.KeyboardButton(text='/changepassword'))
    return keyboard

@bot.message_handler(commands=['start'])
def start_message(message):

    tg_user = message.from_user
    # if firstname not set
    if tg_user.first_name is None:
        tg_user.first_name = tg_user.id
    # if lastname not set
    if tg_user.last_name is None:
        tg_user.last_name = 'Фамилия'

    user = User.objects.filter(tg_id=message.from_user.id).first()

    # get user profile image

    image = bot.get_user_profile_photos(tg_user.id, limit=1)
    if(len(image.photos) > 0):
        image = image.photos[0][0].file_id
        # get image file
        image_file = bot.get_file(image)
        # get image url
        image_url = bot.get_file_url(image_file.file_id)
        image = image_url
    else:
        image = "https://i.ytimg.com/vi/jYFk1O_t43A/maxresdefault.jpg"

    if user is None:
        
        pwd = ""
        for i in range(5):
            pwd += chr(random.randint(97, 122))
        user = User.objects.create_user(tg_id=tg_user.id, name=tg_user.first_name, surname=tg_user.last_name, img_url=image, password=pwd, is_active=True)
        user.save()
        bot.send_message(message.chat.id, 'Привет. Это бот EasyLang.\nВас зовут ' + str(tg_user.first_name) + ' ' + str(tg_user.last_name) + '\nВаш аккаунт зарегистрирован\nЛогин: ' + str(tg_user.id) + '\nПароль: ' + pwd, reply_markup=get_kb())
        return
    else:
        # change user image
        user.img_url = image
        user.save()
        bot.send_message(message.chat.id, 'Привет, ' + str(user.name) + ' ' + str(user.surname) + '\nВаш аккаунт уже зарегистрирован\nЛогин: ' + str(tg_user.id), reply_markup=get_kb())
        return

@bot.message_handler(commands=['changename'])
def change_name(message):
    bot.send_message(message.chat.id, 'Введите новое имя(Без фамилии)')
    bot.register_next_step_handler(message, change_name_step)

def change_name_step(message):
    user = User.objects.filter(tg_id=message.from_user.id).first()
    user.name = message.text
    user.save()
    bot.send_message(message.chat.id, 'Имя изменено\nВведите новую фамилию')
    bot.register_next_step_handler(message, change_surname_step)

def change_surname_step(message):

    user = User.objects.filter(tg_id=message.from_user.id).first()
    user.surname = message.text
    user.save()
    bot.send_message(message.chat.id, 'Фамилия изменена', reply_markup=get_kb())
    

@bot.message_handler(commands=['changepassword'])
def change_password(message):
    pwd = ""
    for i in range(5):
        pwd += chr(random.randint(97, 122))
    user = User.objects.filter(tg_id=message.from_user.id).first()
    user.set_password(pwd)
    user.save()
    bot.send_message(message.chat.id, 'Пароль изменен\nВаш новый пароль: ' + pwd, reply_markup=get_kb())
    return


