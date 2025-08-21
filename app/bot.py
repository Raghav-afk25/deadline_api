# app/bot.py
import os
import secrets
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from app.config import BOT_TOKEN, users_col, PLANS  # PLANS if you keep plans in config
# If you keep PLANS in app/plans.py then: from app.plans import PLANS

OWNER_ID = int(os.getenv("OWNER_ID", "0"))  # your Telegram user id

def _month_str():
    now = datetime.utcnow()
    return f"{now.year:04d}-{now.month:02d}"

def _today_str():
    return datetime.utcnow().strftime("%Y-%m-%d")

def _new_key() -> str:
    # short, URL-safe key
    return secrets.token_urlsafe(16)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "DeadlineTech Bot\n\n"
        "Commands:\n"
        "/getkey - Generate/Rotate your API key\n"
        "/myplan - Show your plan & usage\n"
        "/plans  - View available plans (codes)\n"
        "Owner-only: /setplan <user_id> <plan_code> [months]\n"
        "            /ban <user_id> | /unban <user_id>\n"
    )

async def plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lines = []
    for code, p in PLANS.items():
        lines.append(f"{code}: {p['daily']}/day, {p['monthly']}/month, ₹{p.get('price_rs', '-')}rs")
    await update.message.reply_text("Available plans:\n" + "\n".join(lines))

async def getkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = users_col.find_one({"tg_id": uid})
    if not user:
        # default plan when first time (you can change)
        default = "d1k" if "d1k" in PLANS else list(PLANS.keys())[0]
        plan = PLANS[default]
        key = _new_key()
        now = datetime.utcnow()
        doc = {
            "tg_id": uid,
            "api_key": key,
            "plan_code": default,
            "daily_limit": plan["daily"],
            "monthly_limit": plan["monthly"],
            "active": True,
            "created_at": now,
            "expires_at": now + timedelta(days=30),  # 1 month
            "daily_count": 0,
            "daily_reset_date": _today_str(),
            "monthly_count": 0,
            "month_start": _month_str(),
            # optional usage maps if you use them elsewhere
            "usage": {},
            "monthly_usage": {},
        }
        users_col.insert_one(doc)
        await update.message.reply_text(
            f"Your API key:\n`{key}`\n\nPlan: {default}\nDaily: {plan['daily']} | Monthly: {plan['monthly']}",
            parse_mode="Markdown",
        )
    else:
        # rotate (new key) keeping plan/limits same
        key = _new_key()
        users_col.update_one({"tg_id": uid}, {"$set": {"api_key": key}})
        await update.message.reply_text(f"Your new API key:\n`{key}`", parse_mode="Markdown")

async def myplan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = users_col.find_one({"tg_id": uid})
    if not user:
        await update.message.reply_text("No key yet. Use /getkey")
        return
    dleft = max(0, int(user.get("daily_limit", 0)) - int(user.get("daily_count", 0)))
    mleft = max(0, int(user.get("monthly_limit", 0)) - int(user.get("monthly_count", 0)))
    msg = (
        f"Plan: {user.get('plan_code')}\n"
        f"API Key: `{user.get('api_key')}`\n"
        f"Daily: {user.get('daily_count',0)}/{user.get('daily_limit')}, left {dleft}\n"
        f"Monthly: {user.get('monthly_count',0)}/{user.get('monthly_limit')}, left {mleft}\n"
        f"Active: {user.get('active', True)}\n"
        f"Expires: {user.get('expires_at')}"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

def _owner_check(update: Update) -> bool:
    return update.effective_user and update.effective_user.id == OWNER_ID

async def setplan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _owner_check(update):
        await update.message.reply_text("Owner only.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /setplan <tg_user_id> <plan_code> [months]")
        return
    try:
        target = int(context.args[0])
    except:
        await update.message.reply_text("Invalid tg_user_id")
        return
    plan_code = context.args[1]
    months = int(context.args[2]) if len(context.args) >= 3 else 1
    if plan_code not in PLANS:
        await update.message.reply_text("Unknown plan code.")
        return
    plan = PLANS[plan_code]
    now = datetime.utcnow()
    res = users_col.find_one_and_update(
        {"tg_id": target},
        {"$set": {
            "plan_code": plan_code,
            "daily_limit": plan["daily"],
            "monthly_limit": plan["monthly"],
            "expires_at": now + timedelta(days=30*months),
            "active": True,
        }},
        upsert=True,
        return_document=True,
    )
    await update.message.reply_text(f"Set plan for {target}: {plan_code} ({plan['daily']}/day, {plan['monthly']}/month)")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _owner_check(update):
        await update.message.reply_text("Owner only.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /ban <tg_user_id>")
        return
    users_col.update_one({"tg_id": int(context.args[0])}, {"$set": {"active": False}})
    await update.message.reply_text("Banned.")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _owner_check(update):
        await update.message.reply_text("Owner only.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /unban <tg_user_id>")
        return
    users_col.update_one({"tg_id": int(context.args[0])}, {"$set": {"active": True}})
    await update.message.reply_text("Unbanned.")

def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN missing in .env")
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("plans", plans))
    app.add_handler(CommandHandler("getkey", getkey))
    app.add_handler(CommandHandler("myplan", myplan))
    app.add_handler(CommandHandler("setplan", setplan))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
