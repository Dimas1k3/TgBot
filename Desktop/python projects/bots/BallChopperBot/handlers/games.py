import os
import asyncio
import time
import random
import sqlite3
import aiosqlite
import requests
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Message, ReplyKeyboardRemove, InputMediaPhoto
from telegram.ext import ContextTypes, MessageHandler, CallbackQueryHandler, filters, ConversationHandler


from app.data import (
    AWAITING_USER_INPUT,
    AWAITING_USER_INPUT_ANTICHEAT,
    AWAITING_USER_INPUT_21,
    WAITING_FOR_2048_MOVE,
    all_texts,
    image_text_map,
    game_deck,
    tiles,
    board_2048,
    BOARD_SIZE,
    CELL_SIZE,
    FONT_SIZE,
    COLORS,
    FONT,
    BORDER_COLOR,
    BACKGROUND_COLOR,
    symbol_list,
    photo_links
)

from handlers.helpers import add_to_wpm_leaderboard, get_from_wpm_leaderboard

conn = sqlite3.connect('games.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS wpm_leaderboard (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        wpm INTEGER NOT NULL
    )
''')

conn.commit()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS coldown_bj (
        id INTEGER NOT NULL,
        username TEXT NOT NULL,
        balance REAL NOT NULL,
        last_claim DATETIME NOT NULL
    )
''')

conn.commit()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS "2048_leaderboard" (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        score INTEGER NOT NULL
    )
