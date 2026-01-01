from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

SELECT_JOB = 1

DISCOVERY_JOBS = [
    "job_alpha",
    "job_beta",
    "job_gamma",
]

async def discovery_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[job] for job in DISCOVERY_JOBS]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await update.message.reply_text(
        "Select a discovery job:",
        reply_markup=markup,
    )
    return SELECT_JOB


async def discovery_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected_job = update.message.text

    # Placeholder — replace later
    result = f"📊 Results for discovery job: {selected_job}\n(TODO)"

    await update.message.reply_text(result)
    return ConversationHandler.END


async def discovery_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Discovery cancelled.")
    return ConversationHandler.END
