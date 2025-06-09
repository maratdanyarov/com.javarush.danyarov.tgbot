"""Inline keyboard layouts for the bot."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import (QUIZ_TOPICS, PERSONALITIES, RECOMMENDATION_CATEGORIES, MOVIE_GENRES, BOOK_GENRES)


def get_start_keyboard() -> InlineKeyboardMarkup:
    """Get the start menu keyboard."""
    keyboard = [
        [InlineKeyboardButton("🎲 Random Fact", callback_data="cmd_random"),
         InlineKeyboardButton("🤖 ChatGPT", callback_data="cmd_gpt")],
        [InlineKeyboardButton("💬 Talk to Personality", callback_data="cmd_talk"),
         InlineKeyboardButton("🧠 Quiz", callback_data="cmd_quiz")],
        [InlineKeyboardButton("🌐 Translator", callback_data="cmd_translate"),
         InlineKeyboardButton("🎬 Recommendations", callback_data="cmd_recommend")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_finish_keyboard() -> InlineKeyboardMarkup:
    """Get the finish button keyboard."""
    keyboard = [[InlineKeyboardButton("🏁 Finish", callback_data="finish")]]
    return InlineKeyboardMarkup(keyboard)


def get_random_fact_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for random fact feature."""
    keyboard = [
        [InlineKeyboardButton("🎲 Another Fact", callback_data="another_fact")],
        [InlineKeyboardButton("🏁 Finish", callback_data="finish")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_quiz_topics_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for quiz topic selection."""
    keyboard = []
    for topic_id, topic_name in QUIZ_TOPICS.items():
        keyboard.append([InlineKeyboardButton(topic_name,
                                              callback_data=f"quiz_topic_{topic_id}")])
    keyboard.append([InlineKeyboardButton("🏁 Back to Menu", callback_data="finish")])
    return InlineKeyboardMarkup(keyboard)


def get_quiz_continue_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for continuing quiz."""
    keyboard = [
        [InlineKeyboardButton("➡️ Next Question", callback_data="quiz_next")],
        [InlineKeyboardButton("🔄 Change Topic", callback_data="quiz_change_topic")],
        [InlineKeyboardButton("🏁 Finish Quiz", callback_data="finish")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_personalities_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for personality selection."""
    keyboard = []
    for pers_id, pers_name in PERSONALITIES.items():
        keyboard.append([InlineKeyboardButton(pers_name, callback_data=f"talk_{pers_id}")])
    keyboard.append([InlineKeyboardButton("🏁 Back to Menu", callback_data="finish")])
    return InlineKeyboardMarkup(keyboard)


def get_talk_finish_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for talk feature."""
    keyboard = [
        [InlineKeyboardButton("🔄 Change Personality", callback_data="change_personality")],
        [InlineKeyboardButton("🏁 Finish", callback_data="finish")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for language selection."""
    keyboard = [
        [InlineKeyboardButton("🔄 Auto-detect", callback_data="translate_auto")],
        [InlineKeyboardButton("🇬🇧 English → Russian", callback_data="translate_en_ru")],
        [InlineKeyboardButton("🇷🇺 Russian → English", callback_data="translate_ru_en")],
        [InlineKeyboardButton("🏁 Back to Menu", callback_data="finish")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_translate_continue_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for translation feature."""
    keyboard = [
        [InlineKeyboardButton("🔄 Change Mode", callback_data="translate_change")],
        [InlineKeyboardButton("🏁 Finish", callback_data="finish")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_recommendation_category_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for recommendations category selection."""
    keyboard = []
    for cat_id, cat_name in RECOMMENDATION_CATEGORIES.items():
        keyboard.append([InlineKeyboardButton(f"{cat_name}",
                                              callback_data=f"rec_cat_{cat_id}")])
    keyboard.append([InlineKeyboardButton("🏁 Back to Menu", callback_data="finish")])
    return InlineKeyboardMarkup(keyboard)


def get_genre_keyboard(category: str) -> InlineKeyboardMarkup:
    """Get keyboard for genre selection."""
    genres = MOVIE_GENRES if category == 'movies' else BOOk_GENRES
    keyboard = []

    for i in range(0, len(genres), 2):
        row = []
        row.append(InlineKeyboardButton(genres[i],
                                        callback_data=f"rec_genre_{genres[i].lower()}"))
        if i + 1 < len(genres):
            row.append(InlineKeyboardButton(genres[i + 1],
                                            callback_data=f"rec_genre_{genres[i + 1].lower()}"))
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("🏁 Back", callback_data="rec_back")])
    return InlineKeyboardMarkup(keyboard)


def get_recommendation_feedback_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for recommendation feedback."""
    keyboard = [
        [InlineKeyboardButton("👎 Not Interested", callback_data="rec_dislike")],
        [InlineKeyboardButton("🔄 More Recommendations", callback_data="rec_more")],
        [InlineKeyboardButton("🏁 Finish", callback_data="finish")]
    ]
    return InlineKeyboardMarkup(keyboard)
