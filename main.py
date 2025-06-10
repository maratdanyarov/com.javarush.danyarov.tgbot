"""Main entry point for the Telegram ChatGPT bot."""
import logging
import asyncio
from telegram import Update
from telegram.ext import (Application, CommandHandler, MessageHandler,
                         CallbackQueryHandler, ConversationHandler, filters)
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning
from config import TELEGRAM_BOT_TOKEN
from database import Database
from openai_client import OpenAIClient

# Import handlers
from handlers.start import start_command, finish_callback
from handlers.random_fact import (random_command, random_command_from_callback,
                                  another_fact_callback)
from handlers.gpt import (gpt_command, gpt_command_from_callback,
                         handle_gpt_message, cancel_gpt, GPT_CHAT)
from handlers.talk import (talk_command, talk_command_from_callback,
                          personality_selected, handle_talk_message,
                          change_personality, cancel_talk, TALK_CHAT)
from handlers.quiz import (quiz_command, quiz_command_from_callback,
                          topic_selected, handle_quiz_answer,
                          next_question, change_topic, cancel_quiz, QUIZ_ANSWER)
from handlers.translate import (translate_command, translate_command_from_callback,
                               translation_mode_selected, handle_translation,
                               change_translation_mode, cancel_translate, TRANSLATE_TEXT)
from handlers.recommend import (recommend_command, recommend_command_from_callback,
                               category_selected, genre_selected, handle_dislike,
                               handle_more_recommendations, recommendation_back)

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    """Initialize bot data after startup."""
    # Initialize database
    db = Database()
    await db.initialize()
    application.bot_data['database'] = db

    # Initialize OpenAI client
    openai_client = OpenAIClient()
    application.bot_data['openai_client'] = openai_client

    logger.info("Bot initialization complete")


def main():
    """Start the bot."""
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add post-init callback
    application.post_init = post_init

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("random", random_command))

    # GPT conversation handler
    gpt_handler = ConversationHandler(
        entry_points=[
            CommandHandler("gpt", gpt_command),
            CallbackQueryHandler(gpt_command_from_callback, pattern="^cmd_gpt$")
        ],
        states={
            GPT_CHAT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_gpt_message),
                CallbackQueryHandler(finish_callback, pattern="^finish$")
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_gpt)],
    )
    application.add_handler(gpt_handler)

    # Talk conversation handler
    talk_handler = ConversationHandler(
        entry_points=[
            CommandHandler("talk", talk_command),
            CallbackQueryHandler(talk_command_from_callback, pattern="^cmd_talk$")
        ],
        states={
            TALK_CHAT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_talk_message),
                CallbackQueryHandler(finish_callback, pattern="^finish$"),
                CallbackQueryHandler(change_personality, pattern="^change_personality$")
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_talk)]
    )
    application.add_handler(talk_handler)

    # Quiz conversation handler
    quiz_handler = ConversationHandler(
        entry_points=[
            CommandHandler("quiz", quiz_command),
            CallbackQueryHandler(quiz_command_from_callback, pattern="^cmd_quiz$")
        ],
        states={
            QUIZ_ANSWER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_quiz_answer),
                CallbackQueryHandler(next_question, pattern="^quiz_next$"),
                CallbackQueryHandler(change_topic, pattern="^quiz_change_topic$"),
                CallbackQueryHandler(finish_callback, pattern="^finish$")
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_quiz)]
    )
    application.add_handler(quiz_handler)

    # Translate conversation handler
    translate_handler = ConversationHandler(
        entry_points=[
            CommandHandler("translate", translate_command),
            CallbackQueryHandler(translate_command_from_callback, pattern="^cmd_translate$")
        ],
        states={
            TRANSLATE_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_translation),
                CallbackQueryHandler(change_translation_mode, pattern="^translate_change$"),
                CallbackQueryHandler(finish_callback, pattern="^finish$")
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_translate)]
    )
    application.add_handler(translate_handler)

    # Recommendation handlers
    application.add_handler(CommandHandler("recommend", recommend_command))
    application.add_handler(CallbackQueryHandler(recommend_command_from_callback, pattern="^cmd_recommend$"))

    # Callback query handlers
    application.add_handler(CallbackQueryHandler(random_command_from_callback, pattern="^cmd_random$"))
    application.add_handler(CallbackQueryHandler(finish_callback, pattern="^finish$"))
    application.add_handler(CallbackQueryHandler(another_fact_callback, pattern="^another_fact$"))

    # Talk callbacks
    application.add_handler(CallbackQueryHandler(personality_selected, pattern="^talk_"))

    # Quiz callbacks
    application.add_handler(CallbackQueryHandler(topic_selected, pattern="^quiz_topic_"))

    # Translate callbacks
    application.add_handler(CallbackQueryHandler(translation_mode_selected, pattern="^translate_"))

    # Recommendation callbacks
    application.add_handler(CallbackQueryHandler(category_selected, pattern="^rec_cat_"))
    application.add_handler(CallbackQueryHandler(genre_selected, pattern="^rec_genre_"))
    application.add_handler(CallbackQueryHandler(handle_dislike, pattern="^rec_dislike$"))
    application.add_handler(CallbackQueryHandler(handle_more_recommendations, pattern="^rec_more$"))
    application.add_handler(CallbackQueryHandler(recommendation_back, pattern="^rec_back$"))

    # Start polling
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()