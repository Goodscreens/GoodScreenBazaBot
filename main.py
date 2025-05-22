import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

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
        # ... твой сценарий отдел продаж (оставь как есть)
        # ... копируешь полностью из предыдущего main.py
    },
    # Остальные отделы — заглушки
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    reply_markup = ReplyKeyboardMarkup(
        [[d] for d in DEPARTMENTS],
        one_time_keyboard=True,
        resize_keyboard=True
    )
    await update.message.reply_text(
        "Выберите отдел для работы с ботом:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if 'department' not in context.user_data:
        if text not in DEPARTMENTS:
            await update.message.reply_text("Выберите отдел из списка.")
            return
        context.user_data['department'] = text
        if not SCENARIOS[text]:
            contact = RESPONSIBLES.get(text, "ответственному руководителю")
            await update.message.reply_text(
                f"Твоя инструкция в разработке, пока можешь обратиться к {contact}"
            )
            context.user_data.clear()
            await start(update, context)
            return
        context.user_data['step'] = 'start'
        context.user_data['path'] = []
        await show_step(update, context)
        return

    if text.lower() == "начать сначала":
        context.user_data.clear()
        await start(update, context)
        return

    department = context.user_data['department']
    scenario = SCENARIOS[department]
    current_step = context.user_data.get('step', 'start')
    path = context.user_data.get('path', [])

    if text.lower() not in ["да", "нет", "назад", "начать сначала"]:
        await update.message.reply_text("Пожалуйста, выбери только 'Да', 'Нет', 'Назад' или 'Начать сначала'")
        return

    if text.lower() == "назад" and len(path) > 0:
        previous_step = path[-1]
        context.user_data['step'] = previous_step
        context.user_data['path'] = path[:-1]
        next_step = previous_step
    else:
        next_step = scenario[current_step]['yes'] if text.lower() == 'да' else scenario[current_step]['no']
        context.user_data['step'] = next_step
        context.user_data['path'] = path + [current_step]

    buttons = [["Да", "Нет"], ["Начать сначала"]]
    if len(context.user_data.get('path', [])) >= 1:
        buttons[1].insert(0, "Назад")
    reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(scenario[next_step]['text'], reply_markup=reply_markup)

async def show_step(update, context):
    department = context.user_data['department']
    step = context.user_data['step']
    scenario = SCENARIOS[department]
    reply_markup = ReplyKeyboardMarkup(
        [["Да", "Нет"], ["Начать сначала"]],
        one_time_keyboard=True,
        resize_keyboard=True
    )
    await update.message.reply_text(scenario[step]['text'], reply_markup=reply_markup)

async def remove_previous_webhook(app):
    try:
        await app.bot.delete_webhook()
    except Exception:
        pass

async def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()
    await remove_previous_webhook(app)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    PORT = int(os.environ.get('PORT', '10000'))
    await app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"https://goodscreenbazabot.onrender.com/{TOKEN}"
    )

if __name__ == '__main__':
    import asyncio

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except RuntimeError:
        # Если event loop уже запущен (иногда бывает на Render)
        import nest_asyncio
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
