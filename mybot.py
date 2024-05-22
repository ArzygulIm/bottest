import telebot
from telebot import types
import urllib.parse
import requests
import users
import json


class Page:
    def __init__(self, page=''):
        self.page = page

    def get_page(self):
        return self.page

    def set_page(self, new_page):
        self.page = new_page


class SelectedCity:
    def __init__(self, city=''):
        self.city = city

    def get_city(self):
        return self.city

    def set_city(self, new_city):
        self.city = new_city


class PrevMessage:
    def __init__(self, mess=''):
        self.mess = mess

    def get_mess(self):
        return self.mess

    def set_mess(self, new_mess):
        self.mess = new_mess


class BotMess:
    def __init__(self, mess=''):
        self.mess = mess

    def get_message(self):
        return self.mess

    def set_message(self, new_mess):
        self.mess = new_mess


user_states = {}


def is_authorized(id):
    with open('users.json') as f:
        users_from_db = json.load(f)
        for i in users_from_db:
            if i['id'] == id or i['number'] == id:
                return True
    return False


def get_user_info(id):
    with open('users.json') as f:
        users_from_db = json.load(f)
        for i in users_from_db:
            if i['id'] == id:
                return i


def get_city_info(city):
    try:
        with open('cities.json', 'r', encoding='utf-8') as f:
            cities_from_db = json.load(f)
            for i in cities_from_db:
                if 'name' in i and 'attractions' in i and 'hotels' in i:
                    if city.lower() in i['name'].lower():
                        return i
                    for attraction in i['attractions']:
                        if city.lower() in attraction['name'].lower():
                            return i
                    for hotel in i['hotels']:
                        if city.lower() in hotel['name'].lower():
                            return i
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Ошибка при чтении файла: {e}")
    except AttributeError as e:
        print(f"Ошибка при обработке данных: {e}")
    return 'Не удалось найти такого города в нашей базе данных'


bot = telebot.TeleBot('6884410705:AAHiels3a_1m3dcpOvJ8i5HaIr0HwBdlvp4')
GOOGLE_MAPS_API_KEY = 'AIzaSyCAfh0trHPrlTpPcRYIdomOuxo9eIR6aYk'
phone_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
phone_markup.add(types.KeyboardButton(text="Отправить номер телефона", request_contact=True))

main_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn_main = types.KeyboardButton('Главная страница', request_contact=False, request_location=False)
btn_biography = types.KeyboardButton('Биография Достопримечательности', request_contact=False, request_location=False)
btn_put = types.KeyboardButton('Проложить путь', request_contact=False, request_location=False)
btn_feedback = types.KeyboardButton('Обратная связь', request_contact=False, request_location=False)
main_menu_markup.add(btn_main, btn_biography, btn_put, btn_feedback)

go_to_main_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
go_to_main_markup.add(btn_main)

main_put_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_put_markup.add(btn_main, btn_put)


def check_and_delete(message):
    user_id = message.from_user.id
    if user_id not in user_states:
        user_states[user_id] = {'selected_city': SelectedCity(), 'page': Page(), 'prev_mess': PrevMessage(),
                                'bot_mess': BotMess()}

    prev_message = user_states[user_id]['prev_mess'].get_mess()
    current_message_text = message.text or (message.contact and message.contact.phone_number)

    if prev_message == current_message_text:
        bot.delete_message(message.chat.id, message.message_id)
    else:
        user_states[user_id]['prev_mess'].set_mess(current_message_text)

def send_unique_message(chat_id, text, reply_markup=None):
    user_id = chat_id
    if user_id not in user_states:
        user_states[user_id] = {'selected_city': SelectedCity(), 'page': Page(), 'prev_mess': PrevMessage()}

    prev_message = user_states[user_id]['prev_mess'].get_mess()

    if prev_message != text:
        bot.send_message(chat_id, text, reply_markup=reply_markup)
        user_states[user_id]['prev_mess'].set_mess(text)

def send_unique_message_with_html(chat_id, text, parse_mode=None, reply_markup=None):
    user_id = chat_id
    if user_id not in user_states:
        user_states[user_id] = {'selected_city': SelectedCity(), 'page': Page(), 'prev_mess': PrevMessage()}

    prev_message = user_states[user_id]['prev_mess'].get_mess()

    if prev_message != text:
        bot.send_message(chat_id, text, parse_mode=parse_mode, reply_markup=reply_markup)
        user_states[user_id]['prev_mess'].set_mess(text)


@bot.message_handler(commands=['start'])
def start(message):
    double = check_and_delete(message)
    if double == True:
        return True
    send_unique_message(message.chat.id, 'Привет! Для авторизации отправьте свой номер телефона.',
                     reply_markup=phone_markup)


@bot.message_handler(content_types=['contact'])
def get_contact(message):
    check_and_delete(message)
    if is_authorized(message.contact.phone_number):
        user_states[message.from_user.id] = {'selected_city': SelectedCity(), 'page': Page(),
                                             'prev_mess': PrevMessage()}
        send_unique_message(message.chat.id, f'Привет, {message.from_user.first_name}', reply_markup=main_menu_markup)
    else:
        if message.from_user and message.from_user.first_name and message.contact and message.contact.phone_number and message.from_user.id:
            user_name = message.from_user.first_name
            user_number = message.contact.phone_number
            user_id = message.from_user.id
            user = users.User(user_number, user_name, user_id)
            db = users.UserDatabase()
            db.add_user(user)
            if is_authorized(user_id):
                user_states[message.from_user.id] = {'selected_city': SelectedCity(), 'page': Page(),
                                                     'prev_mess': PrevMessage()}
                send_unique_message(message.chat.id, 'Вы успешно авторизованы.', reply_markup=main_menu_markup)
            else:
                send_unique_message(message.chat.id, 'Вы не авторизованы. Попробуйте еще раз.', reply_markup=phone_markup)


