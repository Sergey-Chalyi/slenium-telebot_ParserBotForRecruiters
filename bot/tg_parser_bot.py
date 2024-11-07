import os
import telebot
from telebot import types
from work_au_parser import WorkUaParser
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')

if API_TOKEN is None:
    raise ValueError("API_TOKEN не знайден в .env файлі")

bot = telebot.TeleBot(API_TOKEN)

specialty = ""
location = ""
category = None
filters = {
    'search_params': [],
    'employment': [],
    'age': {},
    'gender': [],
    'salary': {},
    'education': [],
    'experience': []
}


@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("work.ua"), types.KeyboardButton("rabota.us"))
    bot.send_message(message.chat.id, "Оберіть сайт для парсингу даних:", reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text in ["work.ua", "rabota.us"])
def site_selection(message):
    site = message.text
    if site == "work.ua":
        msg = bot.send_message(message.chat.id, "Введіть спеціальність для пошуку (наприклад, Python developer):")
        bot.register_next_step_handler(msg, get_specialty)
    else:
        bot.send_message(message.chat.id, "Функціонал для rabota.us поки не реалізований.")


def get_specialty(message):
    global specialty
    specialty = message.text
    msg = bot.send_message(message.chat.id, "Введіть місто для пошуку (наприклад, Київ):")
    bot.register_next_step_handler(msg, get_location)


def get_location(message):
    global location
    location = message.text
    bot.send_message(message.chat.id, f"Спеціальність: {specialty}\nЛокація: {location}")
    bot.send_message(message.chat.id, "Тепер оберіть категорію для пошуку кандидатів.")
    send_category_options(message)


def send_category_options(message):
    categories_text = (
        "Будь ласка, оберіть категорію для пошуку кандидатів (вкажіть номер):\n\n"
        "1. IT, комп'ютери, інтернет\n"
        "2. Адміністрація, керівництво середньої ланки\n"
        "3. Будівництво, архітектура\n"
        "4. Бухгалтерія, аудит\n"
        "5. Готельно-ресторанний бізнес, туризм\n"
        "6. Дизайн, творчість\n"
        "7. ЗМІ, видавництво, поліграфія\n"
        "8. Краса, фітнес, спорт\n"
        "9. Культура, музика, шоу-бізнес\n"
        "10. Логістика, склад, ЗЕД\n"
        "11. Маркетинг, реклама, PR\n"
        "12. Медицина, фармацевтика\n"
        "13. Нерухомість\n"
        "14. Освіта, наука\n"
        "15. Охорона, безпека\n"
        "16. Продаж, закупівля\n"
        "17. Робочі спеціальності, виробництво\n"
        "18. Роздрібна торгівля\n"
        "19. Секретаріат, діловодство, АГВ\n"
        "20. Сільське господарство, агробізнес\n"
        "21. Страхування\n"
        "22. Сфера обслуговування\n"
        "23. Телекомунікації та зв'язок\n"
        "24. Топменеджмент, керівництво вищої ланки\n"
        "25. Транспорт, автобізнес\n"
        "26. Управління персоналом, HR\n"
        "27. Фінанси, банк\n"
        "28. Юриспруденція\n"
        "29. Інші сфери діяльності\n"
    )
    msg = bot.send_message(message.chat.id, categories_text)
    bot.register_next_step_handler(msg, set_category)


def set_category(message):
    global category
    try:
        category = int(message.text)
        if 1 <= category <= 29:
            bot.send_message(message.chat.id, f"Категорія встановлена: {category}")
            send_filter_options(message)
        else:
            bot.send_message(message.chat.id, "Будь ласка, оберіть номер категорії від 1 до 29.")
            send_category_options(message)
    except ValueError:
        bot.send_message(message.chat.id, "Будь ласка, введіть номер категорії.")
        send_category_options(message)


def send_filter_options(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton("Параметри пошуку"),
        types.KeyboardButton("Тип зайнятості"),
        types.KeyboardButton("Вік для пошуку")
    )
    keyboard.add(
        types.KeyboardButton("Стать для пошуку"),
        types.KeyboardButton("Зарплата"),
        types.KeyboardButton("Освіта")
    )
    keyboard.add(types.KeyboardButton("Застосувати фільтри"))
    bot.send_message(message.chat.id, "Оберіть категорію фільтрації:", reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == "Параметри пошуку")
def filter_search_params(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton("Пошук лише в заголовку"),
        types.KeyboardButton("Пошук з синонімами"),
        types.KeyboardButton("Пошук будь-яке з слів")
    )
    bot.send_message(message.chat.id, "Оберіть параметр пошуку:", reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == "Пошук лише в заголовку")
def set_title_only(message):
    filters['search_params'].append('title_only')
    bot.send_message(message.chat.id, "Пошук лише в заголовку увімкнено.")
    send_filter_options(message)


@bot.message_handler(func=lambda message: message.text == "Пошук з синонімами")
def set_with_synonyms(message):
    filters['search_params'].append('with_synonyms')
    bot.send_message(message.chat.id, "Пошук з синонімами увімкнено.")
    send_filter_options(message)


