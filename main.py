import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Структура взаимодействия
flow = {
    'Сценарий работы Отел продаж': {
        '1. Новый лид поступил в Bitrix?': {
            'Да': {
                'description': 'Менеджер принимает лид совершая звонок или отправляя письмо и вносит все данные в Bitrix',
                'next': '2. Менеджер связался с клиентом?',
            },
            'Нет': {
                'description':
                    'Сообщить о сбое ответственному за интеграцию. Проверить форму на сайте/квизе.',
            },
        },
        '2. Менеджер связался с клиентом?': {
            'Да': {
                'description':
                    'Уточнить ТЗ клиента и внести все данные в карточку лида, переместив его.',
                'next': '3. ТЗ клиента уточнено?',
            },
            'Нет': {
                'description':
                    'Вручную назначить ответственного. Уведомить руководителя.',
            },
        },
        # Добавляем остальные шаги аналогично...
    }
}

# Глобальная переменная для хранения состояния каждого пользователя
user_states = {}

def start(update: Update, context: CallbackContext):
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    user_states[user_id] = {'current_node': 'Сценарий работы Отел продаж'}
    send_current_question(update, context)

def send_current_question(update: Update, context: CallbackContext):
    """Отправляет текущий вопрос пользователю"""
    user_id = update.effective_user.id
    current_node = user_states[user_id]['current_node']
    node_data = flow[current_node]

    if isinstance(node_data, dict):
        question = list(node_data.keys())[0]
        update.message.reply_text(question)
    else:
        update.message.reply_text("Конец сценария.")

def handle_response(update: Update, context: CallbackContext):
    """Обрабатывает ответ пользователя"""
    user_id = update.effective_user.id
    response = update.message.text.strip().capitalize()

    if user_id not in user_states:
        update.message.reply_text("Вы не начали сценарий. Напишите /start.")
        return

    current_node = user_states[user_id]['current_node']
    node_data = flow[current_node]

    if isinstance(node_data, dict):
        question = list(node_data.keys())[0]
        options = node_data[question]

        if response in options:
            next_step = options[response]

            if 'next' in next_step:
                user_states[user_id]['current_node'] = next_step['next']
                send_current_question(update, context)
            else:
                update.message.reply_text(next_step['description'])
                del user_states[user_id]  # Сброс состояния после завершения
        else:
            update.message.reply_text("Выберите 'Да' или 'Нет'.")
    else:
        update.message.reply_text("Ошибка в состоянии. Начните заново с /start.")

def main():
    """Основная функция для запуска бота"""
    # Замените 'YOUR_TELEGRAM_BOT_TOKEN' на токен вашего бота
    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN", use_context=True)

    dp = updater.dispatcher

    # Обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_response))

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
