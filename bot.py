import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
import re

# ==================================================
# НАСТРОЙКИ - ЗАМЕНИТЕ НА СВОИ ЗНАЧЕНИЯ!
# ==================================================
ACCESS_TOKEN = "vk.tokkkkk....."  # Ваш токен доступа (см. шаг 2)
GROUP_ID = 5555555            # ID сообщества (например, 123456789)

# ID администраторов (можно узнать через vk.com/dev)
ADMINS = []  # Например: [123456789, 987654321]

# ==================================================
# ИНИЦИАЛИЗАЦИЯ БОТА
# ==================================================
vk_session = vk_api.VkApi(token=ACCESS_TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)


def send_message(user_id, message, keyboard=None):
    """
    Отправляет сообщение пользователю
    """
    params = {
        "user_id": user_id,
        "message": message,
        "random_id": random.randint(1, 2**32)
    }
    if keyboard:
        params["keyboard"] = keyboard
    
    vk.messages.send(**params)


def create_main_keyboard():
    """
    Создаёт главную клавиатуру с кнопками меню
    """
    keyboard = {
        "one_time": False,
        "buttons": [
            [
                {"action": {"type": "text", "label": "🛡️ Проверь новость"}, "color": "primary"},
                {"action": {"type": "text", "label": "⚖️ Юридический кейс"}, "color": "primary"}
            ],
            [
                {"action": {"type": "text", "label": "📚 Твои права"}, "color": "secondary"},
                {"action": {"type": "text", "label": "🚫 Чего нельзя"}, "color": "negative"}
            ],
            [
                {"action": {"type": "text", "label": "❓ Помощь"}, "color": "secondary"}
            ]
        ]
    }
    return json.dumps(keyboard, ensure_ascii=False)


def create_quiz_keyboard(options):
    """
    Создаёт клавиатуру для теста с вариантами ответов
    """
    buttons = []
    row = []
    for i, option in enumerate(options):
        row.append({"action": {"type": "text", "label": option}, "color": "primary"})
        if len(row) == 2 or i == len(options) - 1:
            buttons.append(row)
            row = []
    
    keyboard = {"one_time": True, "buttons": buttons}
    return json.dumps(keyboard, ensure_ascii=False)


# ==================================================
# КОМАНДЫ И ОБРАБОТЧИКИ
# ==================================================

def handle_start(user_id):
    """Приветственное сообщение при старте"""
    welcome_text = """🛡️ *Добро пожаловать в «ЦифраЗащита»!*

Я бот-тренажёр, который поможет тебе научиться:
• ✅ Отличать достоверную информацию от фейков
• ✅ Распознавать фишинг и мошенничество
• ✅ Понимать свои права и обязанности в интернете
• ✅ Действовать правильно в опасных ситуациях

📌 *Как пользоваться:*
Просто нажимай на кнопки меню и выполняй задания!

Начнём с небольшого теста? Напиши *тест* или выбери раздел в меню."""
    
    send_message(user_id, welcome_text, create_main_keyboard())


def handle_fake_check(user_id):
    """Модуль «Проверь новость» — задание на распознавание фейка"""
    # База фейковых и реальных новостей
    news_items = [
        {
            "text": "СРОЧНО! В школах Москвы с 1 сентября отменяют домашние задания!",
            "is_fake": True,
            "explanation": "❌ Это ФЕЙК! Официальных заявлений об отмене домашних заданий не поступало. Признаки: эмоциональный заголовок «СРОЧНО», отсутствие ссылки на источник, слишком хорошая новость."
        },
        {
            "text": "ВКонтакте запускает новый формат коротких видео — «Клипы». Информация опубликована в официальном блоге VK.",
            "is_fake": False,
            "explanation": "✅ Это ПРАВДА. Информация подтверждена официальным источником."
        },
        {
            "text": "Внимание! Новый вирус в WhatsApp! Не открывайте сообщение с темой «Привет, это видео про тебя» — оно взламывает телефон!",
            "is_fake": True,
            "explanation": "❌ Это ФЕЙК! Такие сообщения — классический вирусный фейк, который кочует из года в год. WhatsApp не может взломать телефон просто от открытия сообщения."
        }
    ]
    
    # Выбираем случайную новость
    current_news = news_items[0]  # Для простоты берём первую
    
    question = f"📰 *Проверь новость*\n\n{current_news['text']}\n\nКак ты думаешь, это правда или фейк?"
    
    # Сохраняем состояние пользователя (в реальном проекте лучше использовать БД)
    # Здесь используем глобальный словарь для простоты
    user_states[user_id] = {"module": "fake_check", "news": current_news}
    
    keyboard = create_quiz_keyboard(["✅ Правда", "❌ Фейк"])
    send_message(user_id, question, keyboard)