''')

conn.commit()
conn.close()

# ==============================================================================================
# ТЕСТ НА СКОРОСТЬ ПЕЧАТИ (WPM)     DONE
# ==============================================================================================

async def wpm_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('ПРИГОТОВЬСЯ ПЕЧАТАТЬ ТЕКСТ!')
    await asyncio.sleep(0.5)
    for number in reversed(range(1, 4)):
        await update.message.reply_text(number)
        await asyncio.sleep(1)
    
    text = random.choice(all_texts)
    text_list = text.split()
    start_pos = random.randint(0, (len(text_list)-40))
    end_pos = start_pos
    words = []
    n = 0

    if (text_list[start_pos][0]).isupper() and (text_list[start_pos - 1][-1]) == '.':
        while n != 2: # для того, чтобы бот выдал 2 предложения юзеру
            while (text_list[end_pos][-1]) != '.': # поиск конца предложения
                end_pos += 1
            n += 1
            end_pos += 1
        for word in range(start_pos, end_pos):
            words.append(text_list[word])
    else:
        while not ((text_list[start_pos][0]).isupper() and (text_list[start_pos - 1][-1]) == '.'): # проверка на то, чтобы слово начиналось с большой буквы и перед ним была точка
            start_pos += 1
        end_pos = start_pos
        while n != 2:
            while (text_list[end_pos][-1]) != '.': # поиск конца предложения
                end_pos += 1
            n += 1
            end_pos += 1
        for word in range(start_pos, end_pos):
            words.append(text_list[word])

    sentence = ' '.join(words) 
    await update.message.reply_text(sentence)
    context.user_data["sentence"] = sentence
    context.user_data["start_time"] = time.time()

    return AWAITING_USER_INPUT
    
async def wpm_score(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int: 
    chat_id = update.message.chat_id
    user_text = update.message.text
    user_text_list = user_text.split()
    sentence_text = context.user_data.get("sentence")
    sentence_text_list = sentence_text.split()
    word_list = []
    word_counter = 0
    min_length = min(len(sentence_text_list), len(user_text_list))

    for i in range(min_length):
        if sentence_text_list[i] == user_text_list[i]:
            word_list.append(user_text_list[i])
            word_counter += 1

    end_time = time.time()
    start_time = context.user_data.get("start_time")
    
    words = ''.join(word_list)
    one_word = 0
    user_words = 0

    for j in words:
        one_word += 1
        if one_word == 5:
            user_words += 1
            one_word = 0
    if one_word > 5:
        user_words += 1
    
    # print(len(words))
    # print(user_words) 
    elapsed_time = end_time - start_time
    elapsed_minutes = elapsed_time / 60 
    accuracy = (word_counter / len(sentence_text_list)) * 100
    wpm = user_words / elapsed_minutes 
    wpm = int(wpm)

    if wpm > 100:
        image_url, text_for_image = random.choice(list(image_text_map.items()))
        context.user_data["text_for_image"] = text_for_image

        await update.message.reply_text('Мне кажется, ты читеришь, дружок')
        await asyncio.sleep(0.5)
        await update.message.reply_text(f'И я чет ваще не верю, что твой wpm равен {wpm}')
        await asyncio.sleep(0.5)
        await update.message.reply_text('Попробуй ка напечатать это')
        await context.bot.send_photo(chat_id=chat_id, photo=image_url)
        context.user_data["start_time_anticheat"] = time.time()
        return AWAITING_USER_INPUT_ANTICHEAT
    else:
        await update.message.reply_text(f'Количество правильных слов: {word_counter} из {len(sentence_text_list)}')
        await update.message.reply_text(f'Твоя точность: {int(accuracy)}%')
        await update.message.reply_text(f'Твой wpm: {wpm} cлов в минуту')
        username = update.message.from_user.first_name
        if wpm > 0:
            conn = sqlite3.connect('games.db')
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM "wpm_leaderboard" WHERE username = ?', (username))
            user = cursor.fetchone()

            if user[2] < wpm:
                await add_to_wpm_leaderboard(username, wpm)

        return ConversationHandler.END
    
async def wpm_anticheat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int: 
    chat_id = update.message.chat_id
    user_text = update.message.text
    text_for_image = context.user_data.get('text_for_image')
    user_text_list = user_text.split()
    text_for_image_list = text_for_image.split()
    min_length = min(len(text_for_image_list), len(user_text_list))
    word_list = []
    word_counter = 0

    for i in range(min_length):
        if text_for_image_list[i] == user_text_list[i]:
            word_list.append(user_text_list[i])
            word_counter += 1
            end_time = time.time()
    
    end_time = time.time()
    start_time = context.user_data.get("start_time_anticheat")
    
    words = ''.join(word_list)
    one_word = 0
    user_words = 0

    for j in words:
        one_word += 1
        if one_word == 5:
            user_words += 1
            one_word = 0
    if one_word > 5:
        user_words += 1
    
    username = update.message.from_user.first_name
    elapsed_time = end_time - start_time
    elapsed_minutes = elapsed_time / 60 
    accuracy = (word_counter / len(text_for_image_list)) * 100
    wpm = user_words / elapsed_minutes 
    wpm = int(wpm)

    if wpm >= 100:
        await update.message.reply_text(f'Признаю, твой wpm и правда равен {wpm}')
        await add_to_wpm_leaderboard(username, wpm)
    else:
        await update.message.reply_text(f'БРО, СЕРЬЕЗНО, ТВОЙ WPM ТОЛЬКО {wpm}????? GET GOOD NIGGA')
    
    return ConversationHandler.END

# ==============================================================================================
# КРЕСТИКИ-НОЛИКИ       REWORK??
# ==============================================================================================

async def tictactoe_lobby(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if context.chat_data.get('game_state') == True:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Игра уже идет, подожди')
        return
    else:
        handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_players_move)
        context.chat_data['move_handler'] = handler  # Сохраняем обработчик для удаления позже
        context.application.add_handler(handler)
        chat_id = update.message.chat_id
        #4 ключа из тг словаря для игроков
        context.chat_data['player1'] = None
        context.chat_data['player2'] = None
        context.chat_data['current_turn'] = 'player1'
        context.chat_data['game_state'] = True

        # создание интерактивных кнопок
        keyboard = [
            [InlineKeyboardButton("Игрок 1 (X)", callback_data='tictactoe_player1')],
            [InlineKeyboardButton("Игрок 2 (O)", callback_data='tictactoe_player2')]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Выберите игрока:',
            reply_markup=reply_markup
        )

        context.chat_data['tictactoe_keyboard'] = keyboard
        context.chat_data['tictactoe_message_id'] = message.message_id

async def choose_player(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    user = query.from_user

    await query.answer()
    # print(query)
    # print(user)

    new_keyboard = context.chat_data.get('tictactoe_keyboard')

    for i in range(1, 3):
        if query.data == f'tictactoe_player{i}':
            if i == 1 and context.chat_data.get(f'player{i + 1}') == user.id:
                pass
            
            elif i == 2 and context.chat_data.get(f'player{i - 1}') == user.id:
                pass

            elif context.chat_data.get(f'player{i}') is None:
                context.chat_data[f'player{i}'] = user.id
                context.chat_data[f'player{i}_name'] = user.first_name

                new_keyboard[int(f'{i - 1}')] = [InlineKeyboardButton(f"{user.first_name} (X)", callback_data=f'player{i}')]
                reply_markup = InlineKeyboardMarkup(new_keyboard)
                await query.edit_message_reply_markup(reply_markup=reply_markup)

    if context.chat_data.get('player1') is not None and context.chat_data.get('player2') is not None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Оба игрока выбраны, начинаем")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{context.chat_data['player1_name']} vs {context.chat_data['player2_name']}")
        await query.edit_message_reply_markup(reply_markup=None)
        board_state = await show_tictactoe_board()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=board_state)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{context.chat_data['player1_name']}, твой ход: ")
        await handle_players_move(update, context)

async def handle_players_move(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:  
    # print('handle_players_move started')
    global board
    user_id = update.message.from_user.id
    user_input = update.message.text
    # print(f"Message from {update.message.from_user.username}: {user_input}")  
    current_turn = context.chat_data['current_turn'] # передача хода от игроку к игроку
    
    if current_turn == 'player1' and context.chat_data['player1'] == user_id:
        try:
            choice = int(user_input)
            if board[choice - 1] != 'x' and board[choice - 1] != 'o':
                board[choice - 1] = 'x'
                board_state = await show_tictactoe_board()
                await context.bot.send_message(chat_id=update.effective_chat.id, text=board_state)

                for check in win:
                    if board[check[0]] == board[check[1]] == board[check[2]] == 'x':
                        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{context.chat_data['player1_name']} победил")
                        remove_move_handler(context)
                        context.chat_data['player1_name'] = "Игрок 1"
                        context.chat_data['player2_name'] = "Игрок 2"
                        board = [1, 2, 3, 4, 5, 6, 7, 8, 9]
                        context.chat_data['game_state'] = False
                        return
                    
                if await tictactoe_draw(update, context) == True:
                    return

                context.chat_data['current_turn'] = 'player2'
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{context.chat_data['player2_name']}, твой ход")
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text='ЗАНЯТО')
        except (ValueError, IndexError):
            pass
            # await context.bot.send_message(chat_id=update.effective_chat.id, text='НЕЛЬЗЯ')
    
    elif current_turn == 'player2' and context.chat_data['player2'] == user_id:
        try:
            choice = int(user_input)
            if board[choice - 1] != 'x' and board[choice - 1] != 'o':
                board[choice - 1] = 'o'
                board_state = await show_tictactoe_board()
                await context.bot.send_message(chat_id=update.effective_chat.id, text=board_state)

                for check in win:
                    if board[check[0]] == board[check[1]] == board[check[2]] == 'o':
                        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{context.chat_data['player2_name']} победил")
                        remove_move_handler(context) 
                        context.chat_data['player1_name'] = "Игрок 1"
                        context.chat_data['player2_name'] = "Игрок 2"
                        board = [1, 2, 3, 4, 5, 6, 7, 8, 9]
                        context.chat_data['game_state'] = False
                        return
                
                if await tictactoe_draw(update, context) == True:
                    return
                    
                context.chat_data['current_turn'] = 'player1'
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{context.chat_data['player1_name']}, твой ход")
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text='ЗАНЯТО')
        except (ValueError, IndexError):
            pass
            # await context.bot.send_message(chat_id=update.effective_chat.id, text='НЕЛЬЗЯ')

board = [1, 2, 3, 4, 5, 6, 7, 8, 9]
win = [[0,1,2], [3,4,5], [6,7,8], [0,3,6], [1,4,7], [2,5,8], [0,4,8], [2,4,6]]
async def show_tictactoe_board():
    return (f"{board[0]} | {board[1]} | {board[2]}\n" \
                f"------------\n" \
                f"{board[3]} | {board[4]} | {board[5]}\n" \
                f"------------\n" \
                f"{board[6]} | {board[7]} | {board[8]}")

async def tictactoe_draw(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global board
    board_str = ''.join(map(str, board))
    if not any(char.isdigit() for char in board_str):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="НИЧЬЯ")
        remove_move_handler(context)
        context.chat_data['player1_name'] = "Игрок 1"
        context.chat_data['player2_name'] = "Игрок 2"
        board = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        context.chat_data['game_state'] = False
        return True
    return False

def remove_move_handler(context):
    for handler in context.application.handlers[0]:
        if isinstance(handler, MessageHandler):
            context.application.remove_handler(handler)
            break

# ==============================================================================================
# ИГРА В ОЧКО   MAKE MULTIPLAYER
# ==============================================================================================

async def blackjack_lobby(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    host_id = update.effective_user.id 
    context.chat_data['host_id'] = host_id

    if context.chat_data.get('blackjack_lobby_state') == True:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Игра уже идет, подожди')
        return
    else:
        handler = MessageHandler(filters.TEXT & ~filters.COMMAND, choose_blackjack_players)
        context.chat_data['move_handler'] = handler  # Сохраняем обработчик для удаления позже
        context.application.add_handler(handler)
        chat_id = update.message.chat_id
        #4 ключа из тг словаря для игроков
        context.chat_data['player1'] = None
        context.chat_data['player2'] = None
        context.chat_data['player3'] = None
        context.chat_data['player4'] = None
        context.chat_data['blackjack_lobby_state'] = True
        context.chat_data['bj_player_list'] = []
        context.chat_data['bet_player_list'] = []

        # создание интерактивных кнопок
        keyboard = [
            [InlineKeyboardButton("Игрок 1", callback_data='blackjack_player1')],
            [InlineKeyboardButton("Игрок 2", callback_data='blackjack_player2')],
            [InlineKeyboardButton("Игрок 3", callback_data='blackjack_player3')],
            [InlineKeyboardButton("Игрок 4", callback_data='blackjack_player4')]
        ]

        context.chat_data['bj_current_keyboard'] = keyboard

        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Лобби BlackJack:',
            reply_markup=reply_markup
        )

        text = ['Каждый игрок должен поставить стою ставку', 'Чтобы начать игру, Хост должен ввести команду /start_bj']
        for words in text:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=words
            )
            await asyncio.sleep(0.1)

        context.chat_data['blackjack_message_id'] = message.message_id

async def choose_blackjack_players(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    # chat_id = query.message.chat_id
    user = query.from_user

    await query.answer()

    new_keyboard = context.chat_data.get('bj_current_keyboard')

    for i in range(1, 5):
        player_key = f"player{i}"
        callback_key = f"blackjack_player{i}"

        if query.data == callback_key:
            for j in range(1, 5):
                if context.chat_data.get(f'player{j}') == user.id:
                    break

            else:
                if context.chat_data.get(player_key) is None:
                    context.chat_data[player_key] = user.id
                    context.chat_data[f'{player_key}_name'] = user.first_name
                    
                    new_keyboard = context.chat_data.get('bj_current_keyboard')
                    new_keyboard[i-1][0] = InlineKeyboardButton(f"{user.first_name}", callback_data=callback_key)
                    context.chat_data['bj_current_keyboard'] = new_keyboard
                                
                    reply_markup = InlineKeyboardMarkup(new_keyboard)

                    if context.chat_data.get('player_count') is None:
                        context.chat_data['player_count'] = 1
                    else:
                        context.chat_data['player_count'] += 1
                    
                    context.chat_data['bj_player_list'].append(user.id)
                    await context.bot.edit_message_reply_markup(chat_id=update.effective_chat.id,  message_id=context.chat_data['blackjack_message_id'], reply_markup=reply_markup)

async def start_bj(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # a = context.chat_data.get('player_count')
    # print(f"Людей в лобби: {a}")   
    user_id = update.effective_user.id 
    host_id = context.chat_data.get('host_id') 

    if user_id == host_id:
        if int(context.chat_data.get('player_count', 0)) >= 1 and len(context.chat_data['bj_player_list']) == len(context.chat_data['bet_player_list']):
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text = 'Игра началась'
            )

            context.chat_data['blackjack_game_state'] = True

            await context.bot.edit_message_reply_markup(
                chat_id=update.effective_chat.id,
                message_id=context.chat_data['blackjack_message_id'],
                reply_markup=None
                )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text = 'Бро, выполни все условия'
            )
        print(context.chat_data['bj_player_list'])
        print(context.chat_data['bet_player_list'])
        print(context.chat_data['player1'])
    else:
        pass

async def bet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    
    if context.chat_data.get('blackjack_lobby_state') is None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text = 'Братан, какая ставка, игра даже не идет')
        return
        
    if user_id in context.chat_data['bj_player_list'] and context.chat_data.get('blackjack_game_state') is None:
        message = update.message.text
        parts = message.split(' ')
            
        if len(parts) != 2 or not parts[1].isdigit():
            await context.bot.send_message(chat_id=update.effective_chat.id, text = 'Бро, это не ставка')
            return
        else:
            user_bet = int(parts[1])
                
    if await check_user_balance(user_id, user_bet) == False and user_id not in context.chat_data['bet_player_list']:
            await context.bot.send_message(chat_id=update.effective_chat.id, text='Бро, у тебя нет столько денег')
            return

    if await check_user_balance(user_id, user_bet) == True and user_id not in context.chat_data['bet_player_list']:
        await update_user_balance(user_id, user_bet)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'{user_name}, ваша ставка в размере {user_bet} принята')
        context.chat_data['bet_player_list'].append(user_id)
                
async def check_user_balance(user_id, user_bet):
    conn = sqlite3.connect('games.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM coldown_bj WHERE id = ?', (user_id,))
    user = cursor.fetchone()

    user_balance = user[2]

    if user_balance >= user_bet:
        return True
    else:
        return False

async def update_user_balance(user_id, user_bet):
    conn = sqlite3.connect('games.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM coldown_bj WHERE id = ?', (user_id,))
    user = cursor.fetchone()

    user_balance = user[2]

    new_balance = user_balance - user_bet
    cursor.execute('UPDATE coldown_bj SET balance = ? WHERE id = ?', (new_balance, user_id))
    conn.commit()

async def claim(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    '''
        id INTEGER NOT NULL,
        username TEXT NOT NULL,
        balance REAL NOT NULL,
        last_claim DATETIME NOT NULL
    '''

    conn = sqlite3.connect('games.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM coldown_bj WHERE id = ?', (user_id,))
    user = cursor.fetchone()

    if user is None:
        balance = random.randint(250,500)
        last_claim = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('INSERT INTO coldown_bj (id, username, balance, last_claim) VALUES (?, ?, ?, ?)', 
                       (user_id, user_name, balance, last_claim))
        conn.commit()
        
        await context.bot.send_message(chat_id=update.effective_chat.id, 
                text=f'Привет, новенький, твой стартовый баланс {balance}')
    else:
        cursor.execute('SELECT * FROM coldown_bj WHERE id = ?', (user_id,))
        row = cursor.fetchone() 
        print(row)

        last_claim = datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S') 
        current_time = datetime.now()
        
        time_difference = (current_time - last_claim).total_seconds() / 3600

        if time_difference >= 3:
            to_add = random.randint(75,150)
            new_balance = int(row[2]) + to_add 
            cursor.execute('UPDATE coldown_bj SET balance = ?, last_claim = ? WHERE id = ?', 
                               (new_balance, time.strftime('%H:%M:%S'), user_id))
            conn.commit()

            await context.bot.send_message(chat_id=update.effective_chat.id, 
                text=f'Тебе выпало {to_add} хомячков, твой новый баланс: {new_balance:.0f} хомячков')
        else:
            remaining_time = 3 - time_difference
            hours = int(remaining_time)
            minutes = int((remaining_time - hours) * 60)

            if hours == 1:
                hour_word = "час"
            elif 2 <= hours  <= 4:
                hour_word = "часа"
            else:
                hour_word = "часов"

            if minutes == 1:
                minute_word = "минута"
            elif 2 <= minutes <= 4:
                minute_word = "минуты"
            else:
                minute_word = "минут"
           
            if hours > 0 and minutes > 0:
                text=f'Подожди еще {hours} {hour_word} и {minutes} {minute_word}'
            elif hours > 0:
                text = f'Подожди еще {hours} {hour_word}'
            else:
                text = f'Подожди еще {minutes} {minute_word}'

            await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
            
    conn.close()

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    conn = sqlite3.connect('games.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM coldown_bj WHERE id = ?', (user_id,))
    user = cursor.fetchone()

    try:
        balance = user[2]  
        await context.bot.send_message(chat_id=update.effective_chat.id, 
                           text=f'Твой баланс: {balance} хомячков')
    except TypeError:
        await context.bot.send_message(chat_id=update.effective_chat.id, 
                                        text=f'Бро, у тебя 0 на счету, команда /claim в помощь, нищ')

async def game_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if context.chat_data.get('BlacKJackState') == True:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Игра уже идет, подожди')
        return
    else:
        cards = game_deck.copy()
        context.chat_data['BlacKJackState'] = True

        # функция для выбора двух рандомных карт для игрока и крупье
        player_cards, bot_cards, current_stage = await start_cards(update, context, cards)

        # функция, чтобы показать карты игроку
        player_cards_list, bot_cards_list  = await show_start_cards(update, context, player_cards, bot_cards)

        user_score = 0
        bot_score = 0

        # считаем, сколько очков уже есть у игрока
        for score1 in player_cards.values():
            user_score += score1
        
        for score2 in bot_cards.values():
            bot_score += score2

        context.user_data['user_score'] = user_score
        context.user_data['bot_score'] = bot_score
        context.user_data['bot_cards_list'] = bot_cards_list
        context.user_data['cards'] = cards
        context.chat_data['BlacKJackState'] = True
        
        if user_score == 21 and bot_score != 21:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Вы набрали 21 очко и победили")
            context.chat_data['BlacKJackState'] = False
            return ConversationHandler.END
        elif user_score != 21 and bot_score == 21:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Крупье набрал 21 очко и победил")
            context.chat_data['BlacKJackState'] = False
            return ConversationHandler.END
        elif user_score == 21 and bot_score == 21:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Ничья, у всех 21 очко")
            context.chat_data['BlacKJackState'] = False
            return ConversationHandler.END

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Будете брать карту? Да/нет"
        )

        return AWAITING_USER_INPUT_21

async def start_cards(update, context, cards):
    player_cards = {}
    bot_cards = {}

    while len(player_cards) < 2:
        card, value = random.choice(list(cards.items()))
        player_cards[card] = value
        del cards[card]

    while len(bot_cards) < 2:
        card, value = random.choice(list(cards.items()))
        bot_cards[card] = value
        del cards[card]

    return player_cards, bot_cards, AWAITING_USER_INPUT_21

async def show_start_cards(update, context, player_cards, bot_cards):
    player_cards_list = []
    bot_cards_list = []
    
    # добавляем все карты, которые цифры
    for card, value in player_cards.items():
        if card.isdigit():
            player_cards_list.append(card)
    
    # если остались карты, которые не цифры, добавляем их
    if len(player_cards_list) != 2:
        for card, value in player_cards.items():
            if not card.isdigit():
                player_cards_list.append([card, value])

    # тож самое, но для карт крупье
    for card, value in bot_cards.items():
        if card.isdigit():
            bot_cards_list.append(card)
    
    if len(bot_cards_list) != 2:
        for card, value in bot_cards.items():
            if not card.isdigit():
                bot_cards_list.append([card, value])

    if not player_cards_list[0][0].isdigit() and not player_cards_list[1][0].isdigit():
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                f"Вам выпали карты: {player_cards_list[0][0]} номиналом {player_cards_list[0][1]} "
                f"и {player_cards_list[1][0]} номиналом {player_cards_list[1][1]}"
            )
        )
    elif player_cards_list[0].isdigit() and not player_cards_list[1][0].isdigit():
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                f"Вам выпали карты: {player_cards_list[0]} "
                f"и {player_cards_list[1][0]} номиналом {player_cards_list[1][1]}"
            )
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Вам выпали карты: {player_cards_list[0]} и {player_cards_list[1]}"
        )

    if not bot_cards_list[0][0].isdigit() and not bot_cards_list[1][0].isdigit():
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Крупье выпала карта - {bot_cards_list[0][0]} номиналом {bot_cards_list[0][1]}, вторая скрыта"
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Крупье выпала карта - {bot_cards_list[0]}, вторая скрыта"
        )

    return player_cards_list, bot_cards_list

async def pick_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_choice = update.message.text.strip().lower()

    user_score = context.user_data['user_score']
    bot_score = context.user_data['bot_score']
    bot_cards_list = context.user_data['bot_cards_list']
    cards = context.user_data['cards']

    if user_choice == 'да':
        card, value = random.choice(list(cards.items()))
        if card.isdigit():
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Вам выпала карта - {card}"
            )
            user_score += value
            context.user_data['user_score'] = user_score
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Вам выпала карта {card} номиналом {value}"
            )
            if card == 'Туз':
                if user_score + 11 > 21:
                    user_score += 1
                    context.user_data['user_score'] = user_score
                else:
                    user_score += value
                    context.user_data['user_score'] = user_score
            else:
                user_score += value
                context.user_data['user_score'] = user_score

        del cards[card]
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Ваш текущий счет: {user_score}"
        )

        if user_score > 21:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Вы проиграли, потому что набрали больше 21 очка"
            )
            context.chat_data['BlacKJackState'] = False
            return ConversationHandler.END
        elif user_score == 21:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Вы набрали 21 очко и выиграли"
            )
            context.chat_data['BlacKJackState'] = False
            return ConversationHandler.END
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Будете брать ещё карту? Да/нет"
            )
            return AWAITING_USER_INPUT_21
    
    elif user_choice == 'нет':
        await bot_pick_card(update, context, user_score, bot_score, bot_cards_list, cards)
        return ConversationHandler.END

    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Пожалуйста, ответьте 'Да' или 'Нет'."
        )
        return AWAITING_USER_INPUT_21

async def bot_pick_card(update, context, user_score, bot_score, bot_cards_list, cards):
    user_score = context.user_data['user_score']
    bot_score = context.user_data['bot_score']
    
    if not bot_cards_list[0][0].isdigit() and not bot_cards_list[1][0].isdigit():
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                f"Крупье выпали карты: {bot_cards_list[0][0]} номиналом {bot_cards_list[0][1]} "
                f"и {bot_cards_list[1][0]} номиналом {bot_cards_list[1][1]}"
            )
        )
    elif bot_cards_list[0][0].isdigit() and not bot_cards_list[1][0].isdigit():
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                f"Крупье выпали карты: {bot_cards_list[0]} и {bot_cards_list[1][0]} "
                f"номиналом {bot_cards_list[1][1]}"
            )
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Крупье выпали карты {bot_cards_list[0]} и {bot_cards_list[1]}"
        )

    # if bot_score > user_score:
    
    if await check_bot_win(update, context, user_score, bot_score):     # Эту функцию стоит исправить, так как иногда крупье имея 16 может не брать карту
        context.chat_data['BlacKJackState'] = False
        return

    if bot_score < 17:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Крупье берет карту")
        await asyncio.sleep(0.7)

    while bot_score < 17:
        card, value = random.choice(list(cards.items()))

        if card.isdigit():
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Крупье выпала карта - {card}"
            )
            bot_score += value
            del cards[card]
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"У крупье {bot_score} очков"
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Крупье выпала карта {card} номиналом {value}"
            )
            if card == 'Туз':
                if bot_score + 11 > 21:
                    bot_score += 1
                else:
                    bot_score += value
                del cards[card]
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"У крупье {bot_score} очков"
                )
            else:
                bot_score += value
                del cards[card]
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"У крупье {bot_score} очков"
                )

        if bot_score >= 17:
            break

    if user_score > bot_score:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Вы набрали {user_score} очков, крупье набрал {bot_score}, Вы победили"
        )
    else:
        await check_bot_win(update, context, user_score, bot_score)
        context.chat_data['BlacKJackState'] = False

async def check_bot_win(update, context, user_score, bot_score):
    if bot_score == 21:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Крупье набрал 21 очко и победил"
        )
        return True
    elif bot_score > 21:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Крупье набрал больше 21 очка и Вы победили"
        )
        return True
    elif bot_score >= 17 and bot_score > user_score:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Крупье набрал {bot_score} очков и победил Вас"
        )
        return True
    elif bot_score == user_score:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Ничья, Вы с крупье оба набрали по {user_score} очков"
        )
        return True
    return False

# ==============================================================================================
# 2048      MAKE LEADERBOARD AND SCORE
# ==============================================================================================

score_2048 = 0

def spawn_number():
    empty_cells = []
    
    for row in range(4):
        for col in range(4):
            if board_2048[row][col] == 0:
                empty_cells.append((row, col))

    if not empty_cells:
        return
    
    while True:
        row = random.randint(0, 3)
        col = random.randint(0, 3)
        if board_2048[row][col] == 0:
            tile = random.choice([2, 4])
            board_2048[row][col] = tile
            break

def print_board():
    result = ""
    for row in board_2048:
        result += " ".join(map(str, row)) + "\n"
    return result

def move_up():
    global score_2048
    
    for row in range(len(board_2048)):
        for col in range(4):
            if board_2048[row][col] != 0:
                new_row = row

                while new_row != 0 and board_2048[new_row - 1][col] == 0:  # Сдвиг, если клетка сверху 0
                    board_2048[new_row - 1][col] = board_2048[new_row][col]
                    board_2048[new_row][col] = 0
                    new_row = new_row - 1

                if new_row != 0 and board_2048[new_row - 1][col] == board_2048[new_row][col]:  # Слияние, если клетка сверху не 0
                    board_2048[new_row - 1][col] = board_2048[new_row - 1][col] * 2
                    score_2048 += board_2048[new_row - 1][col]
                    board_2048[new_row][col] = 0

def move_down():
    global score_2048
    
    for row in reversed(range(len(board_2048))):
        for col in range(4):
            if board_2048[row][col] != 0:
                new_row = row

                while new_row != 3 and board_2048[new_row + 1][col] == 0:
                    board_2048[new_row + 1][col] = board_2048[new_row][col]
                    board_2048[new_row][col] = 0
                    new_row = new_row + 1

                if new_row != 3 and board_2048[new_row + 1][col] == board_2048[new_row][col]:
                    board_2048[new_row + 1][col] = board_2048[new_row + 1][col] * 2
                    score_2048 += board_2048[new_row + 1][col]
                    board_2048[new_row][col] = 0

def move_right():
    global score_2048
    
    for row in range(len(board_2048)):
        for col in reversed(range(4)):
            if board_2048[row][col] != 0:
                new_col = col

                while new_col != 3 and board_2048[row][new_col + 1] == 0:
                    board_2048[row][new_col + 1] = board_2048[row][new_col]
                    board_2048[row][new_col] = 0
                    new_col = new_col + 1

                if new_col != 3 and board_2048[row][new_col + 1] == board_2048[row][new_col]:
                    board_2048[row][new_col + 1] = board_2048[row][new_col + 1] * 2
                    score_2048 += board_2048[row][new_col + 1]
                    board_2048[row][new_col] = 0

def move_left():
    global score_2048
    
    for row in range(len(board_2048)):
        for col in range(4):
            if board_2048[row][col] != 0:
                new_col = col

                while new_col != 0 and board_2048[row][new_col - 1] == 0:
                    board_2048[row][new_col - 1] = board_2048[row][new_col]
                    board_2048[row][new_col] = 0
                    new_col = new_col - 1

                if new_col != 0 and board_2048[row][new_col - 1] == board_2048[row][new_col]:
                    board_2048[row][new_col - 1] = board_2048[row][new_col - 1] * 2
                    score_2048 += board_2048[row][new_col - 1]
                    board_2048[row][new_col] = 0

def draw_board(board_2048):
    img = Image.new("RGB", (BOARD_SIZE, BOARD_SIZE), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)

    for row in range(4):
        for col in range(4):
            value = board_2048[row][col]
            color = COLORS.get(value, (BACKGROUND_COLOR)) 
            x0 = col * CELL_SIZE
            y0 = row * CELL_SIZE
            x1 = x0 + CELL_SIZE
            y1 = y0 + CELL_SIZE

            draw.rectangle([x0, y0, x1, y1], fill=color, outline=BORDER_COLOR, width=5)

            if value != 0:
                text = str(value)
                bbox = draw.textbbox((0, 0), text, font=FONT)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                text_x = x0 + (CELL_SIZE - text_width) / 2
                text_y = y0 + (CELL_SIZE - text_height) / 2
                draw.text((text_x, text_y), text, fill="black", font=FONT)

    return img

async def game_2048(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    user_name = update.effective_user.name
    global score_2048

    context.chat_data['2048_game_player_id'] = user_id
    context.chat_data['2048_game_player_name'] = user_name

    if context.chat_data.get('2048_game_state') == True:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Игра уже идет, подожди')
        return
    else:
        context.chat_data['2048_game_state'] = True

        for _ in range(2):
            spawn_number()
        
        img = draw_board(board_2048)

        output = BytesIO()
        img.save(output, format="PNG")
        output.seek(0)

        keyboard = [
            [
                InlineKeyboardButton("⬛️", callback_data="skip"), 
                InlineKeyboardButton("⬆️", callback_data="up"), 
                InlineKeyboardButton("⬛️", callback_data="skip")
            ],
            [
                InlineKeyboardButton("⬅️", callback_data="left"), 
                InlineKeyboardButton("⬛️", callback_data="skip"), 
                InlineKeyboardButton("➡️", callback_data="right")
            ],
            [
                InlineKeyboardButton("⬛️", callback_data="skip"), 
                InlineKeyboardButton("⬇️", callback_data="down"), 
                InlineKeyboardButton("⬛️", callback_data="skip")
            ]
        ] 

        reply_markup = InlineKeyboardMarkup(keyboard)

        message = await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=output,
            caption=f"Твой счет: {score_2048}",
            reply_markup=reply_markup
        )

        context.chat_data['2048_keyboard'] = keyboard
        context.chat_data['2048_message_id'] = message.message_id
        output.close()

async def check_end_2048(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    c = 0
    move_possible = False

    for row in range(len(board_2048)):
        for col in range(4):
            if board_2048[row][col] == 2048:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text='ПОБЕДА'
                )
                return True

            if board_2048[row][col] != 0:
                c += 1

            if row > 0 and board_2048[row][col] == board_2048[row - 1][col]:  
                move_possible = True
            if row < 3 and board_2048[row][col] == board_2048[row + 1][col]:  
                move_possible = True
            if col > 0 and board_2048[row][col] == board_2048[row][col - 1]:  
                move_possible = True
            if col < 3 and board_2048[row][col] == board_2048[row][col + 1]:  
                move_possible = True

    if c == 16 and not move_possible:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='ПОРАЖЕНИЕ'
        )
        return True

    return False

async def update_game_board(update: Update, context: ContextTypes.DEFAULT_TYPE, c) -> None:
    global score_2048
    
    img = draw_board(board_2048)

    output = BytesIO()
    img.save(output, format="PNG")
    output.seek(0)

    keyboard = context.chat_data.get('2048_keyboard')
    message_id = context.chat_data.get('2048_message_id')
    # print(keyboard)
    # print(message_id)

    if keyboard and message_id and c == 0:
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.edit_message_media(
            chat_id=update.effective_chat.id,
            message_id=message_id,
            media=InputMediaPhoto(output, caption=f"Счет: {score_2048}"),
            reply_markup=reply_markup
        )

    elif keyboard and message_id and c == 1:
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.edit_message_media(
            chat_id=update.effective_chat.id,
            message_id=message_id,
            media=InputMediaPhoto(output, caption=f"Счет: {score_2048}"),
            reply_markup=None
        )

    output.close()

async def handle_2048_move(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global score_2048
    global board_2048
    query = update.callback_query
    action = query.data
    c = 0

    await query.answer()

    user_id = query.from_user.id
    player_id = context.chat_data.get('2048_game_player_id')

    if action == "up" and user_id == player_id:
        move_up()
    elif action == "down" and user_id == player_id:
        move_down()
    elif action == "left" and user_id == player_id:
        move_left()
    elif action == "right" and user_id == player_id:
        move_right()
    elif action == "skip" and user_id == player_id:
        await update_game_board(update, context, c)
        return
    
    if user_id == player_id:
        spawn_number()

    # for row in board_2048:
    #     print(row)
    # print('---------------------')

    if await check_end_2048(update, context) == True:
        c = 1

        await context.bot.edit_message_reply_markup(
        chat_id=update.effective_chat.id,
        message_id=context.chat_data['2048_message_id'],  
        reply_markup=None  
        )

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="ГГ, НИГА"
        )

        await update_2048_leaderboard(update,context, c)

        context.chat_data['2048_game_state'] = False
        score_2048 = 0
        board_2048 = [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]

        return

    await update_game_board(update, context, c)

async def update_2048_leaderboard(update, context):
    global score_2048
    user_id = context.chat_data.get('2048_game_player_id')
    user_name = context.chat_data.get('2048_game_player_name')
    
    '''
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        score INTEGER NOT NULL
    '''

    conn = sqlite3.connect('games.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM "2048_leaderboard" WHERE id = ?', (user_id,))
    user = cursor.fetchone()

    if user is None:
        cursor.execute('INSERT INTO "2048_leaderboard" (id, username, score) VALUES (?, ?, ?)', 
                       (user_id, user_name, score_2048))
        conn.commit()
    else:
        if user[2] < score_2048:
            cursor.execute('UPDATE "2048_leaderboard" SET SCORE = ? WHERE id = ?', (score_2048, user_id,))
            conn.commit()
        
# ==============================================================================================
# СЛОТЫ
# ==============================================================================================

async def spin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    text = update.message.text

    parts = text.split()

    if len(parts) < 2:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="ТЫ ЕБЛАН, НАДО ТАК -> '/spin 30'")
    else:
        try:
            user_bet = int(parts[1])
        except ValueError:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"ЭТО НЕ СТАВКА"
            )
            return

        await draw_slots(update, context, user_bet)

        # if await check_user_balance(user_id, user_bet) == True:
        #     await update_user_balance(user_id, user_bet)
        #     await draw_slots(update, context, user_bet)
        #     return
        # else:
        #     await context.bot.send_message(
        #         chat_id=update.effective_chat.id,
        #         text=f"ТЫ СЛИШКОМ НИЩИЙ, БРО"
        #     )
        #     return

async def draw_slots(update, context, user_bet) -> None:
    lst = []
            
    for _ in range(3):
        random_symbol = random.choice(symbol_list)
        lst.append(random_symbol)

    await check_slots_win(update, context, lst, user_bet)

    # result = " | ".join(lst)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Ставка: {user_bet}"
    )

    width, height = 400, 200

    img = Image.new("RGB", (width, height), "black")  
    draw = ImageDraw.Draw(img)

    line_thickness = 5  
    line1_x = width // 3  
    line2_x = (width // 3) * 2  

    draw.rectangle([(line1_x, 0), (line1_x + line_thickness, height)], fill="white")
    draw.rectangle([(line2_x, 0), (line2_x + line_thickness, height)], fill="white")

    start_x = 18
    step_x = width // 3
    y = (height // 2) - 45
    font = ImageFont.truetype("arial.ttf", 50)

    for i, symbol in enumerate(lst):
        x = start_x + i * step_x
        response = requests.get(photo_links[symbol])
        photo = Image.open(BytesIO(response.content))

        photo = photo.resize((100, 100))

        img.paste(photo, (x, y))

    output = BytesIO()
    img.save(output, format="PNG")
    output.seek(0)

    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=output)

    output.close()

async def check_slots_win(update, context, user_bet) -> None:
    pass