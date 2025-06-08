"""Database module for SQLite operations."""
import aiosqlite
import logging
from typing import List, Dict, Optional
from config import DATABASE_PATH

logger = logging.getLogger(__name__)

class Database:
    """Async SQLite database handler."""

    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path

    async def initialize(self):
        """Initialize the database tables."""
        async with aiosqlite.connect(self.db_path) as db:
            # Quiz scores table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS quiz_scores (
                    user_id INTEGER,
                    topic TEXT,
                    correct_answers INTEGER,
                    total_questions INTEGER,
                    timestamp DATATIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, topic, timestamp)
                )
            ''')

            # User conversations table (for personality talks)
            await db.execute('''
                CREATE TABLE IF NOT EXISTS conversation (
                    user_id INTEGER PRIMARY KEY,
                    personality TEXT,
                    context TEXT
                )
            ''')

            # Recommendations table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS recommendations (
                    user_id INTEGER,
                    category TEXT,
                    item_name TEXT,
                    liked BOOLEAN,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, category, item_name)
                )
            ''')

            # User preferences table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id INTEGER,
                    prefernces_type TEXT,
                    preferences_value TEXT,
                    PRIMARY KEY (user_id, prefernces_type)
                )
            ''')

            await db.commit()
            logger.info("Database successfully initialized")

    async def save_quiz_score(self, user_id: int, topic: str,
                              correct_answers: int, total_questions: int):
        """Save quiz score for a user."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO quiz_scores (user_id, topic, correct_answers, total_questions)
                VALUES(?, ?, ?, ?)
            ''', (user_id, topic, correct_answers, total_questions))
            await db.commit()

    async def get_quiz_stats(self, user_id: int, topic: Optional[str] = None) -> Dict:
        """Get quiz statistics for a user."""
        async with aiosqlite.connect(self.db_path) as db:
            if topic:
                cursor = await db.execute('''
                    SELECT SUM(correct_answers), SUM(total_questions)
                    FROM quiz_scores 
                    WHERE user_id = ? AND topic = ?
                ''', (user_id, topic))
            else:
                cursor = await db.execute('''
                    SELECT SUM(correct_answers), SUM(total_questions)
                    FROM quiz_scores
                    WHERE user_id = ?
                ''', (user_id,))

            row = await cursor.fetchone()
            if row and row[0] is not None:
                return {
                    'correct': row[0],
                    'total': row[1],
                    'percentage': round((row[0] / row[1]) * 100, 2) if row[1] > 0 else 0
                }
            return {'correct': 0, 'total': 0, 'percentage': 0}

    async def save_conversation_context(self, user_id: int, personality: str, context: str):
        """Save conversation context for personality talk."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO conversation (user_id, personality, context)
                VALUES(?, ?, ?)
            ''', (user_id, personality, context))
            await db.commit()

    async def get_conversation_context(self, user_id: int) -> Optional[Dict]:
        """Get conversation context for a user."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT personality, context FROM conversation
                WHERE user_id = ?
            ''', (user_id,))
            row = await cursor.fetchone()
            if row:
                return {'personality': row[0], 'context': row[1]}
            return None

    async def clear_conversation_context(self, user_id: int):
        """Clear conversation context for a user."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                DELETE FROM conversation WHERE user_id = ?
            ''', (user_id))
            await db.commit()


    async def save_recommendation(self, user_id: int, category: str,
                                   item_name: str, liked: bool):
        """Save recommendationn feedback."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO recommendations
                (user_id, category, item_name, liked)
                VALUES(?, ?, ?, ?)
            ''', (user_id, category, item_name, liked))
            await db.commit()

    async def get_disliked_recommendations(self, user_id: int,
                                           category: str) -> List[str]:
        """Get list of disliked recommendations."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT item_name FROM recommendations
                WHERE user_id = ? AND category = ? AND liked = 0
            ''', (user_id, category))
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

    async def save_user_preference(self, user_id: int, pref_type: str, pref_value: str):
        """Save user preferences."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO user_preferences
                (user_id, preference_type, preference_value)
                VALUES(?, ?, ?)
            ''', (user_id, pref_type, pref_value))
            await db.commit()

    async def get_user_preferences(self, user_id: int, pref_type: str) -> Optional[str]:
        """Get user preference."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT preference_value FROM user_preferences
                WHERE user_id = ? AND preference_type = ?
            ''', (user_id, pref_type))
            row = await cursor.fetchone()
            return row[0] if row else None
        