"""Start command handler."""
import logging
import os
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from utils.keyboards import get_start_keyboard
from config import IMAGES

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    logger.info(f"User {user.id} started the bot.")

    welcome_text = f"""🌟 Welcome, {user.first_name}! 🌟

I'm your AI assistant powered by ChatGPT. Here's what I can do:

🎲 **Random Fact** - Get fascinating facts about anything
🤖 **ChatGPT** - Chat directly with AI
💬 **Talk to Personality** - Chat with historical figures
🧠 **Quiz** - Test your knowledge on various topics
🌐 **Translator** - Translate between English and Russian
🎬 **Recommendations** - Get movie and book suggestions

Choose an option below or use the commands:
/random - Random fact
/gpt - ChatGPT interface
/talk - Talk to a personality
/quiz - Start a quiz
/translate - Translator
/recommend - Get recommendations"""

    # Try to send with image, fallback to text only
    try:
        if os.path.exists(IMAGES['start']):
            await update.message.reply_photo(
                photo=open(IMAGES['start'], 'rb'),
                caption=welcome_text,
                reply_markup=get_start_keyboard()
            )
        else:
            await update.message.reply_text(
                text=welcome_text,
                reply_markup=get_start_keyboard()
            )
    except Exception as e:
        logger.error(f"Error sending start message: {e}")
        await update.message.reply_text(
            text=welcome_text,
            reply_markup=get_start_keyboard()
        )


async def finish_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle finish button callback."""
    query = update.callback_query
    await query.answer()

    # Clear any ongoing conversation states
    context.user_data.clear()

    # Send start menu
    user = update.effective_user
    welcome_text = f"""🌟 Welcome back, {user.first_name}! 🌟

What would you like to do next?"""

    await query.message.reply_text(
        text=welcome_text,
        reply_markup=get_start_keyboard()
    )

    return ConversationHandler.END
