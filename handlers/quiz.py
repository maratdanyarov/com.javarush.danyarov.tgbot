"""Quiz command handler."""
import logging
import os
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from utils.keyboards import (get_quiz_topics_keyboard, get_quiz_continue_keyboard,
                           get_finish_keyboard)
from utils.prompts import get_quiz_prompt, get_quiz_validation_prompt
from config import IMAGES, QUIZ_TOPICS

logger = logging.getLogger(__name__)

# Conversation states
QUIZ_ANSWER = 1


async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /quiz command."""
    logger.info(f"User {update.effective_user.id} started quiz")

    # Send topic selection
    try:
        if os.path.exists(IMAGES['quiz']):
            await update.message.reply_photo(
                photo=open(IMAGES['quiz'], 'rb'),
                caption="🧠 **Quiz Time!**\n\nChoose a topic to test your knowledge:",
                reply_markup=get_quiz_topics_keyboard()
            )
        else:
            await update.message.reply_text(
                "🧠 **Quiz Time!**\n\nChoose a topic to test your knowledge:",
                reply_markup=get_quiz_topics_keyboard(),
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error sending image: {e}")
        await update.message.reply_text(
            "🧠 **Quiz Time!**\n\nChoose a topic to test your knowledge:",
            reply_markup=get_quiz_topics_keyboard(),
            parse_mode='Markdown'
        )


async def topic_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle topic selection."""
    query = update.callback_query
    await query.answer()

    topic_id = query.data.split('_')[2]
    topic_name = QUIZ_TOPICS[topic_id]

    logger.info(f"User {update.effective_user.id} selected topic: {topic_name}")

    # Initialize quiz state
    context.user_data['quiz_topic'] = topic_id
    context.user_data['quiz_topic_name'] = topic_name
    context.user_data['quiz_score'] = 0
    context.user_data['quiz_total'] = 0
    context.user_data['quiz_questions'] = []
    context.user_data['state'] = 'quiz'

    # Generate first question
    await generate_question(query.message, context)

    return QUIZ_ANSWER


async def generate_question(message, context: ContextTypes.DEFAULT_TYPE):
    """Generate a quiz question."""
    topic = context.user_data['quiz_topic_name']
    previous_questions = context.user_data.get('quiz_questions', [])

    # Send typing indicator
    await message.chat.send_action('typing')

    # Get OpenAI client
    openai_client = context.bot_data.get('openai_client')

    # Generate question
    prompt = get_quiz_prompt(topic, previous_questions)
    response = await openai_client.generate_response(prompt)

    # Parse question and answer
    lines = response.strip().split('\n')
    question = ""
    answer = ""

    for line in lines:
        if line.startswith('Question:'):
            question = line.replace('Question:', '').strip()
        elif line.startswith('Answer:'):
            answer = line.replace('Answer:', '').strip()

    # Save current question
    context.user_data['current_question'] = question
    context.user_data['current_answer'] = answer
    context.user_data['quiz_questions'].append(question)

    # Send question
    await message.reply_text(
        f"❓ **Question {context.user_data['quiz_total'] + 1}**\n\n{question}\n\nType your answer:",
        parse_mode='Markdown'
    )


async def handle_quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle quiz answer."""
    if context.user_data.get('state') != 'quiz':
        return ConversationHandler.END

    user_answer = update.message.text
    correct_answer = context.user_data.get('current_answer')
    question = context.user_data.get('current_question')

    logger.info(f"User {update.effective_user.id} answered: {user_answer}")

    # Send typing indicator
    await update.message.chat.send_action('typing')

    # Get OpenAI client
    openai_client = context.bot_data.get('openai_client')

    # Validate answer
    validation_prompt = get_quiz_validation_prompt(question, correct_answer, user_answer)
    validation = await openai_client.generate_response(validation_prompt)

    # Update score
    context.user_data['quiz_total'] += 1
    if validation.lower().startswith('correct'):
        context.user_data['quiz_score'] += 1
        result_emoji = "✅"
    else:
        result_emoji = "❌"

    # Get current stats
    score = context.user_data['quiz_score']
    total = context.user_data['quiz_total']
    percentage = (score / total * 100) if total > 0 else 0

    # Save to database
    db = context.bot_data.get('database')
    await db.save_quiz_score(
        update.effective_user.id,
        context.user_data['quiz_topic'],
        score,
        total
    )

    # Send result
    await update.message.reply_text(
        f"{result_emoji} {validation}\n\n"
        f"📊 **Current Score:** {score}/{total} ({percentage:.1f}%)",
        reply_markup=get_quiz_continue_keyboard(),
        parse_mode='Markdown'
    )

    return QUIZ_ANSWER


async def next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle next question button."""
    query = update.callback_query
    await query.answer()

    await generate_question(query.message, context)
    return QUIZ_ANSWER


async def change_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle change topic button."""
    query = update.callback_query
    await query.answer()

    # Clear quiz state but keep scores
    context.user_data.pop('state', None)
    context.user_data.pop('current_question', None)
    context.user_data.pop('current_answer', None)

    # Show topic selection
    await query.message.reply_text(
        "🧠 **Choose a new topic:**",
        reply_markup=get_quiz_topics_keyboard(),
        parse_mode='Markdown'
    )

    return ConversationHandler.END


async def cancel_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel quiz conversation."""
    context.user_data.pop('state', None)
    return ConversationHandler.END