@bot.message_handler(func=lambda message: message.text == 'Главная страница')
def main_page(message):
    check_and_delete(message)
    if message.from_user and message.from_user.id:
        user_id = message.from_user.id
        if user_id not in user_states:
            user_states[message.from_user.id] = {'selected_city': SelectedCity(), 'page': Page(),
                                                 'prev_mess': PrevMessage()}
        flag = is_authorized(message.from_user.id)
        if flag:
            html_message = """
            <b>Главная страница</b>
            \nДобро пожаловать в вашего личного экскурсовода!
            \nЗдесь вы найдете всю необходимую информацию о достопримечательностях, сможете проложить маршрут и оставить свои отзывы. Выберите один из разделов ниже, чтобы начать ваше путешествие:
            \n<b>Биография Достопримечательности:</b> Узнайте больше о знаменитых местах, их истории и интересных фактах.
            \n<b>Проложить путь:</b> Найдите оптимальный маршрут к выбранной достопримечательности с помощью нашей удобной навигации.
            \n<b>Обратная связь:</b> Поделитесь своими впечатлениями и предложениями для улучшения нашего сервиса.
            """
            send_unique_message_with_html(message.chat.id, html_message, parse_mode='HTML', reply_markup=main_menu_markup)


@bot.message_handler(func=lambda message: message.text == 'Биография Достопримечательности')
def biografy(message):
    check_and_delete(message)
    user_id = message.from_user.id
    if user_id not in user_states:
        user_states[message.from_user.id] = {'selected_city': SelectedCity(), 'page': Page()}
    user_states[user_id]['page'].set_page('Биография Достопримечательности')
    send_unique_message(message.chat.id, 'Пишите имя города', reply_markup=go_to_main_markup)



def get_2gis_link(city_name, zoom=12):
    encoded_city_name = urllib.parse.quote_plus(city_name)
    link = f"https://2gis.ru/?m={zoom}&q={encoded_city_name}"
    return link


@bot.message_handler(func=lambda message: message.text == 'Проложить путь')
def put(message):
    check_and_delete(message)
    user_id = message.from_user.id
    if user_id in user_states:
        user_states[user_id]['page'].set_page('Проложить путь')
        city_info = user_states[user_id]['selected_city'].get_city()
        if city_info and 'name' in city_info:
            city_name = city_info['name']
            zoom = 12
            link = get_2gis_link(city_name, zoom)
            send_unique_message(message.chat.id, f"Нажмите на ссылку для навигации: {link}")
        else:
            send_unique_message(message.chat.id, "Информация о городе не найдена.")
    else:
        send_unique_message(message.chat.id, "Информация о городе недоступна.")


@bot.message_handler(func=lambda message: message.text == 'Обратная связь')
def feedback(message):
    check_and_delete(message)
    user_id = message.from_user.id
    if user_id in user_states:
        user_states[user_id]['page'].set_page('Обратная связь')
        send_unique_message(message.chat.id, "Отправьте сообщение для обратной связи")


@bot.message_handler()
def get_user(message):
    check_and_delete(message)
    user_id = message.from_user.id
    if user_id in user_states:
        if user_states[user_id]['page'].get_page() == 'Биография Достопримечательности':
            city = get_city_info(message.text)
            if city == 'Не удалось найти такого города в нашей базе данных':
                send_unique_message(message.chat.id, city, reply_markup=go_to_main_markup)
            else:
                attr_text = ''
                if 'attractions' in city:
                    for j in city['attractions']:
                        attr_text += f"\n\n\t<b>{j['name']}</b>\n\t{j['attraction_info']}"

                hotels_text = ''
                if 'hotels' in city:
                    for j in city['hotels']:
                        hotels_text += f"\n\n\t<b>{j['name']}</b>\n\t{j['hotel_info']}\n\tЦены начинаются от: {j['prices_from']}\n\tСпециально для наших клиентов {j['sales']}"
                if 'name' in city:
                    city_info = {
                        'name': city['name'],
                        'lat': city['map_data']['lat'],
                        'lon': city['map_data']['lon']
                    }
                    user_states[user_id]['selected_city'].set_city(city_info)
                    html_message = f'<b>{city["name"]}</b>\n\nГлавные достопримечательности{attr_text}\n\nОтели{hotels_text}'
                    print(user_states[user_id]['selected_city'].get_city())
                    send_unique_message(message.chat.id, html_message, parse_mode='HTML', reply_markup=main_put_markup)
        # elif user_states[user_id]['page'].get_page() == 'Обратная связь':
        #     server_url = "http://your_1c_server_address:port"
        #     api_route = "/api/obработка_запроса"
        #     user_info = get_user_info(user_id)
        #     message = {
        #         "from": user_info,
        #         "body": message.text
        #     }
        #
        #     try:
        #         response = requests.post(f"{server_url}{api_route}", json=message)
        #         response.raise_for_status()
        #         print("Сообщение успешно отправлено на сервер 1С.")
        #         print("Ответ сервера 1С:")
        #         print(response.json())
        #     except requests.exceptions.RequestException as e:
        #         print("Произошла ошибка при отправке сообщения на сервер 1С:", str(e))


bot.polling(none_stop=True)
