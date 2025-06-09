"""Random fact command handler."""
import logging
import os
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from utils.keyboards import get_random_fact_keyboard
from utils.prompts import RANDOM_FACT_PROMPT
from config import IMAGES

logger = logging.getLogger(__name__)


async def random_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /random command."""
    logger.info(f"User {update.effective_user.id} requested random fact")

    # Send initial message with image
    try:
        if os.path.exists(IMAGES['random']):
            message = await update.message.reply_photo(
                photo=open(IMAGES['random'], 'rb'),
                caption="🎲 Let me find an interesting fact for you..."
            )
        else:
            message = await update.message.reply_text(
                "🎲 Let me find an interesting fact for you..."
            )
    except Exception as e:
        logger.error(f"Error sending image: {e}")
        message = await update.message.reply_text(
            "🎲 Let me find an interesting fact for you..."
        )

    # Get OpenAI client from context
    openai_client = context.bot_data.get('openai_client')

    # Generate random fact
    fact = await openai_client.generate_response(RANDOM_FACT_PROMPT)

    # Send the fact with keyboard
    await message.reply_text(
        f"💡 **Did you know?**\n\n{fact}",
        reply_markup=get_random_fact_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )


async def another_fact_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle another fact button callback."""
    query = update.callback_query
    await query.answer()

    logger.info(f"User {update.effective_user.id} requested another fact")

    # Send loading message
    await query.message.reply_text("🎲 Finding another interesting fact...")

    # Get OpenAI client from context
    openai_client = context.bot_data.get('openai_client')

    # Generate another random fact
    fact = await openai_client.generate_response(RANDOM_FACT_PROMPT)

    # Send the fact with keyboard
    await query.message.reply_text(
        f"💡 **Did you know?**\n\n{fact}",
        reply_markup=get_random_fact_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )