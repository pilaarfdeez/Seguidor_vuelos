import datetime as dt
import glob
import json
import logging
import os
from telegram import Update, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, constants
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import BadRequest

from utils import handle_error

DATA_PATH = "../../data/"
JOB_SELECTION, SHOW_DATA, DECISION_CONTINUE = range(3)
price_filter = None

@handle_error
async def discovery_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    available_jobs = [[os.path.basename(f).replace("bargains_", "").replace(".json", "")] for f in glob.glob(f"{DATA_PATH}bargains_*.json")]
    
    markup = ReplyKeyboardMarkup(available_jobs, one_time_keyboard=True)
    text = ("¡Bienvenido al buscador de vuelos!\n"
            "Podrás encontrar las mejores ofertas para un viaje futuro.\n"
            "Puedes cancelar en cualquier momento escribiendo /cancelar.\n\n"
            "Para comenzar, selecciona uno de los buscadores de vuelos disponibles:")
    
    await update.message.reply_text(text, reply_markup=markup)
    return JOB_SELECTION


@handle_error
async def select_job(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected_job = update.message.text.strip()
    friendly_name = None

    context.user_data["selected_job"] = selected_job

    # try to open the job file to validate existence and get a friendly name
    try:
        with open(f"{DATA_PATH}bargains_{selected_job}.json", "r", encoding="utf-8") as f:
            job_info = json.load(f)
    except FileNotFoundError:
        available_jobs = [[os.path.basename(f).replace("bargains_", "").replace(".json", "")] for f in glob.glob(f"{DATA_PATH}bargains_*.json")]
        markup = ReplyKeyboardMarkup(available_jobs, one_time_keyboard=True)
        error_text = "No se han encontrado resultados para el buscador seleccionado. Por favor, prueba con otro."
        await update.message.reply_text(error_text, reply_markup=markup)
        return JOB_SELECTION

    if job_info and isinstance(job_info, list):
        try:
            friendly_name = job_info[0]["combinations"][0].get("job")
        except Exception:
            friendly_name = None
    context.user_data["friendly_name"] = friendly_name


    result = f"Has seleccionado el buscador *'{(friendly_name or selected_job)}'*\n"
    result += f"¿Cuál es el precio máximo que deseas filtrar? Para continuar sin filtrar, escribe /saltar."
    result = result.replace("-", "\\-").replace(".", "\\.").replace("_", "\\_").replace("?", "\\?").replace("!", "\\!")
    try:
        await update.message.reply_text(
            result,
            reply_markup=ReplyKeyboardRemove(), 
            parse_mode=constants.ParseMode.MARKDOWN_V2
        )
    except BadRequest:
        await update.message.reply_text(
            f"Has seleccionado el buscador '{friendly_name or selected_job}'\n"
            "¿Cuál es el precio máximo que deseas filtrar? Para continuar sin filtrar, escribe /saltar.",
            reply_markup=ReplyKeyboardRemove()
        )
    return SHOW_DATA


async def wrong_job(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("No se han encontrado resultados para el buscador.")
    return JOB_SELECTION


@handle_error
async def discovery_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    selected_job = context.user_data.get("selected_job")
    friendly_name = context.user_data.get("friendly_name")
    logging.info(f"User {user_id} selected job {selected_job}")

    # determine price filter from the user's message (numeric) or None
    text = (update.message.text or "").strip()
    price_filter = int(text) if text.isdigit() else None

    if not selected_job:
        available_jobs = [[os.path.basename(f).replace("bargains_", "").replace(".json", "")] for f in glob.glob(f"{DATA_PATH}bargains_*.json")]
        markup = ReplyKeyboardMarkup(available_jobs, one_time_keyboard=True)
        await update.message.reply_text("No se ha seleccionado un buscador. Por favor, selecciona uno:", reply_markup=markup)
        return JOB_SELECTION

    try:
        with open(f"{DATA_PATH}bargains_{selected_job}.json", "r", encoding="utf-8") as f:
            job_info = json.load(f)
    except FileNotFoundError:
        available_jobs = [[os.path.basename(f).replace("bargains_", "").replace(".json", "")] for f in glob.glob(f"{DATA_PATH}bargains_*.json")]
        markup = ReplyKeyboardMarkup(available_jobs, one_time_keyboard=True)
        await update.message.reply_text("Fichero del buscador no encontrado. Por favor, selecciona otro.", reply_markup=markup)
        return JOB_SELECTION

    # build and send one message per week
    header = f"📊 Resultados del buscador '{friendly_name or selected_job}'"
    if price_filter:
        header += f" (precio máximo: {price_filter} €)"

    total_shown = 0
    max_show = 30
    weekday_abbr = ['L', 'M', 'X', 'J', 'V', 'S', 'D']

    any_shown = False
    for week in job_info:
        if total_shown >= max_show:
            break

        week_header = week.get("week", "")
        combos = week.get("combinations", [])

        week_lines = [f"<b>Semana: {week_header}</b>", header]
        shown_in_week = 0

        for combo in combos:
            if total_shown >= max_show:
                break

            # total price
            try:
                total_price = int(combo.get("total_price") or 0)
            except Exception:
                total_price = 0

            if price_filter is not None and total_price > price_filter:
                continue

            # map price_change to emoji: 0 same, 1 cheaper, 2 more expensive
            pc_raw = combo.get("price_change", 0)
            try:
                pc = int(pc_raw)
            except Exception:
                if isinstance(pc_raw, bool):
                    pc = 2 if pc_raw else 0
                else:
                    pc = 0

            if pc == 1:
                pc_emoji = "🟢"
            elif pc == 2:
                pc_emoji = "🔴"
            else:
                pc_emoji = ""

            combo_header = f"• <b>Total: {total_price}€</b> {pc_emoji}"
            week_lines.append(combo_header)

            # format legs without per-leg prices; use emoji arrows for outbound/return
            dates = combo.get("date", [])
            origins = combo.get("origin", [])
            destinations = combo.get("destination", [])
            times = combo.get("time", [])
            airlines = combo.get("airline", [])
            stops = combo.get("stops", [])

            for i in range(2):
                d = dates[i]
                wd = weekday_abbr[dt.date.fromisoformat(d).weekday()]
                o = origins[i]
                dst = destinations[i]
                t = times[i]
                a = airlines[i]
                s = stops[i]

                arrow = "➡️" if i % 2 == 0 else "⬅️"
                # show date, route, time and airline, stops; omit per-leg price
                week_lines.append(f"{arrow} {d} ({wd}): {o} → {dst} | {t} | {a} | escalas: {s}")

            shown_in_week += 1
            total_shown += 1
            any_shown = True

        if shown_in_week:
            # send the week's results as a separate message
            week_text = "\n".join(week_lines)

            await update.message.reply_text(week_text, parse_mode=constants.ParseMode.HTML)

    if not any_shown:
        # no results
        reply_options = [["Sí", "No"]]
        markup = ReplyKeyboardMarkup(reply_options, one_time_keyboard=True)
        await update.message.reply_text("No se han encontrado combinaciones que cumplan el filtro. ¿Quieres probar con otro buscador?", reply_markup=markup)
        return DECISION_CONTINUE

    # ask whether to continue (send keyboard once)
    reply_options = [["Sí", "No"]]
    markup = ReplyKeyboardMarkup(reply_options, one_time_keyboard=True)
    await update.message.reply_text("¿Deseas realizar otra búsqueda?", reply_markup=markup)
    return DECISION_CONTINUE


@handle_error
async def discovery_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    decision = update.message.text.lower()
    if decision in ['sí', 'si', 'yes']:
        available_jobs = [[os.path.basename(f).replace("bargains_", "").replace(".json", "")] for f in glob.glob(f"{DATA_PATH}bargains_*.json")]
        
        markup = ReplyKeyboardMarkup(available_jobs, one_time_keyboard=True)
        text = ("Para continuar, selecciona otro de los buscadores de vuelos disponibles:"
                "(recuerda: para cancelar en cualquier momento, escribe /cancelar.)")
        
        await update.message.reply_text(text, reply_markup=markup)
        return JOB_SELECTION
    
    else:
        text = "¡Gracias por usar el buscador de vuelos!"
        
        await update.message.reply_text(text)
        return ConversationHandler.END


async def discovery_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Búsqueda cancelada. ¡Gracias por usar el buscador de vuelos!")
    return ConversationHandler.END
