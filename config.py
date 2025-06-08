"""Configureation module for the Telegram Chatgpt bot."""
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DATABASE_PATH = os.getenv('DATABASE_PATH')

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', logging.INFO)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL)
)

# OpenAI configuration
OPENAI_MODEL = "gpt-4.1"
MAX_TOKENS = 1000
TEMPERATURE = 0.7

# Language options for translator
LANGUAGES = {
    'en': 'English',
    'ru': 'Russian'
}

# Quiz topics
QUIZ_TOPICS = {
    'science': 'Science',
    'history': 'History',
    'geography': 'Geography',
    'literature': 'Literature',
    'movies': 'Movies',
    'technology': 'Technology'
}

# Famous personalities for talk feature
PERSONALITIES = {
    'einstein': 'Albert Einstein',
    'shakespeare': 'William Shakespeare',
    'jobs': 'Steve Jobs'
}

# Recommendation categories
RECOMMENDATION_CATEGORIES = {
    'movies': 'Movies',
    'books': 'Books'
}

# Genres for recommendations
MOVIE_GENRES = [
    'Action', 'Comedy', 'Drama', 'Horror', 'Sci-Fi', 'Fantasy',
    'Romance', 'Thriller', 'Western', 'Documentary', 'Animation'
]

BOOk_GENRES = [
    'Fiction', 'Non-fiction', 'Mystery', 'Sci-Fi', 'Fantasy',
    'Biography', 'History', 'Self-help'
]

# Image paths
IMAGES = {
    'start': 'images/start.png',
    'random': 'images/random.png',
    'gpt': 'images/gpt.png',
    'talk': 'images/talk.png',
    'quiz': 'images/quiz.png',
    'translate': 'images/translate.png',
    'recommend': 'images/recommend.png'
}