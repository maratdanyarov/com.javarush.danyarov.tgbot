"""ChatGPT prompts for various bot features."""

# Random fact prompt
RANDOM_FACT_PROMPT = """Generate an interesting and surprising random fact. 
The fact should be educational, engaging, and suitable for all ages. 
Make it about 2-3 sentences long. Topics can include science, history, 
nature, technology, or any other fascinating subject."""

# Personality prompts
PERSONALITY_PROMPTS = {
    'einstein': """You are Albert Einstein, the renowned physicist. 
    Respond as Einstein would, with his characteristic wit, wisdom, and passion for science. 
    Use his speaking style and occasionally reference his theories or life experiences.
    Be humble yet confident, and express complex ideas in accessible ways.""",

    'shakespeare': """You are William Shakespeare, the famous playwright and poet. 
    Respond in a mix of modern English with occasional Elizabethan phrases. 
    Be poetic, dramatic, and philosophical. Reference your plays and sonnets when relevant.""",

    'jobs': """You are Steve Jobs, the visionary co-founder of Apple. 
    Respond as Jobs would—direct, passionate, and inspiring. 
    Speak with clarity and conviction, often emphasizing simplicity, innovation, and design. 
    Draw from your life at Apple, your views on creativity, and your experience in changing the world through technology. 
    Be bold, challenge conventional thinking, and always aim for excellence."""
}


# Quiz generation prompt
def get_quiz_prompt(topic: str, previous_questions: list = None) -> str:
    """Generate prompt for quiz questions."""
    excluded = ""
    if previous_questions:
        excluded = f"\nDo not repeat these questions: {', '.join(previous_questions)}"

    return f"""Generate a single trivia question about {topic}. 
    The question should be moderately difficult and have a clear, factual answer.
    Format your response as:
    Question: [Your question here]
    Answer: [The correct answer]

    Make sure the answer is brief (1-5 words when possible).{excluded}"""


# Translation prompt
def get_translation_prompt(text: str, target_language: str) -> str:
    """Generate prompt for translation."""
    return f"""Translate the following text to {target_language}. 
    Provide only the translation without any additional explanation:

    {text}"""


# Auto-detect translation prompt
def get_auto_translation_prompt(text: str) -> str:
    """Generate prompt for auto-detect translation."""
    return f"""Detect the language of the following text and translate it:
    - If it's in English, translate to Russian
    - If it's in Russian, translate to English
    - If it's in another language, translate to Russian

    Format your response as:
    Detected: [language]
    Translation: [translated text]

    Text: {text}"""


# Recommendation prompt
def get_recommendation_prompt(category: str, genre: str,
                              disliked_items: list = None) -> str:
    """Generate prompt for recommendations."""
    excluded = ""
    if disliked_items:
        excluded = f"\n\nDo NOT recommend these items as the user is not interested: {', '.join(disliked_items)}"

    if category == 'movies':
        return f"""Recommend 3 {genre} movies. For each movie, provide:
        - Title (with year)
        - Brief plot summary (2-3 sentences)
        - Why it's worth watching

        Format each recommendation clearly with the title in bold.{excluded}"""

    else:  # books
        return f"""Recommend 3 {genre} books. For each book, provide:
        - Title and author
        - Brief summary (2-3 sentences)
        - Why it's worth reading

        Format each recommendation clearly with the title in bold.{excluded}"""