def handle_fake_answer(user_id, answer):
    """Обрабатывает ответ пользователя на задание про фейк"""
    state = user_states.get(user_id, {})
    news = state.get("news", {})
    
    user_choice = "правда" if "правда" in answer.lower() else "фейк"
    is_correct = (user_choice == "фейк" and news.get("is_fake")) or (user_choice == "правда" and not news.get("is_fake"))
    
    if is_correct:
        response = f"✅ *Правильно!*\n\n{news.get('explanation', '')}\n\nОтличная работа! Хочешь попробовать ещё? Напиши «ещё» или выбери другой раздел."
    else:
        response = f"❌ *Неправильно!*\n\n{news.get('explanation', '')}\n\nНе расстраивайся! Запомни эти признаки фейка и попробуй снова. Напиши «ещё» или выбери другой раздел."
    
    send_message(user_id, response, create_main_keyboard())
    user_states.pop(user_id, None)


def handle_law_case(user_id):
    """Модуль «Юридический кейс» — правовая ситуация"""
    cases = [
        {
            "text": "Ты опубликовал в соцсети фото одноклассника без его согласия. Он обиделся и требует удалить фото. Кто прав?",
            "correct": "Одноклассник прав, так как публикация фото без согласия нарушает ст. 152.1 ГК РФ",
            "explanation": "⚖️ *Статья 152.1 ГК РФ*: «Обнародование и использование изображения гражданина допускаются только с согласия этого гражданина». Всегда спрашивай разрешение, прежде чем публиковать чужое фото!"
        },
        {
            "text": "Ты получил сообщение: «Ваш аккаунт ВК будет заблокирован, перейдите по ссылке и подтвердите пароль». Что делать?",
            "correct": "Не переходить по ссылке, это фишинг",
            "explanation": "🔒 *Фишинг* — вид мошенничества. Настоящая техподдержка никогда не просит пароль по ссылке. Игнорируй такие сообщения!"
        }
    ]
    
    current_case = cases[0]
    user_states[user_id] = {"module": "law_case", "case": current_case}
    
    question = f"⚖️ *Юридический кейс*\n\n{current_case['text']}\n\nЧто ты скажешь?"
    send_message(user_id, question, create_main_keyboard())


def handle_help(user_id):
    """Справка по командам"""
    help_text = """❓ *Справка по командам*

• 🛡️ *Проверь новость* — тренируйся распознавать фейки
• ⚖️ *Юридический кейс* — разбирай реальные правовые ситуации
• 📚 *Твои права* — узнавай о своих правах в интернете
• 🚫 *Чего нельзя* — что запрещено законом в сети

📝 *Текстовые команды:*
• Привет / Начать — показать меню
• Правила — список правил безопасности
• Тест — пройти проверку знаний
• Помощь — это сообщение

Бот создан в рамках проекта по медиаграмотности и правовой культуре."""
    
    send_message(user_id, help_text, create_main_keyboard())


def handle_rules(user_id):
    """Показывает правила безопасности"""
    rules = """📋 *20 правил цифровой безопасности*

🔧 *Технические правила:*
1️⃣ Используй сложные пароли (12+ символов)
2️⃣ Включи двухфакторную аутентификацию
3️⃣ Проверяй адрес сайта перед вводом пароля
4️⃣ Обновляй программы и антивирус
5️⃣ Не скачивай файлы с подозрительных сайтов

🧠 *Поведенческие правила:*
6️⃣ Проверяй новости в 3 источниках
7️⃣ Не публикуй личные данные в открытом доступе
8️⃣ Не общайся с навязчивыми незнакомцами
9️⃣ Делай скриншоты при кибербуллинге
🔟 Не распространяй непроверенную информацию

⚖️ *Правовые правила:*
11️⃣ Не публикуй чужие фото без согласия (ст. 152.1 ГК РФ)
12️⃣ Не распространяй личную информацию (ст. 137 УК РФ)
13️⃣ Не оскорбляй людей в сети (ст. 5.61 КоАП РФ)
14️⃣ Не распространяй фейки (ст. 207.3 УК РФ)
15️⃣ Соблюдай авторские права

Сохрани это сообщение! 🔥"""
    
    send_message(user_id, rules)


def handle_test(user_id):
    """Запускает тест на медиаграмотность"""
    questions = [
        {
            "text": "Что такое фишинг?",
            "options": ["Вид рыбной ловли", "Интернет-мошенничество для кражи паролей", "Антивирусная программа", "Правило цифровой гигиены"],
            "correct": 1
        },
        {
            "text": "Можно ли опубликовать фото друга без его согласия?",
            "options": ["Всегда можно", "Нельзя, это нарушает ст. 152.1 ГК РФ", "Можно, если фото красивое", "Можно, если друг не узнает"],
            "correct": 1
        },
        {
            "text": "Какой пароль самый надёжный?",
            "options": ["123456", "qwerty", "МойКотВася2024!", "password"],
            "correct": 2
        }
    ]
    
    # Сохраняем состояние теста
    user_states[user_id] = {"module": "test", "questions": questions, "current_q": 0, "score": 0}
    
    send_test_question(user_id)


