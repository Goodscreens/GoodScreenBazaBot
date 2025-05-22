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
        'Поехали': 'step_1',
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
    'step_2_yes': {
        'text': 'Уточнить ТЗ клиента и внести все данные в карточку лида, переместив его.\n3. ТЗ клиента уточнено?\n(Да/Нет)',
        'yes': 'step_3_yes',
        'no': 'step_3_no'
    },
    'step_2_no': {
        'text': 'Вручную назначить ответственного. Уведомить руководителя.\nСценарий завершён.',
        'yes': 'end',
        'no': 'end'
    },
    'step_3_yes': {
        'text': 'Проверка релевантности проекта.\n4. Проект релевантен (бюджет/регион/тема)?\n(Да/Нет)',
        'yes': 'step_4_yes',
        'no': 'step_4_no'
    },
    'step_3_no': {
        'text': 'Перезвонить, запросить детали по чек-листу. Поставить задачу "ожидание ТЗ".\nСценарий завершён.',
        'yes': 'end',
        'no': 'end'
    },
    'step_4_yes': {
        'text': 'Внести параметры в калькулятор, получить расчёт.\n5. КП подготовлено?\n(Да/Нет)',
        'yes': 'step_5_yes',
        'no': 'step_5_no'
    },
    'step_4_no': {
        'text': 'Зафиксировать причину отказа, перевести лид в архив, заполнить комментарий.\nСценарий завершён.',
        'yes': 'end',
        'no': 'end'
    },
    'step_5_yes': {
        'text': 'Отправить КП клиенту, зафиксировать в Bitrix.\n6. КП отправлено клиенту?\n(Да/Нет)',
        'yes': 'step_6_yes',
        'no': 'step_6_no'
    },
    'step_5_no': {
        'text': 'Внести параметры в калькулятор. Запросить визуал у дизайнера (если нужно).\nСценарий завершён.',
        'yes': 'end',
        'no': 'end'
    },
    'step_6_yes': {
        'text': 'Ждать обратной связи.\n7. Клиент дал обратную связь в течение 3 дней?\n(Да/Нет)',
        'yes': 'step_7_yes',
        'no': 'step_7_no'
    },
    'step_6_no': {
        'text': 'Отправить КП (Bitrix/email), отметить в карточке лида.\nСценарий завершён.',
        'yes': 'end',
        'no': 'end'
    },
    'step_7_yes': {
        'text': 'Проверить интерес клиента.\n8. Клиент подтвердил интерес?\n(Да/Нет)',
        'yes': 'step_8_yes',
        'no': 'step_8_no'
    },
    'step_7_no': {
        'text': 'Сделать follow-up (звонок/письмо), обновить статус в Bitrix.\nСценарий завершён.',
        'yes': 'end',
        'no': 'end'
    },
    'step_8_yes': {
        'text': 'Создать задачу инженеру для согласования.\n9. Передано инженеру для согласования?\n(Да/Нет)',
        'yes': 'step_9_yes',
        'no': 'step_9_no'
    },
    'step_8_no': {
        'text': 'Зафиксировать причину, перевести лид в архив/отказ, заполнить комментарий.\nСценарий завершён.',
        'yes': 'end',
        'no': 'end'
    },
    'step_9_yes': {
        'text': 'Ждать ответа инженера.\n10. Инженер дал ответ вовремя?\n(Да/Нет)',
        'yes': 'step_10_yes',
        'no': 'step_10_no'
    },
    'step_9_no': {
        'text': 'Создать задачу инженеру, приложить КП и ТЗ.\nСценарий завершён.',
        'yes': 'end',
        'no': 'end'
    },
    'step_10_yes': {
        'text': 'КП согласовано, переход к оформлению договора.\n11. КП согласовано, договор оформлен?\n(Да/Нет)',
        'yes': 'step_11_yes',
        'no': 'step_11_no'
    },
    'step_10_no': {
        'text': 'Напомнить инженеру, уведомить Влада при задержке >2 дней.\nСценарий завершён.',
        'yes': 'end',
        'no': 'end'
    },
    'step_11_yes': {
        'text': 'Передача документов Таня (оформление договора/счёта).\n12. Документы переданы в производство?\n(Да/Нет)',
        'yes': 'step_12_yes',
        'no': 'step_12_no'
    },
    'step_11_no': {
        'text': 'Уточнить причину, запросить правки, напомнить Таня.\nСценарий завершён.',
        'yes': 'end',
        'no': 'end'
    },
    'step_12_yes': {
        'text': 'Задача отдела продаж выполнена!\nСценарий завершён.',
        'yes': 'end',
        'no': 'end'
    },
    'step_12_no': {
        'text': 'Отправить проектному менеджеру, убедиться в получении.\nСценарий завершён.',
        'yes': 'end',
        'no': 'end'
    },
    'end': {
        'text': 'Ты молодец! Спасибо!',
        'Заново': 'start',
        'no': 'start'
    }
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
