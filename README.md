# sokolov-web-lab

Practical web development lab built with Flask and FastAPI. The project
combines authentication, SQLAlchemy models, external API integrations and a
small set of REST endpoints.

## Stack

- Python
- Flask
- FastAPI
- SQLAlchemy
- Flask-Login
- Jinja templates
- SQLite
- requests / httpx

## Features

- User registration and login with password hashing.
- Protected pages for authenticated users.
- Weather page with OpenWeather API integration.
- Currency rates from the NBRB API.
- News, reminders, task and validator endpoints through FastAPI.
- Basic internationalization support.
- Responsive HTML templates and dark UI styling.

## Configuration

Create environment variables based on `.env.example`:

```bash
FLASK_SECRET_KEY=change-me
OPENWEATHER_API_KEY=
GNEWS_API_KEY=
```

Do not commit real API keys or Flask secret keys.

## Local Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The Flask app runs on `http://localhost:5000`.
FastAPI routes are mounted under `/fastapi`.

## Project Status

Portfolio training project. Strongest points for CV: authentication, database
models, external API integrations, Flask/FastAPI routing and practical backend
structure.