@bot.message_handler(func=lambda message: message.text == "Пошук будь-яке з слів")
def set_any_word(message):
    filters['search_params'].append('any_word')
    bot.send_message(message.chat.id, "Пошук будь-яке з слів увімкнено.")
    send_filter_options(message)


@bot.message_handler(func=lambda message: message.text == "Тип зайнятості")
def filter_employment_type(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton("Повна зайнятість"),
        types.KeyboardButton("Неповна зайнятість")
    )
    bot.send_message(message.chat.id, "Оберіть тип зайнятості:", reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == "Повна зайнятість")
def set_full_time(message):
    filters['employment'].append('full_time')
    bot.send_message(message.chat.id, "Повна зайнятість обрана.")
    send_filter_options(message)


@bot.message_handler(func=lambda message: message.text == "Неповна зайнятість")
def set_part_time(message):
    filters['employment'].append('part_time')
    bot.send_message(message.chat.id, "Неповна зайнятість обрана.")
    send_filter_options(message)


@bot.message_handler(func=lambda message: message.text == "Вік для пошуку")
def filter_age_range(message):
    msg = bot.send_message(message.chat.id, "Введіть мінімальний вік:")
    bot.register_next_step_handler(msg, set_min_age)


def set_min_age(message):
    try:
        filters['age']['from'] = int(message.text)
        msg = bot.send_message(message.chat.id, "Введіть максимальний вік:")
        bot.register_next_step_handler(msg, set_max_age)
    except ValueError:
        bot.send_message(message.chat.id, "Будь ласка, введіть числове значення.")


def set_max_age(message):
    try:
        filters['age']['to'] = int(message.text)
        bot.send_message(message.chat.id, f"Діапазон віку встановлений: {filters['age']['from']} - {filters['age']['to']}")
        send_filter_options(message)
    except ValueError:
        bot.send_message(message.chat.id, "Будь ласка, введіть числове значення.")


@bot.message_handler(func=lambda message: message.text == "Стать для пошуку")
def filter_gender(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Чоловіча"), types.KeyboardButton("Жіноча"))
    msg = bot.send_message(message.chat.id, "Оберіть стать:", reply_markup=keyboard)
    bot.register_next_step_handler(msg, set_gender)


def set_gender(message):
    gender = 'male' if message.text == "Чоловіча" else 'female'
    filters['gender'].append(gender)
    bot.send_message(message.chat.id, f"Стать обрана: {message.text}")
    send_filter_options(message)


@bot.message_handler(func=lambda message: message.text == "Зарплата")
def filter_salary(message):
    msg = bot.send_message(message.chat.id, "Введіть мінімальну зарплату:")
    bot.register_next_step_handler(msg, set_min_salary)


def set_min_salary(message):
    try:
        filters['salary']['from'] = int(message.text)
        msg = bot.send_message(message.chat.id, "Введіть максимальну зарплату:")
        bot.register_next_step_handler(msg, set_max_salary)
    except ValueError:
        bot.send_message(message.chat.id, "Будь ласка, введіть числове значення.")


def set_max_salary(message):
    try:
        filters['salary']['to'] = int(message.text)
        bot.send_message(message.chat.id, f"Діапазон зарплати встановлений: {filters['salary']['from']} - {filters['salary']['to']}")
        send_filter_options(message)
    except ValueError:
        bot.send_message(message.chat.id, "Будь ласка, введіть числове значення.")


@bot.message_handler(func=lambda message: message.text == "Освіта")
def filter_education(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Вища освіта"), types.KeyboardButton("Середня освіта"))
    msg = bot.send_message(message.chat.id, "Оберіть рівень освіти:", reply_markup=keyboard)
    bot.register_next_step_handler(msg, set_education)


def set_education(message):
    education_level = 'higher' if message.text == "Вища освіта" else 'secondary'
    filters['education'].append(education_level)
    bot.send_message(message.chat.id, f"Рівень освіти обраний: {message.text}")
    send_filter_options(message)


@bot.message_handler(content_types=['voice', 'audio', 'video'])
def unsupported_message(message):
    bot.send_message(message.chat.id, "Будь ласка, введіть текстове повідомлення.")


@bot.message_handler(func=lambda message: message.text == "Застосувати фільтри")
def apply_filters(message):
    bot.send_message(message.chat.id, "Застосовуємо фільтри та починаємо фільтрацію...")
    global category, specialty, location, filters
    try:
        with WorkUaParser() as parser:
            parser.select_category(category)
            parser.choose_profession(specialty)
            parser.choose_location(location)
            parser.apply_filters(filters)

            resumes = parser.get_resumes_from_pages()

        if resumes:
            for resume in resumes:
                bot.send_message(message.chat.id, f"Посилання: {resume.url}")
        else:
            bot.send_message(message.chat.id, "Не знайдено резюме по вказаним параметрам")
    except Exception as e:
        bot.send_message(message.chat.id, f"Відбулася помилка при парсингу: {e}")

bot.polling()
