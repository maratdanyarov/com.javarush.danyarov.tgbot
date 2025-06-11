"""Recommendation command handler."""
import logging
import os
import re
from telegram import Update
from telegram.ext import ContextTypes
from utils.keyboards import (get_recommendation_category_keyboard,
                           get_genre_keyboard, get_recommendation_feedback_keyboard)
from utils.prompts import get_recommendation_prompt
from config import IMAGES, RECOMMENDATION_CATEGORIES

logger = logging.getLogger(__name__)


async def recommend_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /recommend command."""
    logger.info(f"User {update.effective_user.id} started recommendations")

    # Send category selection
    try:
        if os.path.exists(IMAGES['recommend']):
            await update.message.reply_photo(
                photo=open(IMAGES['recommend'], 'rb'),
                caption="🎬📚 **Recommendations**\n\nWhat would you like recommendations for?",
                reply_markup=get_recommendation_category_keyboard()
            )
        else:
            await update.message.reply_text(
                "🎬📚 **Recommendations**\n\nWhat would you like recommendations for?",
                reply_markup=get_recommendation_category_keyboard(),
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error sending image: {e}")
        await update.message.reply_text(
            "🎬📚 **Recommendations**\n\nWhat would you like recommendations for?",
            reply_markup=get_recommendation_category_keyboard(),
            parse_mode='Markdown'
        )


async def recommend_command_from_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /recommend command from callback query."""
    query = update.callback_query
    await query.answer()

    logger.info(f"User {query.from_user.id} started recommendations from button")

    # Send category selection
    try:
        if os.path.exists(IMAGES['recommend']):
            await query.message.reply_photo(
                photo=open(IMAGES['recommend'], 'rb'),
                caption="🎬📚 **Recommendations**\n\nWhat would you like recommendations for?",
                reply_markup=get_recommendation_category_keyboard()
            )
        else:
            await query.message.reply_text(
                "🎬📚 **Recommendations**\n\nWhat would you like recommendations for?",
                reply_markup=get_recommendation_category_keyboard(),
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error sending image: {e}")
        await query.message.reply_text(
            "🎬📚 **Recommendations**\n\nWhat would you like recommendations for?",
            reply_markup=get_recommendation_category_keyboard(),
            parse_mode='Markdown'
        )


async def category_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle category selection."""
    query = update.callback_query
    await query.answer()

    category = query.data.split('_')[2]
    category_name = RECOMMENDATION_CATEGORIES[category]

    logger.info(f"User {update.effective_user.id} selected category: {category_name}")

    # Save category to context
    context.user_data['rec_category'] = category
    context.user_data['rec_category_name'] = category_name

    # Show genre selection
    await query.message.reply_text(
        f"🎭 **{category_name} Recommendations**\n\nChoose a genre:",
        reply_markup=get_genre_keyboard(category),
        parse_mode='Markdown'
    )


async def genre_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle genre selection."""
    query = update.callback_query
    await query.answer()

    genre = query.data.split('_')[2]
    category = context.user_data.get('rec_category')
    category_name = context.user_data.get('rec_category_name')

    logger.info(f"User {update.effective_user.id} selected genre: {genre}")

    # Save genre to context
    context.user_data['rec_genre'] = genre
    context.user_data['shown_recommendations'] = []

    # Send typing indicator
    await query.message.chat.send_action('typing')

    # Get database and check for disliked items
    db = context.bot_data.get('database')
    disliked_items = await db.get_disliked_recommendations(
        update.effective_user.id, category
    )

    # Get OpenAI client
    openai_client = context.bot_data.get('openai_client')

    # Generate recommendations
    prompt = get_recommendation_prompt(category, genre, disliked_items)
    recommendations = await openai_client.generate_response(prompt)

    # Extract item names for tracking
    current_items = extract_item_names(recommendations)
    context.user_data['current_recommendations'] = current_items

    # Add to shown recommendations
    context.user_data['shown_recommendations'].extend(current_items)

    # Send recommendations
    icon = "🎬" if category == "movies" else "📚"
    await query.message.reply_text(
        f"{icon} **{category_name} Recommendations - {genre.title()}**\n\n{recommendations}",
        reply_markup=get_recommendation_feedback_keyboard(),
        parse_mode='Markdown'
    )


async def handle_dislike(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle dislike button."""
    query = update.callback_query
    await query.answer("Noted! I'll avoid similar recommendations.")

    # Save disliked items to database
    db = context.bot_data.get('database')
    category = context.user_data.get('rec_category')
    current_recs = context.user_data.get('current_recommendations', [])

    for item in current_recs:
        await db.save_recommendation(
            update.effective_user.id, category, item, liked=False
        )

    # Generate new recommendations
    await get_more_recommendations(query, context)


async def get_more_recommendations(query, context: ContextTypes.DEFAULT_TYPE):
    """Get more recommendations."""
    category = context.user_data.get('rec_category')
    category_name = context.user_data.get('rec_category_name')
    genre = context.user_data.get('rec_genre')

    # Send typing indicator
    await query.message.chat.send_action('typing')

    # Get database and check for disliked items
    db = context.bot_data.get('database')
    disliked_items = await db.get_disliked_recommendations(
        query.from_user.id, category
    )

    # Get all previous shown recommendations
    shown_items = context.user_data.get('shown_recommendations', [])

    # Combine disliked and already shown items to avoid repetitions
    all_excluded_items = list(set(disliked_items + shown_items))

    # Get OpenAI client
    openai_client = context.bot_data.get('openai_client')

    # Generate new recommendations
    prompt = get_recommendation_prompt(category, genre, all_excluded_items)
    recommendations = await openai_client.generate_response(prompt)

    # Extract item names for tracking
    current_items = extract_item_names(recommendations)
    context.user_data['current_recommendations'] = current_items
    context.user_data['shown_recommendations'].extend(current_items)

    # Send recommendations
    icon = "🎬" if category == "movies" else "📚"
    await query.message.reply_text(
        f"{icon} **{category_name} Recommendations - {genre.title()}**\n\n{recommendations}",
        reply_markup=get_recommendation_feedback_keyboard(),
        parse_mode='Markdown'
    )


async def handle_more_recommendations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle more recommendations button."""
    query = update.callback_query
    await query.answer()

    await get_more_recommendations(query, context)


async def recommendation_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back button in recommendations."""
    query = update.callback_query
    await query.answer()

    # Clear genre selection
    context.user_data.pop('rec_genre', None)
    context.user_data.pop('shown_recommendations', None)

    # Show category selection
    await query.message.reply_text(
        "🎬📚 **Recommendations**\n\nWhat would you like recommendations for?",
        reply_markup=get_recommendation_category_keyboard(),
        parse_mode='Markdown'
    )


def extract_item_names(recommendations: str) -> list:
    """Extract item names from recommendations text."""
    items = []

    # Try to find bold titles (between ** markers)
    bold_pattern = r'\*\*(.*?)\*\*'
    matches = re.findall(bold_pattern, recommendations)

    for match in matches:
        # Clean up the match and check if it looks like a title
        if len(match) > 3 and not match.startswith('Recommendations'):
            # Remove year in parentheses for movies
            clean_title = re.sub(r'\s*\([0-9]{4}\)\s*', '', match)
            items.append(clean_title.strip())

    return items[:3]