"""Translator command handler."""
import logging
import os
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from utils.keyboards import get_language_keyboard, get_translate_continue_keyboard
from utils.prompts import get_translation_prompt, get_auto_translation_prompt
from config import IMAGES, LANGUAGES

logger = logging.getLogger(__name__)

# Conversation states
TRANSLATE_TEXT = 4


async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /translate command."""
    logger.info(f"User {update.effective_user.id} started translator")

    # Send language selection
    try:
        if os.path.exists(IMAGES['translate']):
            await update.message.reply_photo(
                photo=open(IMAGES['translate'], 'rb'),
                caption="🌐 **Translator**\n\nChoose translation mode:",
                reply_markup=get_language_keyboard()
            )
        else:
            await update.message.reply_text(
                "🌐 **Translator**\n\nChoose translation mode:",
                reply_markup=get_language_keyboard(),
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error sending image: {e}")
        await update.message.reply_text(
            "🌐 **Translator**\n\nChoose translation mode:",
            reply_markup=get_language_keyboard(),
            parse_mode='Markdown'
        )


async def translate_command_from_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /translate command from callback query."""
    query = update.callback_query
    await query.answer()

    logger.info(f"User {query.from_user.id} started translator from button")

    await query.message.reply_text(
        "🌐 **Translator**\n\nChoose translation mode:",
        reply_markup=get_language_keyboard(),
        parse_mode='Markdown'
    )


async def translation_mode_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle translation mode selection."""
    query = update.callback_query
    await query.answer()

    mode = query.data.split('_')[1]

    if mode == 'auto':
        context.user_data['translate_mode'] = 'auto'
        instruction = "I'll automatically detect the language and translate between English and Russian."
    elif mode == 'en':
        context.user_data['translate_mode'] = 'en_ru'
        context.user_data['target_language'] = 'Russian'
        instruction = "I'll translate from English to Russian."
    else:  # ru_en
        context.user_data['translate_mode'] = 'ru_en'
        context.user_data['target_language'] = 'English'
        instruction = "I'll translate from Russian to English."

    context.user_data['state'] = 'translate'

    logger.info(f"User {update.effective_user.id} selected translation mode: {mode}")

    await query.message.reply_text(
        f"✅ {instruction}\n\nSend me the text you want to translate:",
        reply_markup=get_translate_continue_keyboard()
    )

    return TRANSLATE_TEXT


async def handle_translation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text translation."""
    if context.user_data.get('state') != 'translate':
        return ConversationHandler.END

    text_to_translate = update.message.text
    mode = context.user_data.get('translate_mode')

    logger.info(f"User {update.effective_user.id} translating text (mode: {mode})")

    # Send typing indicator
    await update.message.chat.send_action('typing')

    # Get OpenAI client
    openai_client = context.bot_data.get('openai_client')

    # Generate translation
    if mode == 'auto':
        prompt = get_auto_translation_prompt(text_to_translate)
        response = await openai_client.generate_response(prompt)

        # Parse response
        lines = response.strip().split('\n')
        detected_lang = ""
        translation = ""

        for line in lines:
            if line.startswith('Detected:'):
                detected_lang = line.replace('Detected:', '').strip()
            elif line.startswith('Translation:'):
                translation = line.replace('Translation:', '').strip()

        if not translation:
            translation = response  # Fallback if parsing fails

        result = f"🔍 **Detected:** {detected_lang}\n\n📝 **Translation:**\n{translation}"
    else:
        target_lang = context.user_data.get('target_language')
        prompt = get_translation_prompt(text_to_translate, target_lang)
        translation = await openai_client.generate_response(prompt)
        result = f"📝 **Translation to {target_lang}:**\n\n{translation}"

    # Send translation
    await update.message.reply_text(
        result,
        reply_markup=get_translate_continue_keyboard(),
        parse_mode='Markdown'
    )

    return TRANSLATE_TEXT


async def change_translation_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle change mode button."""
    query = update.callback_query
    await query.answer()

    # Clear translation state
    context.user_data.pop('state', None)
    context.user_data.pop('translate_mode', None)
    context.user_data.pop('target_language', None)

    # Show mode selection
    await query.message.reply_text(
        "🌐 **Choose translation mode:**",
        reply_markup=get_language_keyboard(),
        parse_mode='Markdown'
    )

    return ConversationHandler.END


async def cancel_translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel translation conversation."""
    context.user_data.pop('state', None)
    return ConversationHandler.END