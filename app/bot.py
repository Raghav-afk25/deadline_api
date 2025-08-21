import logging
import secrets
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from app.config import BOT_TOKEN, OWNER_ID, users_col, PLANS

# ---------- logging ----------
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO
)
log = logging.getLogger("deadline-bot")

# ---------- helpers ----------
def _today() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d")

def _month() -> str:
    now = datetime.utcnow()
    return f"{now.year:04d}-{now.month:02d}"

def _new_key() -> str:
    return secrets.token_urlsafe(16)

def _owner(update: Update) -> bool:
    return update.effective_user and update.effective_user.id == OWNER_ID

# ---------- commands ----------
async def start(update: Update, _: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "DeadlineTech Bot ✅\n\n"
        "/ping – check bot\n"
        "/plans – list plans\n"
        "/getkey – generate/rotate your API key\n"
        "/myplan – show plan & usage\n\n"
        "Owner only:\n"
        "/setplan <tg_id> <plan_code> [months]\n"
        "/ban <tg_id>\n"
        "/unban <tg_id>\n"
    )

async def ping(update: Update, _: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("pong ✅")

async def plans(update: Update, _: ContextTypes.DEFAULT_TYPE):
    lines = [
        f"{code}: {p['daily']}/day, {p['monthly']}/month, ₹{p.get('price_rs','-')}"
        for code, p in PLANS.items()
    ]
    await update.message.reply_text("Available plans:\n" + "\n".join(lines))

async def getkey(update: Update, _: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = users_col.find_one({"tg_id": uid})

    if not user:
        # first time: assign default plan
        plan_code = "d1k" if "d1k" in PLANS else list(PLANS.keys())[0]
        plan = PLANS[plan_code]
        key = _new_key()
        now = datetime.utcnow()
        users_col.insert_one({
            "tg_id": uid,
            "api_key": key,
            "plan_code": plan_code,
            "daily_limit": plan["daily"],
            "monthly_limit": plan["monthly"],
            "active": True,
            "created_at": now,
            "expires_at": now + timedelta(days=30),
            "daily_count": 0, "daily_reset_date": _today(),
            "monthly_count": 0, "month_start": _month(),
            # optional maps if you also track per-day/per-month docs elsewhere:
            "usage": {}, "monthly_usage": {},
        })
        await update.message.reply_text(
            f"Your API key:\n`{key}`\nPlan: {plan_code}\n"
            f"Daily: {plan['daily']} | Monthly: {plan['monthly']}",
            parse_mode="Markdown"
        )
        return

    # rotate existing key
    key = _new_key()
    users_col.update_one({"tg_id": uid}, {"$set": {"api_key": key}})
    await update.message.reply_text(f"New API key:\n`{key}`", parse_mode="Markdown")

async def myplan(update: Update, _: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = users_col.find_one({"tg_id": uid})
    if not user:
        await update.message.reply_text("No key yet. Use /getkey")
        return
    d, dl = user.get("daily_count", 0), user.get("daily_limit", 0)
    m, ml = user.get("monthly_count", 0), user.get("monthly_limit", 0)
    msg = (
        f"Plan: {user.get('plan_code')}\n"
        f"Key: `{user.get('api_key')}`\n"
        f"Daily: {d}/{dl} | Monthly: {m}/{ml}\n"
        f"Active: {user.get('active', True)}\n"
        f"Expires: {user.get('expires_at')}"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def setplan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _owner(update):
        await update.message.reply_text("Owner only.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /setplan <tg_user_id> <plan_code> [months]")
        return
    try:
        target = int(context.args[0])
    except Exception:
        await update.message.reply_text("Invalid tg_user_id")
        return
    plan_code = context.args[1]
    months = int(context.args[2]) if len(context.args) >= 3 else 1
    if plan_code not in PLANS:
        await update.message.reply_text("Unknown plan code.")
        return

    plan = PLANS[plan_code]
    now = datetime.utcnow()
    users_col.update_one(
        {"tg_id": target},
        {"$set": {
            "plan_code": plan_code,
            "daily_limit": plan["daily"],
            "monthly_limit": plan["monthly"],
            "expires_at": now + timedelta(days=30*months),
            "active": True
        }},
        upsert=True
    )
    await update.message.reply_text(
        f"Set plan for {target}: {plan_code} ({plan['daily']}/day, {plan['monthly']}/month)"
    )

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _owner(update):
        await update.message.reply_text("Owner only.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /ban <tg_user_id>")
        return
    users_col.update_one({"tg_id": int(context.args[0])}, {"$set": {"active": False}})
    await update.message.reply_text("Banned.")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _owner(update):
        await update.message.reply_text("Owner only.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /unban <tg_user_id>")
        return
    users_col.update_one({"tg_id": int(context.args[0])}, {"$set": {"active": True}})
    await update.message.reply_text("Unbanned.")

async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.exception("Update error: %s", context.error)

def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN missing in .env or config")
    logging.info("Starting bot polling…")
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("plans", plans))
    app.add_handler(CommandHandler("getkey", getkey))
    app.add_handler(CommandHandler("myplan", myplan))
    app.add_handler(CommandHandler("setplan", setplan))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))

    app.add_error_handler(on_error)
    app.run_polling()

if __name__ == "__main__":
    main()
