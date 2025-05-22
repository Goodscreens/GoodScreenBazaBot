import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Получаем токен из переменных окружения
import os
TOKEN = os.environ.get("TOKEN", "YOUR_BOT_TOKEN")

# --- СЦЕНАРИЙ ИЗ ТВОЕГО .MD ФАЙЛА ---
SCENARIO = {
    'start': {
        'text': 'Это бот-инструкция для отдела продаж. Начнём?\n(Да/Нет)',
        'yes': 'step_1',
        'no': 'end'
    },
    'step_1': {
        'text': '1. Новый лид поступил в Bitrix?\n(Да/Нет)',
        'yes': 'step_1_yes',
        'no': 'step_1_no'
    },
    'step_1_yes': {
        'text': 'Менеджер принимает лид совершая звонок или отправляя письмо и вносит все данные в Bitrix\n2. Менеджер связался с клиентом?\n(Да/Нет)',
        'yes': 'step_2_yes',
        'no': 'step_2_no'
    },
    'step_1_no': {
        'text': 'Сообщить о сбое ответственному за интеграцию. Проверить форму на сайте/квизе.\nСценарий завершён.',
        'yes': 'end',
        'no': 'end'
    },
    # ... (остальные шаги здесь)
}

# --- ОБРАБОТЧИКИ ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['step'] = 'start'
    reply_markup = ReplyKeyboardMarkup([["Да", "Нет"]], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(SCENARIO['start']['text'], reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answer = update.message.text.lower()
    if user_answer not in ["да", "нет"]:
        await update.message.reply_text("Пожалуйста, выберите только 'Да' или 'Нет'")
        return

    current_step = context.user_data.get('step', 'start')
    next_step = SCENARIO[current_step]['yes'] if user_answer == 'да' else SCENARIO[current_step]['no']

    context.user_data['step'] = next_step
    reply_markup = ReplyKeyboardMarkup([["Да", "Нет"]], one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(SCENARIO[next_step]['text'], reply_markup=reply_markup)

# --- ЗАПУСК БОТА ---

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
