import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

referrals = {}
invited_by = {}

REQUIRED = 5

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id

    if user_id not in referrals:
        referrals[user_id] = 0

    # referral logic
    if context.args:
        referrer_id = int(context.args[0])

        if user_id != referrer_id and user_id not in invited_by:
            invited_by[user_id] = referrer_id

            referrals[referrer_id] = referrals.get(referrer_id, 0) + 1

            await context.bot.send_message(
                chat_id=referrer_id,
                text=f"🎉 Referral added!\nProgress: {referrals[referrer_id]}/{REQUIRED}"
            )

            if referrals[referrer_id] == REQUIRED:
                await context.bot.send_message(
                    chat_id=referrer_id,
                    text="🔥 Congrats! You unlocked 10GB. Contact admin."
                )

    bot_username = (await context.bot.get_me()).username
    link = f"https://t.me/{bot_username}?start={user_id}"

    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "📸 Send screenshot after signup\n\n"
        "👥 Invite 5 friends to unlock 10GB\n\n"
        f"🔗 Your link:\n{link}\n\n"
        f"📊 Progress: {referrals[user_id]}/{REQUIRED}"
    )

# PHOTO HANDLER
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo = update.message.photo[-1]

    username = user.username if user.username else "NoUsername"

    # send to admin
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📥 Screenshot from {username} (ID: {user.id})"
    )

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo.file_id
    )

    # IMPORTANT: new instruction after image
    await update.message.reply_text(
        "✅ Screenshot received!\n\n"
        "👥 Now invite 5 friends to unlock 10GB 📶\n"
        "Use /start to get your referral link."
    )

# MAIN
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("BOT RUNNING...")
    app.run_polling()

if __name__ == "__main__":
    main()