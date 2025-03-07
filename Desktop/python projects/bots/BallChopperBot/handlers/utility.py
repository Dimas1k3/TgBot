import asyncio
import requests
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
import google.generativeai as genai

from app.data import (
    ASKING,
    COUNTING,
    COINMARKETCAP_KEY,
    AWAITING_USER_INPUT_PRANK
)

# ==============================================================================================
# СПАМ В ЧАТ
# ==============================================================================================

async def ddos_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Введи сообщение, которое я буду спамить в чат: ')
    return ASKING

async def counter_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['target'] = update.message.text # Контект.юзер.дата это словарь от телеграма, где можно хранить любые данные от пользователя
    await update.message.reply_text('Введи количество сообщений, которое я буду спамить в чат: ')
    return COUNTING

# Проверка на то, чтобы юзер написал число, а не сообщение
async def handle_target(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        count = int(update.message.text)
    except ValueError:
        await update.message.reply_text('ЕБАНАТ, ЧИСЛО ВВЕДИ, А НЕ ВОТ ЭТУ ХУЙНЮ')
        return COUNTING
    
    if count > 25:
        await update.message.reply_text('Не, чет слишком много, мне лень')
        return ConversationHandler.END

    # из телеграм словаря достаем сообщение от юзера с прошлого этапа диалога
    target = context.user_data['target']
    
    for _ in range(count):
        await update.message.reply_text(target)
        await asyncio.sleep(0.5)
    return ConversationHandler.END

# ==============================================================================================
# ЦЕНА КРИПТЫ
# ==============================================================================================

# Получение названия койна от юзера
async def crypto_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    command_text = update.message.text
    parts = command_text.split()

    if len(parts) != 2:
        await update.message.reply_text('Пожалуйста, используйте команду в формате: /crypto <символ>, например: /crypto HMSTR')
    else:
        crypto = parts[1].upper() 
        price = await get_crypto_price(crypto)
        await update.message.reply_text(price)

# Получение цены нужного койна
async def get_crypto_price(crypto: str) -> str:
    symbol = crypto.upper()
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {'symbol': symbol}
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': COINMARKETCAP_KEY,
    }

    try:
        response = requests.get(url, headers=headers, params=parameters)
        response.raise_for_status()  
        data = response.json()
        price = data['data'][symbol]['quote']['USD']['price']
        return f'Текущая цена {symbol} составляет ${price:.6f}'
    except requests.exceptions.RequestException as e:
        return f"Ошибка при запросе к API: {e}"
    except KeyError:
        return "Не удалось найти цену для указанной криптовалюты"

# ==============================================================================================
# ОБРАЩЕНИЕ К ГЕЙМИНИ (ИИ)
# ==============================================================================================
    
async def Ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ai_promt = update.message.text
    parts = ai_promt.split()

    if len(parts) != 2:
        await update.message.reply_text('Пожалуйста, используйте команду в формате: /ask <вопрос>')
    else:
        genai.configure(api_key="AIzaSyCcxG29V4B5rv27tQYsrKeEbwmMipbukM8")
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(parts[1]) 
        await update.message.reply_text(response.text)

# ==============================================================================================
# CАМАЯ ЛУЧШАЯ КОМАНДА ДЛЯ ПРАНКА
# ==============================================================================================

async def prank_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = await context.bot.send_message(chat_id=update.effective_chat.id, text="Ты тапал хомячка?")
    message_id = message.message_id
    context.chat_data["prank_message_id"] = message_id
    return AWAITING_USER_INPUT_PRANK

async def prank_answer_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = update.message.text.lower()
    user_answer_id = update.message.message_id
    context.chat_data["counter"] = context.chat_data.get("counter", 0)

    if answer == 'да':
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=context.chat_data["prank_message_id"],
            text="Сосал?"
        )

        await update.message.reply_text('Ебать ты тупой')
        
        await context.bot.forward_message(
            chat_id=update.effective_chat.id,
            from_chat_id=update.effective_chat.id,
            message_id=context.chat_data["prank_message_id"]
        )

        await context.bot.forward_message(
            chat_id=update.effective_chat.id,
            from_chat_id=update.effective_chat.id,
            message_id=user_answer_id
        )

        return ConversationHandler.END
    else:
        context.chat_data["counter"] += 1
        if context.chat_data["counter"] < 5:
            await prank_command(update, context)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Не, ты реально даун")
            return ConversationHandler.END