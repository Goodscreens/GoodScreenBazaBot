import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

TOKEN = os.environ.get("TOKEN", "YOUR_BOT_TOKEN")

DEPARTMENTS = [
    "Продажи", "Маркетинг", "СММ", "Делопроизводство", "Дизайн",
    "Закупки", "Склад", "Производство", "Монтаж", "Логистика", "IT", "Финансы"
]

RESPONSIBLES = {
    "Продажи": "@responsible_sales",
    "Маркетинг": "@responsible_marketing",
    "СММ": "@responsible_smm",
    "Делопроизводство": "@responsible_doc",
    "Дизайн": "@responsible_design",
    "Закупки": "@responsible_purchase",
    "Склад": "@responsible_warehouse",
    "Производство": "@responsible_factory",
    "Монтаж": "@responsible_install",
    "Логистика": "@responsible_logistics",
    "IT": "@responsible_it",
    "Финансы": "@responsible_finance"
}

SCENARIOS = {
    "Продажи": {
        'start': {
            'text': 'Это бот-инструкция для отдела продаж. Начнём?',
            'yes': 'step_1',
            'no': 'end'
        },
        'step_1': {
            'text': '1. Новый лид поступил в Bitrix?',
            'yes': 'step_1_yes',
            'no': 'step_1_no'
        },
        'step_1_yes': {
            'text': 'Менеджер принимает лид совершая звонок или отправляя письмо и вносит все данные в Bitrix\n2. Менеджер связался с клиентом?',
            'yes': 'step_2_yes',
            'no': 'step_2_no'
        },
        'step_1_no': {
            'text': 'Сообщить о сбое ответственному за интеграцию. Проверить форму на сайте/квизе.\nСценарий завершён.',
            'yes': 'end',
            'no': 'end'
        },
        'step_2_yes': {
            'text': 'Уточнить ТЗ клиента и внести все данные в карточку лида, переместив его.\n3. ТЗ клиента уточнено?',
            'yes': 'step_3_yes',
            'no': 'step_3_no'
        },
        'step_2_no': {
            'text': 'Вручную назначить ответственного. Уведомить руководителя.\nСценарий завершён.',
            'yes': 'end',
            'no': 'end'
        },
        'step_3_yes': {
            'text': 'Проверка релевантности проекта.\n4. Проект релевантен (бюджет/регион/тема)?',
            'yes': 'step_4_yes',
            'no': 'step_4_no'
        },
        'step_3_no': {
            'text': 'Перезвонить, запросить детали по чек-листу. Поставить задачу "ожидание ТЗ".\nСценарий завершён.',
            'yes': 'end',
            'no': 'end'
        },
        'step_4_yes': {
            'text': 'Внести параметры в калькулятор, получить расчёт.\n5. КП подготовлено?',
            'yes': 'step_5_yes',
            'no': 'step_5_no'
        },
        'step_4_no': {
            'text': 'Зафиксировать причину отказа, перевести лид в архив, заполнить комментарий.\nСценарий завершён.',
            'yes': 'end',
            'no': 'end'
        },
        'step_5_yes': {
            'text': 'Отправить КП клиенту, зафиксировать в Bitrix.\n6. КП отправлено клиенту?',
            'yes': 'step_6_yes',
            'no': 'step_6_no'
        },
        'step_5_no': {
            'text': 'Внести параметры в калькулятор. Запросить визуал у дизайнера (если нужно).\nСценарий завершён.',
            'yes': 'end',
            'no': 'end'
        },
        'step_6_yes': {
            'text': 'Ждать обратной связи.\n7. Клиент дал обратную связь в течение 3 дней?',
            'yes': 'step_7_yes',
            'no': 'step_7_no'
        },
        'step_6_no': {
            'text': 'Отправить КП (Bitrix/email), отметить в карточке лида.\nСценарий завершён.',
            'yes': 'end',
            'no': 'end'
        },
        'step_7_yes': {
            'text': 'Проверить интерес клиента.\n8. Клиент подтвердил интерес?',
            'yes': 'step_8_yes',
            'no': 'step_8_no'
        },
        'step_7_no': {
            'text': 'Сделать follow-up (звонок/письмо), обновить статус в Bitrix.\nСценарий завершён.',
            'yes': 'end',
            'no': 'end'
        },
        'step_8_yes': {
            'text': 'Создать задачу инженеру для согласования.\n9. Передано инженеру для согласования?',
            'yes': 'step_9_yes',
            'no': 'step_9_no'
        },
        'step_8_no': {
            'text': 'Зафиксировать причину, перевести лид в архив/отказ, заполнить комментарий.\nСценарий завершён.',
            'yes': 'end',
            'no': 'end'
        },
        'step_9_yes': {
            'text': 'Ждать ответа инженера.\n10. Инженер дал ответ вовремя?',
            'yes': 'step_10_yes',
            'no': 'step_10_no'
        },
        'step_9_no': {
            'text': 'Создать задачу инженеру, приложить КП и ТЗ.\nСценарий завершён.',
            'yes': 'end',
            'no': 'end'
        },
        'step_10_yes': {
            'text': 'КП согласовано, переход к оформлению договора.\n11. КП согласовано, договор оформлен?',
            'yes': 'step_11_yes',
            'no': 'step_11_no'
        },
        'step_10_no': {
            'text': 'Напомнить инженеру, уведомить Влада при задержке >2 дней.\nСценарий завершён.',
            'yes': 'end',
            'no': 'end'
        },
        'step_11_yes': {
            'text': 'Передача документов Таня (оформление договора/счёта).\n12. Документы переданы в производство?',
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
            'text': 'Сценарий завершён. Спасибо!',
            'yes': 'start',
            'no': 'start'
        }
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

def get_step_keyboard(step, path):
    buttons = [
        [InlineKeyboardButton("Да", callback_data=f"answer|yes")],
        [InlineKeyboardButton("Нет", callback_data=f"answer|no")]
    ]
    nav = []
    if path:
        nav.append(InlineKeyboardButton("Назад", callback_data="nav|back"))
    nav.append(InlineKeyboardButton("Начать сначала", callback_data="nav|reset"))
    buttons.append(nav)
    return InlineKeyboardMarkup(buttons)

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
        contact = RESPONSIBLES.get(dep, "ответственному руководителю")
        await query.edit_message_text(
            f"Твоя инструкция в разработке, пока можешь обратиться к @amiled_pro или @vladislavsaenko"
        )
        await start(update, context)
        return

    context.user_data['step'] = 'start'
    context.user_data['path'] = []
    await show_step(update, context, edit=True)

async def step_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_data = context.user_data
    dep = user_data.get('department')
    scenario = SCENARIOS[dep]
    step = user_data.get('step', 'start')
    path = user_data.get('path', [])

    if query.data == "nav|reset":
        context.user_data.clear()
        await start(update, context)
        return
    if query.data == "nav|back" and path:
        prev = path[-1]
        user_data['step'] = prev
        user_data['path'] = path[:-1]
        await show_step(update, context, edit=True)
        return

    answer = "yes" if query.data == "answer|yes" else "no"
    next_step = scenario[step]['yes'] if answer == "yes" else scenario[step]['no']
    user_data['step'] = next_step
    user_data['path'] = path + [step]
    await show_step(update, context, edit=True)

async def show_step(update, context, edit=False):
    user_data = context.user_data
    dep = user_data['department']
    scenario = SCENARIOS[dep]
    step = user_data['step']
    path = user_data.get('path', [])
    text = scenario[step]['text']
    keyboard = get_step_keyboard(step, path)
    if edit:
        await update.callback_query.edit_message_text(text, reply_markup=keyboard)
    else:
        await update.message.reply_text(text, reply_markup=keyboard)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(department_callback, pattern=r"^department\|"))
    app.add_handler(CallbackQueryHandler(step_callback, pattern=r"^(answer|nav)\|"))
    app.run_polling()

if __name__ == '__main__':
    main()
