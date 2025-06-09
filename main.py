"""Main entry point for the Telegram ChatGPT bot."""
import logging
import asyncio
from telegram import Update
from telegram.ext import (Application, CommandHandler, MessageHandler,
                          CallbackQueryHandler, ConversationHandler, filters)

from config import TELEGRAM_BOT_TOKEN
from database import Database
from openai_client import OpenAIClient

# Import hanldlers
from handlers.start import start_command, finish_callback
from handlers.random_fact import random_command, another_fact_callback
from handlers.gpt import gpt_command, handle_gpt_message, cancel_gpt, GPT_CHAT


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


async def handle_command_callback(update: Update, context):
    """Handle command callbacks from inline keyboard."""
    query = update.callback_query
    await query.answer()

    command = query.data.replace('cmd_', "/")

    query.message.text = command

    # TODO: add all commands handlers
    if command == '/random':
        await random_command(query, context)
    elif command == '/gpt':
        await gpt_command(query, context)

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
        entry_points=[CommandHandler("gpt", gpt_command)],
        states={
            GPT_CHAT:[
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_gpt_message),
                CallbackQueryHandler(finish_callback, pattern="^finish$")
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_gpt)]
    )
    application.add_handler(gpt_handler)


    # Start polling
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
