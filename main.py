import logging
import os
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, ReplyKeyboardRemove
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    CallbackQueryHandler, MessageHandler, filters
)

TOKEN = os.environ.get("TOKEN", "YOUR_BOT_TOKEN")

DEPARTMENTS = [
    "Продажи", "Маркетинг", "СММ", "Делопроизводство", "Дизайн",
    "Закупки", "Склад", "Производство", "Монтаж", "Логистика", "IT", "Финансы"
]

SCENARIOS = {
    "Продажи": {
        'start': {'text': 'Это бот-инструкция для отдела продаж. Начнём?', 'yes': 'step_1', 'no': 'end'},
        'step_1': {'text': '1. Новый лид поступил в Bitrix?', 'yes': 'step_1_yes', 'no': 'step_1_no'},
        'step_1_yes': {'text': 'Менеджер принимает лид... и т.д.', 'yes': 'step_2_yes', 'no': 'step_2_no'},
        'step_1_no': {'text': 'Сообщить о сбое ответственному... Сценарий завершён.', 'yes': 'end', 'no': 'end'},
        'step_2_yes': {'text': 'Уточнить ТЗ клиента... и т.д.', 'yes': 'step_3_yes', 'no': 'step_3_no'},
        'step_2_no': {'text': 'Вручную назначить ответственного... Сценарий завершён.', 'yes': 'end', 'no': 'end'},
        'step_3_yes': {'text': 'Проверка релевантности проекта...', 'yes': 'step_4_yes', 'no': 'step_4_no'},
        'step_3_no': {'text': 'Перезвонить, запросить детали... Сценарий завершён.', 'yes': 'end', 'no': 'end'},
        'step_4_yes': {'text': 'Внести параметры в калькулятор...', 'yes': 'step_5_yes', 'no': 'step_5_no'},
        'step_4_no': {'text': 'Зафиксировать причину отказа... Сценарий завершён.', 'yes': 'end', 'no': 'end'},
        'step_5_yes': {'text': 'Отправить КП клиенту...', 'yes': 'step_6_yes', 'no': 'step_6_no'},
        'step_5_no': {'text': 'Внести параметры в калькулятор... Сценарий завершён.', 'yes': 'end', 'no': 'end'},
        'step_6_yes': {'text': 'Ждать обратной связи...', 'yes': 'step_7_yes', 'no': 'step_7_no'},
        'step_6_no': {'text': 'Отправить КП... Сценарий завершён.', 'yes': 'end', 'no': 'end'},
        'step_7_yes': {'text': 'Проверить интерес клиента...', 'yes': 'step_8_yes', 'no': 'step_8_no'},
        'step_7_no': {'text': 'Сделать follow-up... Сценарий завершён.', 'yes': 'end', 'no': 'end'},
        'step_8_yes': {'text': 'Создать задачу инженеру...', 'yes': 'step_9_yes', 'no': 'step_9_no'},
        'step_8_no': {'text': 'Зафиксировать причину... Сценарий завершён.', 'yes': 'end', 'no': 'end'},
        'step_9_yes': {'text': 'Ждать ответа инженера...', 'yes': 'step_10_yes', 'no': 'step_10_no'},
        'step_9_no': {'text': 'Создать задачу инженеру... Сценарий завершён.', 'yes': 'end', 'no': 'end'},
        'step_10_yes': {'text': 'КП согласовано... переход к оформлению...', 'yes': 'step_11_yes', 'no': 'step_11_no'},
        'step_10_no': {'text': 'Напомнить инженеру... Сценарий завершён.', 'yes': 'end', 'no': 'end'},
        'step_11_yes': {'text': 'Передача документов Тане...', 'yes': 'step_12_yes', 'no': 'step_12_no'},
        'step_11_no': {'text': 'Уточнить причину... Сценарий завершён.', 'yes': 'end', 'no': 'end'},
        'step_12_yes': {'text': 'Задача отдела продаж выполнена! Сценарий завершён.', 'yes': 'end', 'no': 'end'},
        'step_12_no': {'text': 'Отправить проектному менеджеру... Сценарий завершён.', 'yes': 'end', 'no': 'end'},
        'end': {'text': 'Сценарий завершён. Спасибо!', 'yes': 'start', 'no': 'start'}
    },
    "Маркетинг": None,
    "СММ": None,
    "Делопроизводство": None,
    "Дизайн": None,
    "Закупки": None,
    "Склад": None,
    "Производство": None,
    "Монтаж": None,
    "Логистика": None,
    "IT": None,
    "Финансы": None
}

def get_departments_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(dep, callback_data=f"department|{dep}")]
        for dep in DEPARTMENTS
    ])

def get_reply_step_keyboard():
    return ReplyKeyboardMarkup(
        [["Да", "Нет"], ["Назад", "Начать сначала"]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    keyboard = get_departments_keyboard()
    if update.message:
        await update.message.reply_text(
            "Выберите отдел для работы с ботом:",
            reply_markup=keyboard
        )
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            "Выберите отдел для работы с ботом:",
            reply_markup=keyboard
        )

async def department_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    dep = query.data.split("|", 1)[1]
    context.user_data.clear()
    context.user_data['department'] = dep

    if not SCENARIOS[dep]:
        await query.edit_message_text(
            "Твоя инструкция в разработке, пока можешь обратиться к @amiled_pro или @vladislavsaenko",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Начать сначала", callback_data="nav|reset")]]
            )
        )
        return

    context.user_data['step'] = 'start'
    context.user_data['path'] = []
    # Новый шаг отправляем отдельным сообщением, чтобы активировать reply-клавиатуру
    await query.message.reply_text(SCENARIOS[dep]['start']['text'], reply_markup=get_reply_step_keyboard())

async def scenario_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    dep = user_data.get('department')
    if not dep or not SCENARIOS[dep]:
        return  # Не в сценарии — игнор

    scenario = SCENARIOS[dep]
    step = user_data.get('step', 'start')
    path = user_data.get('path', [])

    text = update.message.text.strip().lower()
    if text == "начать сначала":
        context.user_data.clear()
        await start(update, context)
        return
    if text == "назад" and path:
        prev = path[-1]
        user_data['step'] = prev
        user_data['path'] = path[:-1]
        await update.message.reply_text(scenario[prev]['text'], reply_markup=get_reply_step_keyboard())
        return

    answer = "yes" if text == "да" else "no"
    next_step = scenario[step]['yes'] if answer == "yes" else scenario[step]['no']
    user_data['step'] = next_step
    user_data['path'] = path + [step]

    # Если сценарий завершён, убираем клавиатуру
    if next_step == "end":
        await update.message.reply_text(scenario[next_step]['text'], reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text(scenario[next_step]['text'], reply_markup=get_reply_step_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Для любого текстового сообщения, не относящегося к сценарию — просто запускать start
    await start(update, context)

def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(department_callback, pattern=r"^department\|"))
    app.add_handler(CallbackQueryHandler(start, pattern=r"^nav\|reset"))  # сброс только для заглушки
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, scenario_reply_handler))
    app.run_polling()

if __name__ == '__main__':
    main()
