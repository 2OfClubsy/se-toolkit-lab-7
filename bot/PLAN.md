# LMS Telegram Bot — Implementation Roadmap

## Project Overview

We're developing a Telegram bot that serves as a conversational interface to the LMS backend. Users can check system status, browse laboratory assignments and grades, or ask questions using natural language. The bot leverages an LLM to interpret user requests and retrieve the appropriate data.

## Core Architecture Principle

The architecture centers on **testable handlers**—command logic implemented as pure functions that accept input and return text output. These handlers remain completely decoupled from Telegram, enabling three usage modes:
- `--test` flag for command-line validation
- Unit testing without external dependencies
- Production Telegram integration

This **separation of concerns** approach ensures business logic can be thoroughly tested without requiring a live Telegram connection.

## Task 1: Project Foundation

Establish the basic project structure:

1. **`bot/bot.py`** — Main entry point with `--test` capability
   - `uv run bot.py --test "/start"` outputs response to console
   - Standard execution launches the Telegram bot

2. **`bot/handlers/`** — Command handlers isolated from Telegram
   - Implement: `/start`, `/help`, `/health`, `/labs`, `/scores`
   - Begin with placeholder responses

3. **`bot/config.py`** — Environment configuration from `.env.bot.secret`

4. **`bot/pyproject.toml`** — Package dependencies: `aiogram`, `httpx`, `pydantic-settings`

5. **`.env.bot.secret`** — Credentials storage: `BOT_TOKEN`, `LMS_API_BASE_URL`, `LMS_API_KEY`

## Task 2: API Integration

Connect to the actual LMS backend:

1. **`bot/services/lms_client.py`** — API client implementation
   - Implement Bearer token authentication across all requests
   - Expose methods: `get_health()`, `get_labs()`, `get_scores(lab_id)`
   - Implement robust error handling for timeouts, authentication failures, and server errors

2. **Enhance handlers** to consume the API service instead of placeholders

3. **Graceful degradation** — Display user-friendly messages when backend is unavailable

## Task 3: Natural Language Understanding

Enable plain-text question handling:

1. **`bot/services/llm_client.py`** — LLM integration with tool-calling capabilities

2. **Tool definitions** for LLM function calling:
   - `get_health()` — retrieve system status
   - `get_labs()` — fetch available lab exercises
   - `get_scores(lab_id)` — obtain grades for specific lab

3. **Intent router** — Process user messages by having the LLM select appropriate tools, execute them, and return results

Success depends on well-crafted tool descriptions—clear documentation of each tool's purpose and usage is more critical than complex prompt engineering.

## Task 4: Containerization and Documentation

Prepare for production deployment:

1. **`bot/Dockerfile`** — Build image using Python 3.14 slim with `uv` package manager

2. **`docker-compose.yml` update** — Add bot service with environment variables

3. **Container networking** — Configure inter-container communication using service names
   - Backend endpoint becomes `http://backend:42002` within the bot container

4. **Documentation** — Comprehensive README with deployment procedures

## Project Structure

```
bot/
├── bot.py              # Application entry point
├── config.py           # Configuration management
├── pyproject.toml      # Dependency specification
├── PLAN.md             # Development roadmap
├── handlers/
│   └── commands.py     # Command implementations
└── services/
    ├── lms_client.py   # Backend API wrapper (Task 2)
    └── llm_client.py   # LLM integration (Task 3)
```

## Testing Workflow

```bash
cd bot
uv sync
uv run bot.py --test "/start"
uv run bot.py --test "/health"
uv run bot.py --test "/labs"
```

Each command should produce output and exit successfully with code 0.

## Development Process

For each task:
1. Create corresponding issue
2. Create feature branch: `git checkout -b task-1-scaffold`
3. Implement, test, commit changes
4. Submit pull request with `Closes #...` reference
5. Partner review and merge