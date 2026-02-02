import asyncio
from functools import wraps
import logging, logging.handlers
import os
import sys
from telegram import Update, Bot
from telegram.ext import ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
LIST_OF_ADMINS = [1042856343]


def handle_error(func):
    """Decorator to handle errors in Telegram bot handlers."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            """Log the error and send a telegram message to notify the developer."""
            user_id = update.effective_user.id if update.effective_user else "unknown"

            tb = sys.exc_info()[2]
            while tb.tb_next:
                tb = tb.tb_next
            frame = tb.tb_frame
            function_name = frame.f_code.co_name
            filename = frame.f_code.co_filename
            line_no = tb.tb_lineno

            logging.error(
                msg=f"Exception while handling an update in function '{function_name}' from user {update.effective_user.id}: {e}", 
                exc_info=context.error
            )

            try:
                if user_id in LIST_OF_ADMINS:
                    await update.message.reply_text(
                        f"Ha ocurrido un error en la función '{function_name}': {context.error}\n"
                        f"({filename}:{line_no})"
                    )
                else:
                    await update.message.reply_text("Ha ocurrido un error inesperado con tu petición. El equipo de desarrollo ha sido notificado.")
                    for admin in LIST_OF_ADMINS:
                        await context.bot.send_message(chat_id=admin, text=f"Ha ocurrido un error en la función '{function_name}': {context.error}")
            except Exception:
                logging.error("Failed to send error message to user/admin.", exc_info=True)

    return wrapper


async def send_server_up(bot: Bot):
    for admin in LIST_OF_ADMINS:
        await bot.send_message(chat_id=admin, text="Server is up and running!")


def report_warnings(job: str):

    async def send(warnings: list):
        bot = Bot(token=BOT_TOKEN)
        if not warnings:
            for admin in LIST_OF_ADMINS:
                await bot.send_message(chat_id=admin, text=f"✅ {job} Job completed with no errors.")
        else:
            for admin in LIST_OF_ADMINS:
                await bot.send_message(chat_id=admin, text=f"⚠️ {job} Job Errors ({len(warnings)}):")
            for warn in warnings:
                for admin in LIST_OF_ADMINS:
                    await bot.send_message(chat_id=admin, text=warn)


    root = logging.getLogger()
    buffer_handler = next((h for h in root.handlers if isinstance(h, logging.handlers.MemoryHandler)), None)

    warnings = []

    # inspect buffered LogRecord objects
    if buffer_handler:
        for rec in buffer_handler.buffer:
            if rec.funcName != "<module>":
                warnings.append(f"({rec.module} -> {rec.funcName}) {rec.message}")
            else:
                warnings.append(f"({rec.module}) {rec.message}")

        print(f"Warnings: {warnings}")

        asyncio.run(send(warnings))


def restricted(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            print(f"Para realizar esta acción, tienes que pedir permiso a papi o mami (@DeividMay, @pilar_fdeez).")
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

'''
@restricted
async def my_handler(update, context):
    pass  # only accessible if `user_id` is in `LIST_OF_ADMINS`.
'''

def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        async def command_func(update, context, *args, **kwargs):
            await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return await func(update, context,  *args, **kwargs)
        return command_func
    
    return decorator


'''
send_typing_action = send_action(ChatAction.TYPING)
send_upload_video_action = send_action(ChatAction.UPLOAD_VIDEO)
send_upload_photo_action = send_action(ChatAction.UPLOAD_PHOTO)

OR

@send_action(ChatAction.TYPING)
async def my_handler(update, context):
    pass  # user will see 'typing' while your bot is handling the request.
'''