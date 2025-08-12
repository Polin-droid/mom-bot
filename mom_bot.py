from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "8312955168:AAGwRJ-HviU-4yZsReSxeZ3co1WdHL-cIDc"
ADMIN_CHAT_ID = 355613096  # Твой ID для админского чата

CONTENT_TEXT = (
    "Содержание пакета:\n"
    "1. Подготовка к возвращению из роддома\n"
    "2. Первый месяц\n"
    "3. Питание и кормление\n"
    "4. Сон\n"
    "5. Развитие по месяцам\n"
    "6. Мама после родов\n"
    "7. Частые проблемы и решения\n"
    "8. Экстренные ситуации"
)

PRICE_REKV_TEXT = (
    "Цена: 590 рублей\n"
    "Реквизиты для оплаты:\n"
    "Кому: Полина\n"
    "Карты: 2202 2082 7031 4322\n"
    "\nПосле оплаты пришли сюда фото платежа."
)

start_buttons = [
    [InlineKeyboardButton("Содержание гайда", callback_data='content')],
    [InlineKeyboardButton("Приобрести гайд", callback_data='buy')],
    [InlineKeyboardButton("Цена и реквизиты", callback_data='price')],
]

content_buttons = [
    [InlineKeyboardButton("Круто, хочу!", callback_data='price')],
    [InlineKeyboardButton("Назад", callback_data='start')],
]

price_buttons = [
    [InlineKeyboardButton("Назад", callback_data='start')],
]

GUIDE_LINK = "https://disk.yandex.ru/d/H57QFRziPHVtTQ"  # Твоя ссылка на гайд

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup(start_buttons)
    await update.message.reply_text("Привет! Выбери действие:", reply_markup=keyboard)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'start':
        keyboard = InlineKeyboardMarkup(start_buttons)
        await query.edit_message_text("Привет! Выбери действие:", reply_markup=keyboard)
    elif query.data == 'content':
        keyboard = InlineKeyboardMarkup(content_buttons)
        await query.edit_message_text(CONTENT_TEXT, reply_markup=keyboard)
    elif query.data == 'price':
        keyboard = InlineKeyboardMarkup(price_buttons)
        await query.edit_message_text(PRICE_REKV_TEXT, reply_markup=keyboard)
    elif query.data == 'buy':
        await query.edit_message_text(PRICE_REKV_TEXT + "\n\nПожалуйста, пришли сюда фото оплаты.")

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    user = update.message.from_user

    # Кнопка отправить гайд для админа с user_id в callback_data
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Отправить гайд", callback_data=f"sendguide_{user.id}")]]
    )
    caption = f"Фото оплаты от пользователя {user.first_name} (id: {user.id})"
    await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=photo.file_id, caption=caption, reply_markup=keyboard)
    await update.message.reply_text("Спасибо! Твое фото оплаты получено. Как только проверю, пришлю ссылку.")

async def send_guide_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Проверяем, что кнопку нажал админ
    if query.from_user.id != ADMIN_CHAT_ID:
        await query.answer("У вас нет прав отправлять гайд.", show_alert=True)
        return

    data = query.data
    user_id = int(data.split('_')[1])

    try:
        await context.bot.send_message(chat_id=user_id, text=f"Спасибо за оплату! Вот ссылка на гайд:\n{GUIDE_LINK}")
        await query.edit_message_caption(caption="Гайд отправлен пользователю ✅")
    except Exception as e:
        await query.answer(f"Ошибка при отправке: {e}", show_alert=True)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Используй /start для начала.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler, pattern='^(start|content|price|buy)$'))
    app.add_handler(MessageHandler(filters.PHOTO & (~filters.COMMAND), photo_handler))
    app.add_handler(CallbackQueryHandler(send_guide_callback, pattern='^sendguide_'))
    app.add_handler(CommandHandler("help", help_command))

    print("Бот запущен...")
    app.run_polling()