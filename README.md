# AI Career Guidance Chatbot

A Flask + SQLite + Gemini AI web application for student career guidance.

## Features
- AI career guidance chatbot
- Career directory
- Personalized career recommendation demo
- Career roadmaps
- Login and registration
- Saved chat history for logged-in users
- Responsive modern UI

## Quick start — Windows PowerShell

```powershell
cd AI_Career_Guidance_Chatbot
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
notepad .env
python app.py
```

Then open: http://127.0.0.1:5000

If PowerShell blocks activation:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## API setup
1. Create a Gemini API key in Google AI Studio.
2. Put it in `.env` as `GEMINI_API_KEY=...`.
3. Never put the key in `static/js/*.js` or commit `.env`.
4. Restart Flask after changing `.env`.

## Demo mode
The app still opens if no Gemini key is configured. The chatbot returns a setup message instead of calling the AI service.

## Main routes
- `/` Home
- `/chat` AI Chat
- `/careers` Careers
- `/roadmaps` Roadmaps
- `/about` About
- `/login` Login
- `/register` Register
- `/api/chat` Chat API
- `/api/recommend` Recommendation API
- `/api/history` Saved history API

## Database
`career_guidance.db` is automatically created on first run. `schema.sql` contains the table definitions.
