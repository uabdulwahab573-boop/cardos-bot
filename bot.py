import os
import time
from pymongo import MongoClient
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
MONGO_URL = os.getenv("MONGO_URL")

client = MongoClient(MONGO_URL)
db = client["cardos_bot"]
users = db["users"]

# GET USER
def get_user(user_id):
    user = users.find_one({"user_id": user_id})
    if not user:
        user = {
            "user_id": user_id,
            "balance": 0,
            "referrals": 0,
            "invited_by": None,
            "last_claim": 0
        }
        users.insert_one(user)
    return user

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id

    user_data = get_user(user_id)

    # Referral
    if context.args:
        referrer_id = int(context.args[0])

        if user_id != referrer_id and not user_data["invited_by"]:
            users.update_one(
                {"user_id": user_id},
                {"$set": {"invited_by": referrer_id}}
            )

            users.update_one(
                {"user_id": referrer_id},
                {
                    "$inc": {
                        "referrals": 1,
                        "balance": 150
                    }
                }
            )

            ref_user = get_user(referrer_id)

            await context.bot.send_message(
                chat_id=referrer_id,
                text=f"🎉 New referral!\n+₦150\nTotal: {ref_user['referrals']}/5"
            )

            if ref_user["referrals"] == 5:
                await context.bot.send_message(
                    chat_id=referrer_id,
                    text="🎉 You unlocked FREE 10GB!"
                )

    bot_username = (await context.bot.get_me()).username
    referral_link = f"https://t.me/{bot_username}?start={user_id}"

    text = (
        "🎉 Welcome to Cardos Bot!\n\n"
        "💰 Earn ₦100 daily + ₦150 per referral\n\n"

        f"🔗 Your link:\n{referral_link}\n\n"

        f"👥 Referrals: {user_data['referrals']}/5\n"
        f"💰 Balance: ₦{user_data['balance']}\n\n"

        "📸 Send screenshot after signup\n"
        "💬 Support: https://wa.me/2347072366929"
    )

    await update.message.reply_text(text)

# CLAIM
async def claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user = get_user(user_id)

    now = time.time()

    if now - user["last_claim"] >= 86400:
        users.update_one(
            {"user_id": user_id},
            {
                "$inc": {"balance": 100},
                "$set": {"last_claim": now}
            }
        )

        await update.message.reply_text("✅ You claimed ₦100")
    else:
        await update.message.reply_text("⏳ Already claimed today")

# BALANCE
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user = get_user(user_id)

    await update.message.reply_text(f"💰 Balance: ₦{user['balance']}")

# WITHDRAW
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user = get_user(user_id)

    if user["balance"] >= 5000:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"💸 Withdrawal request\nUser: {user_id}\nAmount: ₦{user['balance']}"
        )

        users.update_one(
            {"user_id": user_id},
            {"$set": {"balance": 0}}
        )

        await update.message.reply_text("✅ Withdrawal requested")
    else:
        await update.message.reply_text("❌ Minimum is ₦5000")

# PHOTO
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo = update.message.photo[-1]

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📥 Screenshot from {user.id}"
    )

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo.file_id
    )

    await update.message.reply_text("✅ Screenshot sent")

# MAIN
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("claim", claim))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("withdraw", withdraw))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot running with database...")
    app.run_polling()

if __name__ == "__main__":
    main()