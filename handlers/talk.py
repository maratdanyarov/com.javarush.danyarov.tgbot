"""Talk to personality command handler."""
import logging
import os
import json
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from utils.keyboards import get_personalities_keyboard, get_talk_finish_keyboard
from utils.prompts import PERSONALITY_PROMPTS
from config import IMAGES, PERSONALITIES

logger = logging.getLogger(__name__)

# Conversation states
TALK_CHAT = 1


async def talk_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /talk command."""
    logger.info(f"User {update.effective_user.id} started talk feature")

    # Send personality selection
    try:
        if os.path.exists(IMAGES['talk']):
            await update.message.reply_photo(
                photo=open(IMAGES['talk'], 'rb'),
                caption="💬 **Talk to a Historical Figure**\n\nChoose a personality to chat with:",
                reply_markup=get_personalities_keyboard()
            )
        else:
            await update.message.reply_text(
                "💬 **Talk to a Historical Figure**\n\nChoose a personality to chat with:",
                reply_markup=get_personalities_keyboard(),
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error sending image: {e}")
        await update.message.reply_text(
            "💬 **Talk to a Historical Figure**\n\nChoose a personality to chat with:",
            reply_markup=get_personalities_keyboard(),
            parse_mode='Markdown'
        )


async def personality_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle personality selection."""
    query = update.callback_query
    await query.answer()

    personality_id = query.data.split('_')[1]
    personality_name = PERSONALITIES[personality_id]

    logger.info(f"User {update.effective_user.id} selected {personality_name}")

    # Save personality to context
    context.user_data['personality'] = personality_id
    context.user_data['personality_name'] = personality_name
    context.user_data['state'] = 'talk_chat'
    context.user_data['conversation_history'] = []

    # Get database from context
    db = context.bot_data.get('database')

    # Check for existing conversation
    existing = await db.get_conversation_context(update.effective_user.id)
    if existing and existing['personality'] == personality_id:
        context.user_data['conversation_history'] = json.loads(existing['context'])
        await query.message.reply_text(
            f"📜 Continuing your conversation with **{personality_name}**...\n\nType your message:",
            reply_markup=get_talk_finish_keyboard(),
            parse_mode='Markdown'
        )
    else:
        await query.message.reply_text(
            f"🎭 You're now talking to **{personality_name}**!\n\nType your message:",
            reply_markup=get_talk_finish_keyboard(),
            parse_mode='Markdown'
        )

    return TALK_CHAT


async def handle_talk_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle messages in talk chat state."""
    if context.user_data.get('state') != 'talk_chat':
        return ConversationHandler.END

    user_message = update.message.text
    personality_id = context.user_data.get('personality')
    personality_name = context.user_data.get('personality_name')

    logger.info(f"User {update.effective_user.id} talking to {personality_name}")

    # Send typing indicator
    await update.message.chat.send_action('typing')

    # Get OpenAI client from context
    openai_client = context.bot_data.get('openai_client')

    # Build conversation history
    messages = [
        {"role": "system", "content": PERSONALITY_PROMPTS[personality_id]}
    ]

    # Add conversation history
    for msg in context.user_data.get('conversation_history', []):
        messages.append(msg)

    # Add current message
    messages.append({"role": "user", "content": user_message})

    # Generate response
    response = await openai_client.generate_conversation_response(messages)

    # Update conversation history
    context.user_data['conversation_history'].append({"role": "user", "content": user_message})
    context.user_data['conversation_history'].append({"role": "assistant", "content": response})

    # Keep only last 10 exchanges
    if len(context.user_data['conversation_history']) > 20:
        context.user_data['conversation_history'] = context.user_data['conversation_history'][-20:]

    # Save to database
    db = context.bot_data.get('database')
    await db.save_conversation_context(
        update.effective_user.id,
        personality_id,
        json.dumps(context.user_data['conversation_history'])
    )

    # Send response
    await update.message.reply_text(
        response,
        reply_markup=get_talk_finish_keyboard()
    )

    return TALK_CHAT


async def change_personality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle change personality button."""
    query = update.callback_query
    await query.answer()

    # Clear conversation
    context.user_data.clear()

    # Show personality selection
    await query.message.reply_text(
        "💬 **Choose a new personality to chat with:**",
        reply_markup=get_personalities_keyboard(),
        parse_mode='Markdown'
    )

    return ConversationHandler.END


async def cancel_talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel talk conversation."""
    context.user_data.pop('state', None)
    return ConversationHandler.END
