from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
import sqlite3

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Дарова, чудик лысый, че тебе надо')

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("СТОП")
    return ConversationHandler.END

async def add_to_wpm_leaderboard(username, wpm):
    conn = sqlite3.connect('games.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO wpm_leaderboard (username, wpm)
        VALUES (?, ?)
    ''', (username, wpm))
    conn.commit()
    conn.close()

async def get_from_wpm_leaderboard():
    conn = sqlite3.connect('games.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM wpm_leaderboard ORDER BY wpm DESC")
    output = cursor.fetchmany(5)
    conn.close()
    return output
    
async def print_wpm_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    leaderboard = await get_from_wpm_leaderboard()
    leaderboard_list = []
    
    for rank, top in enumerate(leaderboard, start=1):
        leaderboard_list.append(f"{rank}. {top[1]}, WPM: {top[2]}")

    leaderboard_text = 'Топ лузеров с самым огромным WPM:\n'
    leaderboard_text += "\n".join(leaderboard_list)

    await context.bot.send_message(chat_id=chat_id, text=leaderboard_text)

async def get_from_2048_leaderboard():
    conn = sqlite3.connect('games.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM "2048_leaderboard" ORDER BY score DESC')
    output = cursor.fetchmany(5)
    conn.close()
    return output

async def print_2048_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    leaderboard = await get_from_2048_leaderboard()
    leaderboard_list = []
    
    for rank, top in enumerate(leaderboard, start=1):
        leaderboard_list.append(f"{rank}. {top[1]}, SCORE: {top[2]}")

    leaderboard_text = 'Топ лузеров с самым огромным счетом в 2048:\n'
    leaderboard_text += "\n".join(leaderboard_list)

    await context.bot.send_message(chat_id=chat_id, text=leaderboard_text)