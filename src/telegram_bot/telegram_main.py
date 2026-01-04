import os
from telegram import Bot
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    InlineQueryHandler,
    filters,
)

from handlers.basic import start, echo, caps, unknown
from handlers.tracker import (
    send_tracker_updates,
    addflight_start,
    removeflight_start,
    tracker_origin,
    tracker_destination,
    tracker_date,
    tracker_time,
    addflight_confirm,
    removeflight_confirm,
    tracker_cancel,
    ORIGIN, DESTINATION, DATE, TIME, CONFIRM
)
from handlers.discovery import (
    discovery_start,
    select_job,
    discovery_show,
    discovery_decision, 
    discovery_cancel,
    JOB_SELECTION, SHOW_DATA, DECISION_CONTINUE
)
from handlers.inline import inline_caps
from utils import send_server_up

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_TOKEN = os.environ.get("WEBHOOK_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 8443))

async def _post_init(app):
    await send_server_up(app.bot)

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).post_init(_post_init).build()
    
    start_handler = CommandHandler('start', start)
    tracker_handler = CommandHandler('tracker', send_tracker_updates)
    add_flight_handler = ConversationHandler(
        entry_points=[CommandHandler("nuevo_vuelo", addflight_start)],
        states={
            ORIGIN: [MessageHandler(filters.TEXT, tracker_origin)],
            DESTINATION: [MessageHandler(filters.TEXT, tracker_destination)],
            DATE: [MessageHandler(filters.TEXT, tracker_date)],
            TIME: [MessageHandler(filters.TEXT, tracker_time)],
            CONFIRM: [MessageHandler(filters.TEXT, addflight_confirm)],
        },
        fallbacks=[CommandHandler("cancelar", tracker_cancel)],
    )
    remove_flight_handler = ConversationHandler(
        entry_points=[CommandHandler("eliminar_vuelo", removeflight_start)],
        states={
            ORIGIN: [MessageHandler(filters.TEXT, tracker_origin)],
            DESTINATION: [MessageHandler(filters.TEXT, tracker_destination)],
            DATE: [MessageHandler(filters.TEXT, tracker_date)],
            TIME: [MessageHandler(filters.TEXT, tracker_time)],
            CONFIRM: [MessageHandler(filters.TEXT, removeflight_confirm)],
        },
        fallbacks=[CommandHandler("cancelar", tracker_cancel)],
    )
    discovery_handler = ConversationHandler(
        entry_points=[CommandHandler("buscador", discovery_start)],
        states={
            JOB_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_job)],
            SHOW_DATA: [
                MessageHandler(filters.Regex(r'^\d+$') & ~filters.COMMAND, discovery_show),
                CommandHandler("saltar", discovery_show)
            ],
            DECISION_CONTINUE: [MessageHandler(filters.Regex(r'(?i)^(Sí|No)$') & ~filters.COMMAND, discovery_decision)]
        },
        fallbacks=[CommandHandler("cancelar", discovery_cancel)],
    )
    caps_handler = CommandHandler('caps', caps)
    inline_caps_handler = InlineQueryHandler(inline_caps)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)


    application.add_handler(start_handler)
    application.add_handler(tracker_handler)
    application.add_handler(add_flight_handler)
    application.add_handler(remove_flight_handler)
    application.add_handler(discovery_handler)
    application.add_handler(caps_handler)
    application.add_handler(inline_caps_handler)
    application.add_handler(echo_handler)
    application.add_handler(unknown_handler)

    send_server_up(application.bot)

    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        secret_token=WEBHOOK_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}",
    )
