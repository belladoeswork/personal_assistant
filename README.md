# Personal Assistant

A personal assistant application that can handle emails, provide weather updates, and convert text to speech.

## Setup

1. Clone the repository:
```bash
git clone https://github.com/belladoeswork/personal_assistant.git
cd personal_assistant
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up environment variables:
   - Copy `.env.example` to `.env.local`
   - Fill in your API keys and credentials in `.env.local`
```bash
cp .env.example .env.local
```

4. Set up Gmail API:
   - Follow [Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart/python)
   - Save your `credentials.json` in the project root
   - Run the app once to generate `token.json`

5. Run the application:
```bash
python app.py
```

## Features

- Email management with Gmail API
- Weather updates using Open-Meteo API
- Text-to-speech using ElevenLabs API
- Conversation history stored in Supabase

## Environment Variables

The following environment variables are required:

- `OPENAI_API_KEY`: Your OpenAI API key
- `LANGCHAIN_API_KEY`: Your LangChain API key
- `ELEVENLABS_API_KEY`: Your ElevenLabs API key
- `VOICE_ID`: Your ElevenLabs voice ID
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_ANON_KEY`: Your Supabase anonymous key

## Contributing

1. Create a feature branch
2. Make your changes
3. Submit a pull request

## Security

- Never commit `.env.local` or any other files containing sensitive information
- Always use environment variables for sensitive data
- Keep your `credentials.json` and `token.json` secure