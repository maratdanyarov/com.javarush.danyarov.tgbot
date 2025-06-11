# Telegram ChatGPT Bot

This is the final project for Module 1 of JavaRush Python University. A feature-rich Telegram bot powered by OpenAI's ChatGPT, offering various AI-powered functionalities.

## Features
1. **Random Facts** (`/random`) - Get interesting educational facts
2. **ChatGPT Interface** (`/gpt`) - Direct conversation with AI
3. **Talk to Personalities** (`/talk`) - Chat with historical figures
4. **Quiz** (`/quiz`) - Test knowledge on various topics
5. **Translator** (`/translate`) - English-Russian translation with auto-detection
6. **Recommendations** (`/recommend`) - Movie and book suggestions by genre

## Project Structure

```
telegram-chatgpt-bot/
├── .env                 # Environment variables (create from .env.example)
├── .env.example         # Environment variables template
├── .gitignore          # Git ignore rules
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── main.py             # Application entry point
├── config.py           # Configuration and constants
├── database.py         # SQLite database operations
├── openai_client.py    # OpenAI API wrapper
├── handlers/           # Command handlers
│   ├── __init__.py
│   ├── start.py       
│   ├── random_fact.py 
│   ├── gpt.py         
│   ├── talk.py        
│   ├── quiz.py        
│   ├── translate.py   
│   └── recommend.py   
├── utils/              # Utility modules
│   ├── __init__.py
│   ├── keyboards.py    # Telegram keyboards
│   └── prompts.py      # ChatGPT prompts
└── images/             # Bot images (optional)
    ├── start.jpg
    ├── random.jpg
    ├── gpt.jpg
    ├── talk.jpg
    ├── quiz.jpg
    ├── translate.jpg
    └── recommend.jpg
```

## Prerequisites

- Python 3.11 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- OpenAI API Key (from [OpenAI Platform](https://platform.openai.com/api-keys))

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd telegram-chatgpt-bot
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your tokens:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   OPENAI_API_KEY=your_openai_api_key_here
   LOG_LEVEL=INFO
   DATABASE_PATH=bot_database.db
   ```

### 5. Create Bot with BotFather
1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow the instructions
3. Copy the token and add it to your `.env` file

### 6. Add Bot Images (Optional)
Create an `images/` directory and add images for each feature:
- `start.jpg`
- `random.jpg`
- `gpt.jpg`
- `talk.jpg`
- `quiz.jpg`
- `translate.jpg`
- `recommend.jpg`

The bot will work without images, displaying text-only messages.

### 7. Run the Bot
```bash
python main.py
```

You should see:
```
INFO - Starting bot...
INFO - Database initialized successfully
INFO - Bot initialization complete
INFO - Application started
```

## Usage

1. Open Telegram and search for your bot username
2. Send `/start` to begin
3. Use the inline keyboard or commands:
   - `/random` - Get a random fact
   - `/gpt` - Chat with AI
   - `/talk` - Talk to historical personalities
   - `/quiz` - Start a quiz
   - `/translate` - Translate text
   - `/recommend` - Get movie/book recommendations

## Features Description

### 🎲 Random Facts
- Command: `/random`
- Generates educational facts using AI
- "Another fact" button for continuous learning

### 🤖 ChatGPT Interface
- Command: `/gpt`
- Direct conversation with ChatGPT
- Context maintained during conversation
- Use "Finish" button to end chat

### 💬 Talk to Personalities
- Command: `/talk`
- Available personalities:
  - Albert Einstein
  - William Shakespeare
  - Steve Jobs
- Conversations are saved and can be resumed

### 🧠 Quiz
- Command: `/quiz`
- Topics: Science, History, Geography, Literature, Movies, Technology
- Tracks scores and statistics
- Intelligent answer validation

### 🌐 Translator
- Command: `/translate`
- Modes:
  - Auto-detect (English ↔ Russian)
  - English → Russian
  - Russian → English

### 🎬📚 Recommendations
- Command: `/recommend`
- Categories: Movies and Books
- Multiple genres available
- Remembers disliked recommendations

## Database

The bot uses SQLite database (`bot_database.db`) with the following tables:
- `quiz_scores`: User quiz performance
- `conversations`: Personality chat history
- `recommendations`: User recommendation preferences
- `user_preferences`: General user settings

To reset the database, simply delete `bot_database.db` and restart the bot.

## Troubleshooting

### Bot not responding
1. Check if the bot is running (you should see logs in terminal)
2. Verify your bot token is correct
3. Make sure you've started the chat with `/start`

### OpenAI errors
1. Check your OpenAI API key is valid
2. Verify you have credits in your OpenAI account
3. Check the logs for specific error messages

### Database errors
1. Delete `bot_database.db` and restart the bot
2. Make sure you have write permissions in the directory

## Development

### Code Standards
- Follows PEP 8 style guide
- Comprehensive error handling
- Logging for debugging
- Modular architecture
- Type hints where applicable

### Adding New Features
1. Create a new handler in `handlers/`
2. Add prompts in `utils/prompts.py`
3. Update keyboards in `utils/keyboards.py`
4. Register handler in `main.py`

### Logging
- Set `LOG_LEVEL=DEBUG` in `.env` for detailed logs
- Logs include user actions and API calls
- Check logs for troubleshooting issues

## Security Notes

- **Never commit** `.env` file or tokens to Git
- Keep `openai-token.txt` in `.gitignore`
- Tokens are automatically revoked if exposed on GitHub
- Use environment variables for all sensitive data

## Cost Considerations

- Monitor your OpenAI usage at [platform.openai.com](https://platform.openai.com)
- Set usage limits in your OpenAI account if needed

## License

This project is created for educational purposes as part of JavaRush Module 1.
