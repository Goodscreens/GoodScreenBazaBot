import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

import os
TOKEN = os.environ["TOKEN"]
  # Сюда вставь свой токен

# Простой сценарий: вопросы и развилки Да/Нет
SCENARIO = {
    "start": {
        "text": "Это бот-инструкция для отдела продаж. Начнём?\n(Да/Нет)",
        "yes": "step1",
        "no": "end"
    },
    "step1": {
        "text": "Вы уже позвонили клиенту?\n(Да/Нет)",
        "yes": "step2",
        "no": "end"
    },
    "step2": {
        "text": "Есть ли интерес?\n(Да/Нет)",
        "yes": "step3",
        "no": "end"
    },
    "step3": {
        "text": "Записали ли вы результат в CRM?\n(Да/Нет)",
        "yes": "end",
        "no": "end"
    },
    "end": {
        "text": "Сценарий завершён. Спасибо!",
        "yes": "start",
        "no": "start"
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['step'] = "start"
    reply_markup = ReplyKeyboardMarkup([["Да", "Нет"]], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(SCENARIO["start"]["text"], reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step", "start")
    user_answer = update.message.text.lower()
    if user_answer not in ["да", "нет"]:
        await update.message.reply_text("Пожалуйста, выберите только 'Да' или 'Нет'")
        return
    next_step = SCENARIO[step]["yes"] if user_answer == "да" else SCENARIO[step]["no"]
    context.user_data['step'] = next_step
    reply_markup = ReplyKeyboardMarkup([["Да", "Нет"]], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(SCENARIO[next_step]["text"], reply_markup=reply_markup)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
