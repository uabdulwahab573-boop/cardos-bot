import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

users = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    users.add(user_id)

    keyboard = [
        [InlineKeyboardButton("✅ I've signed up", callback_data="signed")]
    ]

    text = (
        "Welcome to Cardos Bot 👋\n\n"
        "Follow these steps:\n"
        "1. Download CardCosmic\n"
        "2. Use code: JSEXD8\n"
        "3. Complete signup\n\n"
        "Click below when done 👇"
    )

    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "signed":
        keyboard = [
            [InlineKeyboardButton("📸 Upload Screenshot", callback_data="upload")],
            [InlineKeyboardButton("📨 Referral Program", callback_data="referral")]
        ]

        await query.edit_message_text(
            "Nice one 👍\n\nSend your screenshot to continue 📸",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "upload":
        await query.edit_message_text("Send your screenshot now 📸")

    elif query.data == "referral":
        await query.edit_message_text(
            "Invite 5 friends using your referral link.\nAfter that, you unlock rewards 🎁"
        )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📥 Screenshot from @{user.username} (ID: {user.id})"
    )

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id
    )

    await update.message.reply_text("✅ Screenshot received!")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id == ADMIN_ID:
        await update.message.reply_text(f"👥 Total users: {len(users)}")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

app.run_polling()