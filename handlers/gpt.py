"""GPT command handler."""
import logging
import os
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from utils.keyboards import get_finish_keyboard
from config import IMAGES

logger = logging.getLogger(__name__)

# Conversation states
GPT_CHAT = 1


async def gpt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /gpt command."""
    logger.info(f"User {update.effective_user.id} started GPT chat")

    # Set conversation state
    context.user_data['state'] = 'gpt_chat'

    # Send initial message with image
    try:
        if os.path.exists(IMAGES['gpt']):
            await update.message.reply_photo(
                photo=open(IMAGES['gpt'], 'rb'),
                caption="🤖 **ChatGPT Interface**\n\nI'm ready to help! Send me any question or message, "
                        "and I'll provide a thoughtful response.\n\nType your message below:",
                reply_markup=get_finish_keyboard()
            )
        else:
            await update.message.reply_text(
                "🤖 **ChatGPT Interface**\n\nI'm ready to help! Send me any question or message, "
                "and I'll provide a thoughtful response.\n\nType your message below:",
                reply_markup=get_finish_keyboard(),
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error sending image: {e}")
        await update.message.reply_text(
            "🤖 **ChatGPT Interface**\n\nI'm ready to help! "
            "Send me any question or message, and I'll provide a thoughtful response.\n\nType your message below:",
            reply_markup=get_finish_keyboard(),
            parse_mode='Markdown'
        )

    return GPT_CHAT


async def gpt_command_from_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /gpt command from callback query."""
    query = update.callback_query
    await query.answer()

    logger.info(f"User {query.from_user.id} started GPT chat from button")

    # Set conversation state
    context.user_data['state'] = 'gpt_chat'

    try:
        if os.path.exists(IMAGES['gpt']):
            await query.message.reply_photo(
                photo=open(IMAGES['gpt'], 'rb'),
                caption="🤖 **ChatGPT Interface**\n\nI'm ready to help! Send me any question or message, "
                        "and I'll provide a thoughtful response.\n\nType your message below:",
                reply_markup=get_finish_keyboard()
            )
        else:
            await query.message.reply_text(
                "🤖 **ChatGPT Interface**\n\nI'm ready to help! Send me any question or message, "
                "and I'll provide a thoughtful response.\n\nType your message below:",
                reply_markup=get_finish_keyboard(),
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error sending image: {e}")
        await query.message.reply_text(
            "🤖 **ChatGPT Interface**\n\nI'm ready to help! "
            "Send me any question or message, and I'll provide a thoughtful response.\n\nType your message below:",
            reply_markup=get_finish_keyboard(),
            parse_mode='Markdown'
        )

    return GPT_CHAT


async def handle_gpt_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle messages in GPT chat state."""
    if context.user_data.get('state') != 'gpt_chat':
        return ConversationHandler.END

    user_message = update.message.text
    logger.info(f"User {update.effective_user.id} sent GPT message: {user_message[:50]}...")

    # Send typing indicator
    await update.message.chat.send_action('typing')

    # Get OpenAI client from context
    openai_client = context.bot_data.get('openai_client')

    # Generate response
    response = await openai_client.generate_response(user_message)

    # Send response with keyboard
    await update.message.reply_text(
        response,
        reply_markup=get_finish_keyboard()
    )

    return GPT_CHAT


async def cancel_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel GPT conversation."""
    context.user_data.pop('state', None)
    return ConversationHandler.END