def send_test_question(user_id):
    """Отправляет текущий вопрос теста"""
    state = user_states.get(user_id, {})
    questions = state.get("questions", [])
    current = state.get("current_q", 0)
    
    if current < len(questions):
        q = questions[current]
        text = f"📝 *Вопрос {current + 1} из {len(questions)}*\n\n{q['text']}"
        keyboard = create_quiz_keyboard(q['options'])
        send_message(user_id, text, keyboard)
    else:
        # Тест завершён
        score = state.get("score", 0)
        total = len(questions)
        percent = (score / total) * 100
        
        result = f"🎉 *Тест завершён!*\n\nТвой результат: {score} из {total} ({percent:.0f}%)\n\n"
        if percent >= 80:
            result += "Отлично! Ты хорошо разбираешься в цифровой безопасности! 🏆"
        elif percent >= 50:
            result += "Неплохо! Но есть куда расти. Пройди ещё раз, чтобы закрепить знания. 📚"
        else:
            result += "Стоит подтянуть знания! Попробуй прочитать правила безопасности и пройти тест снова. 💪"
        
        send_message(user_id, result, create_main_keyboard())
        user_states.pop(user_id, None)


def handle_test_answer(user_id, answer):
    """Обрабатывает ответ на вопрос теста"""
    state = user_states.get(user_id, {})
    questions = state.get("questions", [])
    current = state.get("current_q", 0)
    
    if current < len(questions):
        q = questions[current]
        # Находим выбранный вариант
        selected_idx = None
        for i, opt in enumerate(q['options']):
            if opt.lower() == answer.lower():
                selected_idx = i
                break
        
        if selected_idx == q['correct']:
            state["score"] = state.get("score", 0) + 1
            send_message(user_id, "✅ Верно!")
        else:
            correct_text = q['options'][q['correct']]
            send_message(user_id, f"❌ Неверно. Правильный ответ: {correct_text}")
        
        state["current_q"] = current + 1
        user_states[user_id] = state
        send_test_question(user_id)


# ==================================================
# ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ
# ==================================================
import json
user_states = {}  # Хранит состояния пользователей {user_id: {...}}


# ==================================================
# ОСНОВНОЙ ЦИКЛ БОТА
# ==================================================
def main():
    print("🤖 Бот запущен и ожидает сообщения...")
    
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.from_user:
                user_id = event.message['from_id']
                message_text = event.message['text'].lower().strip()
                
                print(f"📩 Сообщение от {user_id}: {message_text}")
                
                # Обработка команд
                if message_text in ["начать", "привет", "старт", "start"]:
                    handle_start(user_id)
                
                elif message_text in ["помощь", "help", "?"]:
                    handle_help(user_id)
                
                elif message_text in ["правила", "rules"]:
                    handle_rules(user_id)
                
                elif message_text in ["тест", "test"]:
                    handle_test(user_id)
                
                elif "проверь новость" in message_text or message_text == "🛡️ проверь новость":
                    handle_fake_check(user_id)
                
                elif "юридический кейс" in message_text or message_text == "⚖️ юридический кейс":
                    handle_law_case(user_id)
                
                elif "твои права" in message_text or message_text == "📚 твои права":
                    send_message(user_id, "📚 *Твои права в интернете*\n\n🔹 Право на неприкосновенность частной жизни\n🔹 Право на защиту персональных данных\n🔹 Право на свободу информации\n🔹 Право на судебную защиту\n\nПодробнее в разделе «Помощь» → Правила", create_main_keyboard())
                
                elif "чего нельзя" in message_text or message_text == "🚫 чего нельзя":
                    send_message(user_id, "🚫 *Чего нельзя делать в интернете*\n\n❌ Оскорблять людей\n❌ Публиковать чужие фото без согласия\n❌ Распространять фейки\n❌ Переходить по подозрительным ссылкам\n❌ Использовать простые пароли\n\nПодробнее в разделе «Помощь» → Правила", create_main_keyboard())
                
                elif message_text in ["ещё", "еще", "дальше"]:
                    # Продолжить последний модуль
                    state = user_states.get(user_id, {})
                    if state.get("module") == "fake_check":
                        handle_fake_check(user_id)
                    elif state.get("module") == "law_case":
                        handle_law_case(user_id)
                    else:
                        send_message(user_id, "Выбери раздел в меню, чтобы начать!", create_main_keyboard())
                
                # Обработка ответов на тест
                elif user_id in user_states and user_states[user_id].get("module") == "test":
                    handle_test_answer(user_id, event.message['text'])
                
                # Обработка ответов на проверку фейка
                elif user_id in user_states and user_states[user_id].get("module") == "fake_check":
                    handle_fake_answer(user_id, event.message['text'])
                
                else:
                    send_message(user_id, "Привет! Напиши *Помощь*, чтобы увидеть список команд, или нажми на кнопку в меню 💬", create_main_keyboard())


if __name__ == "__main__":
    main()