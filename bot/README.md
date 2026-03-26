Here is a paraphrased version of the LMS Telegram Bot documentation:

---

# LMS Telegram Bot

A Telegram bot that connects to the LMS (Learning Management System) backend, allowing users to view system status, browse labs and scores, and ask questions using natural language.

## Features

- **Slash commands**: `/start`, `/help`, `/health`, `/labs`, `/scores <lab>`
- **Natural language queries**: Users can ask questions like "which lab has the lowest pass rate?"
- **LLM-powered intent routing**: Uses a language model to interpret user requests and retrieve relevant data
- **Inline keyboard buttons**: Provides quick access to common actions

## Architecture

```
┌──────────────┐     ┌─────────────────┐     ┌──────────────┐
│  Telegram    │────▶│  Bot (aiogram)  │────▶│  LMS Backend │
│  User        │◀────│  + LLM Router   │◀────│  (FastAPI)   │
└──────────────┘     └─────────────────┘     └──────────────┘
```

## Quick Start

### Prerequisites

- Python 3.14.2
- [uv](https://docs.astral.sh/uv/) package manager
- Telegram bot token from [@BotFather](https://t.me/BotFather)
- A running LMS backend (see main README for setup)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/se-toolkit-lab-7
cd se-toolkit-lab-7/bot

# Install dependencies
uv sync
```

### Configuration

Create `.env.bot.secret` inside the `bot/` directory:

```bash
cp .env.bot.example .env.bot.secret
nano .env.bot.secret
```

Provide the required values:

```text
# Telegram bot token (required)
BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyz

# LMS API (required)
LMS_API_BASE_URL=http://localhost:42002
LMS_API_KEY=your-lms-api-key

# LLM API (required for natural language queries)
LLM_API_KEY=your-llm-api-key
LLM_API_BASE_URL=http://localhost:42005/v1
LLM_API_MODEL=coder-model
```

### Run Locally

```bash
# Test mode (commands)
uv run bot.py --test "/start"
uv run bot.py --test "/health"

# Test mode (natural language)
uv run bot.py --test "what labs are available"

# Start the bot
uv run bot.py
```

## Deploy

### Docker Deployment

The bot can be deployed as a Docker container alongside the LMS backend.

#### Prerequisites

- Docker and Docker Compose
- Backend services (PostgreSQL, LMS API) running
- `.env.docker.secret` configured in the root directory

#### Steps

1. **Build and start the bot container:**

   ```bash
   cd ~/se-toolkit-lab-7
   
   # Start all services including the bot
   docker compose --env-file .env.docker.secret up --build -d
   
   # Verify the bot is running
   docker compose --env-file .env.docker.secret ps bot
   ```

2. **View logs:**

   ```bash
   docker compose --env-file .env.docker.secret logs bot --tail 50
   ```

   Look for:
   - "Application started" — indicates successful connection
   - "HTTP Request: POST .../getUpdates" — shows polling activity

3. **Stop the bot:**

   ```bash
   docker compose --env-file .env.docker.secret stop bot
   ```

#### Environment Variables

The bot uses `.env.docker.secret` in the root directory. Required variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram bot token | `123456789:ABC...` |
| `LMS_API_BASE_URL` | Backend URL (use Docker service name) | `http://backend:8000` |
| `LMS_API_KEY` | Backend API key | `my-secret-key` |
| `LLM_API_KEY` | LLM API key | `your-llm-key` |
| `LLM_API_BASE_URL` | LLM service URL | `http://host.docker.internal:42005/v1` |
| `LLM_API_MODEL` | LLM model name | `coder-model` |

> **Note**: Inside Docker, use `http://backend:8000` for the backend instead of `localhost`. For the LLM running on the host, use `host.docker.internal`.

#### Troubleshooting

| Problem | Solution |
|---------|----------|
| Bot container restarts | Check logs: `docker compose logs bot` |
| `/health` fails | Ensure `LMS_API_BASE_URL=http://backend:8000` is set |
| LLM queries fail | Set `LLM_API_BASE_URL=http://host.docker.internal:42005/v1` |
| Missing env vars | Verify all variables are defined in `.env.docker.secret` |

### Manual Deployment (nohup)

For development, the bot can be run as a background process:

```bash
cd ~/se-toolkit-lab-7/bot

# Stop any existing bot instance
pkill -f "bot.py" 2>/dev/null

# Start in background
nohup uv run bot.py > bot.log 2>&1 &

# Confirm it's running
ps aux | grep bot.py
tail -f bot.log
```

## Testing

### Test Commands

```bash
# Basic commands
uv run bot.py --test "/start"
uv run bot.py --test "/help"
uv run bot.py --test "/health"
uv run bot.py --test "/labs"
uv run bot.py --test "/scores lab-01"

# Natural language queries
uv run bot.py --test "what labs are available"
uv run bot.py --test "which lab has the lowest pass rate"
uv run bot.py --test "show me top 5 students in lab-04"
```

### Verify Backend Connection

```bash
# Check if backend is reachable
curl -sf http://localhost:42002/docs

# Test items endpoint
curl -sf http://localhost:42002/items/ -H "Authorization: Bearer YOUR_API_KEY"
```

## Project Structure

```
bot/
├── bot.py                 # Main entry point
├── config.py              # Configuration loader
├── pyproject.toml         # Dependencies
├── Dockerfile             # Container configuration
├── handlers/
│   ├── basic/             # /start, /help commands
│   ├── commands/          # /health, /labs, /scores commands
│   └── natural_language/  # LLM-based intent routing
├── services/
│   ├── api_client.py      # LMS API client
│   ├── llm_client.py      # LLM API client
│   └── intent_router.py   # Tool-calling logic
└── keyboards/
    └── __init__.py        # Inline keyboard layouts
```

## License

MIT