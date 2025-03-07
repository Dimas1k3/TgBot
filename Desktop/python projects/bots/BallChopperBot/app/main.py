from telegram import BotCommand
import sys, os, asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
print(sys.path)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler,
) 

from handlers.games import (
    game_command,
    pick_card,
    AWAITING_USER_INPUT_21,
    tictactoe_lobby,
    choose_player,
    wpm_command,
    wpm_score,
    wpm_anticheat,
    AWAITING_USER_INPUT,
    AWAITING_USER_INPUT_ANTICHEAT,
    blackjack_lobby,
    choose_blackjack_players,
    start_bj,
    bet,
    claim,
    balance,
    game_2048,
    WAITING_FOR_2048_MOVE,
    handle_2048_move,
    spin
)

from handlers.helpers import start, cancel, print_wpm_leaderboard, print_2048_leaderboard

from handlers.media import handle_tik_tok, tiktok_command, get_tiktok_video_url, download_video, mp3_command

from handlers.utility import (
    ddos_command,
    counter_command,
    handle_target,
    ASKING,
    COUNTING,
    crypto_command,
    Ai_command,
    prank_command,
    prank_answer_command,
    AWAITING_USER_INPUT_PRANK
)

from app.data import TOKEN 

async def main():
    application = Application.builder().token(TOKEN).read_timeout(30).write_timeout(30).build()

    await application.bot.set_my_commands([
        BotCommand("tiktok", "Для тик ток кидов"),
        BotCommand("ddos", "Спам в чат"),
        BotCommand("wpm", "WPM тест"),
        BotCommand("crypto", "Показать цены криптовалют"),
        BotCommand("ask", "Задать вопрос ИИ"),
        BotCommand("mp3", "Конвертировать ютуб ссылку в MP3"),
        BotCommand("top", "Показать лидерборд WPM теста"),
        BotCommand("game", "Начать игру в крестики-нолики с другим игроком"),
        BotCommand("prank", "Пранк"),
        BotCommand("blackjack", "Игра в 21 очко")
    ])

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('ddos', ddos_command)],
        states={
            ASKING: [MessageHandler(filters.TEXT & ~filters.COMMAND, counter_command)],
            COUNTING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_target)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    wpm_handler = ConversationHandler(
        entry_points=[CommandHandler('wpm', wpm_command)],
        states={
            AWAITING_USER_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, wpm_score)],
            AWAITING_USER_INPUT_ANTICHEAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, wpm_anticheat)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    prank_handler = ConversationHandler(
        entry_points=[CommandHandler('prank', prank_command )],
        states={
            AWAITING_USER_INPUT_PRANK: [MessageHandler(filters.TEXT & ~filters.COMMAND, prank_answer_command )],
        },
        fallbacks=[]
    )

    game_21 = ConversationHandler(
        entry_points=[CommandHandler('bj', game_command )],
        states={
            AWAITING_USER_INPUT_21: [MessageHandler(filters.TEXT & ~filters.COMMAND, pick_card)],
        },
        fallbacks=[]
    )

    game_2048_handler = ConversationHandler(
        entry_points=[CommandHandler('2048', game_2048)],
        states={
            WAITING_FOR_2048_MOVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_2048_move)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(CommandHandler("start_bj", start_bj))
    application.add_handler(CommandHandler("tiktok", tiktok_command))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("crypto", crypto_command)) 
    application.add_handler(CommandHandler("ask", Ai_command))
    application.add_handler(CommandHandler("mp3", mp3_command))
    application.add_handler(CommandHandler("top_wpm", print_wpm_leaderboard))
    application.add_handler(CommandHandler("top_2048", print_2048_leaderboard))
    application.add_handler(CommandHandler("game", tictactoe_lobby))
    application.add_handler(CommandHandler("bet", bet))
    application.add_handler(CommandHandler("claim", claim))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CallbackQueryHandler(choose_player, pattern="^tictactoe_"))
    application.add_handler(CommandHandler("blackjack", blackjack_lobby))
    application.add_handler(CallbackQueryHandler(choose_blackjack_players, pattern="^blackjack_"))
    application.add_handler(CommandHandler("2048", game_2048))
    application.add_handler(CallbackQueryHandler(handle_2048_move, pattern="^(up|down|left|right|skip)$"))
    application.add_handler(CommandHandler("spin", spin))
    application.add_handler(wpm_handler)
    application.add_handler(prank_handler)
    application.add_handler(game_21)
    application.add_handler(game_2048_handler)
    # application.add_handler(CommandHandler("feedback", feedback_command))
    # application.add_handler(CommandHandler("test", test_command))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'tiktok\.com'), handle_tik_tok))
    
    await application.run_polling()

if __name__ == '__main__':
    import nest_asyncio
    nest_asyncio.apply()  # это решение придумал гпт, я ХЗ КАК ЭТО РАБОТАЕТ, но оно мне нужно для кнопок

    asyncio.get_event_loop().run_until_complete(main())