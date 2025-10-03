import random
import json
import os
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# -------------------------
# File-based persistent storage
# -------------------------
USERS_FILE = "users.json"

# Load users on startup
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
        # Convert join_date back to datetime
        for uid, data in users.items():
            data["join_date"] = datetime.fromisoformat(data["join_date"])
else:
    users = {}

# Save users to file
def save_users():
    with open(USERS_FILE, "w") as f:
        # Convert datetime to ISO string for JSON
        users_copy = {uid: {**data, "join_date": data["join_date"].isoformat()} for uid, data in users.items()}
        json.dump(users_copy, f, indent=4)

# -------------------------
# Global Variables
# -------------------------
ADMIN_ID = 8146774671  # Your Admin ID
manual_mode = {}

# -------------------------
# Helper Functions
# -------------------------
def generate_profile_id(user_id):
    return str(user_id)[:5] + str(random.randint(1000, 9999))

# -------------------------
# Command Handlers
# -------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    is_new = False

    if user_id not in users:
        users[user_id] = {
            "profile_id": generate_profile_id(user_id),
            "status": "newbie",
            "team_lead": "@Richyadd",
            "earnings": 0,
            "profits": 0,
            "avg_deal": 0,
            "share": 50,
            "pending_payout": 0,
            "paid": 0,
            "join_date": datetime.now()
        }
        save_users()
        is_new = True

    buttons = [
        ["👤 My Profile"],
        ["🪬 Channel", "💬 Team Chat"],
        ["✅ Join"]
    ]
    if str(user_id) == str(ADMIN_ID):
        buttons.append(["📢 Manual Message"])

    welcome_text = (
        "👋 Welcome to the squad! 🚀\n\nYou have successfully joined our exclusive crew!"
        if is_new else
        "✅ Welcome back to the squad! 🔥\n\nYou still have access to our exclusive crew!"
    )

    await update.message.reply_text(
        welcome_text,
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    )

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in users:
        await update.message.reply_text("⚠ Please use /start first to register.")
        return

    data = users[user_id]
    days_in_team = (datetime.now() - data["join_date"]).days + 1
    day_text = "day" if days_in_team == 1 else "days"

    profile_text = f"""Profile {data['profile_id']}
├ Status: {data['status']}
├ Team Lead: {data['team_lead']}

Total Earnings {data['earnings']} USDT
├ Number of Profits {data['profits']} pcs
├ Average Deal {data['avg_deal']} USDT
├ Your Share {data['share']}%

Payouts
├ Pending Payout {data['pending_payout']} USDT
├ Total Paid {data['paid']} USDT

In team: {days_in_team} {day_text}
"""
    await update.message.reply_text(profile_text)

async def channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📢 SANTY | Info\n\n"
        "information, updates, nuances, moments, situations, questions\n\n"
        "👉 https://t.me/+YuxCN4rSLyphN2M9"
    )

async def team_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in users:
        await update.message.reply_text("⚠ Please use /start first to register.")
        return

    status = users[user_id]["status"]
    if status == "newbie":
        await update.message.reply_text("🔒 Chat is locked for you!\nYour status: newbie")
    else:
        await update.message.reply_text("✅ Welcome to Team Chat!\n👉 https://t.me/YourGroupLink")

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⛔ Warning: Only serious players allowed here!\n\n"
        "First, understand what we're all about:\n👉 /work\n\n"
        "MasteBTC transaction reversals with our detailed guide:\n👉 /manual_mobile\n\n"
        "PC Guide is here:\n👉 /manual_pc\n\n"
        "Got questions? Hit up the boss:\n👉 /teamlead\n\n"
        "Studied? Practiced? Ready to make some real money? Message the team lead:\n👉 /teamlead"
    )

async def work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📘 Work Manual:\n👉 https://telegra.ph/Work-MANUAL-09-01")

async def manual_mobile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📱 Mobile Manual:\n👉 https://telegra.ph/SANTYCANCELING-OF-BTC-TRANSACTION-IN-MOBILE-09-01")

async def manual_pc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💻 PC Manual:\n👉 https://telegra.ph/SANTYMANUAL-FOR-PC-09-01")

async def teamlead(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👤 Contact Team Lead:\n👉 @Richyadd")

# -------------------------
# Admin Commands
# -------------------------
async def upgrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("⚠ Usage: /upgrade <user_id> <status>")
        return

    target_id = str(context.args[0])
    new_status = context.args[1]

    if target_id in users:
        users[target_id]["status"] = new_status
        save_users()
        await update.message.reply_text(f"✅ User {target_id} upgraded to {new_status}")
    else:
        await update.message.reply_text("❌ User not found in database.")

async def manual_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to use this.")
        return

    manual_mode[user_id] = True
    await update.message.reply_text("✍ Send me the message you want to broadcast to all users:")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id == ADMIN_ID and manual_mode.get(user_id):
        sent, failed = 0, 0
        for uid in users.keys():
            try:
                await context.bot.send_message(chat_id=int(uid), text=text)
                sent += 1
            except:
                failed += 1

        manual_mode[user_id] = False
        await update.message.reply_text(f"✅ Broadcast complete!\n📨 Sent: {sent}\n❌ Failed: {failed}")

# -------------------------
# Admin: List all users (simple)
# -------------------------
async def all_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to see this.")
        return

    if not users:
        await update.message.reply_text("No users yet.")
        return

    message = "📋 List of Users:\n\n"
    for uid, data in users.items():
        message += f"ID: {uid} | Profile: {data['profile_id']}\n"

    await update.message.reply_text(message)

# -------------------------
# Main
# -------------------------
def main():
    app = Application.builder().token("7636203866:AAFTAa2vvDH62zTpl_gtpKhkFqa1HNigVbo").build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("upgrade", upgrade))
    app.add_handler(CommandHandler("work", work))
    app.add_handler(CommandHandler("manual_mobile", manual_mobile))
    app.add_handler(CommandHandler("manual_pc", manual_pc))
    app.add_handler(CommandHandler("teamlead", teamlead))
    app.add_handler(CommandHandler("allusers", all_users))  # Admin only

    # Buttons
    app.add_handler(MessageHandler(filters.Regex("👤 My Profile"), profile))
    app.add_handler(MessageHandler(filters.Regex("🪬 Channel"), channel))
    app.add_handler(MessageHandler(filters.Regex("💬 Team Chat"), team_chat))
    app.add_handler(MessageHandler(filters.Regex("✅ Join"), join))
    app.add_handler(MessageHandler(filters.Regex("📢 Manual Message"), manual_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
