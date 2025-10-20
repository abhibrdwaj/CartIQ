# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CartIQ is an AI-powered household meal planning assistant that generates contextual shopping plans based on:
- User's natural language intent
- Current pantry inventory
- Household goals and constraints

The system uses a **multi-provider LLM architecture** supporting Groq (FREE), OpenAI, and Anthropic.

## Development Commands

### Server Setup

```bash
cd server
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # Then configure API keys
```

### Running the Server

```bash
cd server
source venv/bin/activate
python -m app.main
```

Server runs on `http://localhost:8000` with auto-reload enabled.

### Testing

```bash
# Health check
curl http://localhost:8000/health

# Quick API test with hardcoded data
python tests/test_api.py

# Quick LLM provider test
python test_groq.py
```

### API Documentation

Interactive docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Architecture

### Multi-Provider AI Service Pattern

The codebase supports **3 LLM providers** through a unified interface:

**Key file:** `server/app/ai_service_multi.py`

- **Provider selection:** Configured via `LLM_PROVIDER` environment variable
- **Initialization:** Each provider has dedicated `_init_*()` method
- **Unified interface:** Single `generate_plan()` method works with all providers
- **Default:** Groq (FREE tier with generous limits)

```python
# Provider switching (in .env)
LLM_PROVIDER=groq       # FREE - llama-3.1-8b-instant
LLM_PROVIDER=openai     # gpt-4-turbo-preview
LLM_PROVIDER=anthropic  # claude-3-5-sonnet
```

### Prompt Management with Jinja2

**Important:** Prompts are externalized to template files for easy iteration.

**Template location:** `server/prompts/meal_planner.j2`

The `_build_prompt()` method in `ai_service_multi.py`:
1. Constructs context from request data (pantry items, goals)
2. Loads Jinja2 template from `prompts/meal_planner.j2`
3. Renders template with variables: `intent`, `pantry_items`, `goals_text`, `days`

**To modify prompts:** Edit the `.j2` file directly, no code changes needed.

### Request Flow

1. **FastAPI endpoint** (`app/main.py`) receives POST to `/generate-plan`
2. **Pydantic validation** (`app/models.py`) validates and sanitizes input
3. **AI Service** (`app/ai_service_multi.py`):
   - Builds prompt using Jinja2 template
   - Calls configured LLM provider
   - Cleans markdown artifacts from response
   - Parses JSON response
4. **Response** returned as structured `GeneratePlanResponse` model

### Data Models

**File:** `server/app/models.py`

Key models:
- `GeneratePlanRequest` - User intent + pantry + goals
- `GeneratePlanResponse` - Meal plan + shopping list + tips
- `PantryItem` - Individual pantry inventory item
- `HouseholdGoals` - Budget, dietary restrictions, preferences

**Security features:**
- Field validators sanitize all string inputs
- Length limits prevent DOS attacks (intent: 1000 chars, pantry: 100 items)
- Range validation for numerical fields (days: 1-14, household_size: 1-50)

## Configuration

### Environment Variables

**File:** `server/.env` (copy from `.env.example`)

Required:
- `LLM_PROVIDER` - Provider choice: groq, openai, anthropic
- `GROQ_API_KEY` or `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`

Optional:
- `PORT` - Server port (default: 8000)
- `HOST` - Server host (default: 0.0.0.0)
- `CORS_ORIGINS` - Comma-separated allowed origins

### Adding New LLM Providers

1. Add provider to `LLMProvider` enum in `ai_service_multi.py`
2. Create `_init_<provider>()` method
3. Create `_call_<provider>()` method
4. Update `generate_plan()` routing logic
5. Update `.env.example` with new API key variable

## Project Structure

```
CartIQ/
├── server/
│   ├── app/
│   │   ├── main.py              # FastAPI app, /generate-plan endpoint
│   │   ├── models.py            # Pydantic models with validation
│   │   ├── ai_service_multi.py  # Multi-provider LLM service
│   │   └── ai_service.py        # Legacy single-provider service
│   ├── prompts/
│   │   └── meal_planner.j2      # Jinja2 prompt template
│   ├── tests/
│   │   └── test_api.py          # API integration test
│   ├── test_groq.py             # Quick LLM connection test
│   ├── requirements.txt
│   └── .env.example
└── README.md
```

## Future Integration Points

The backend is designed to integrate with:
- **Supabase** - For user authentication and persistent storage (pantry, goals)
- **Frontend** - React/Svelte/Vue.js with CORS pre-configured
- **RAG/Store APIs** - Real-time product pricing and availability
- **Computer Vision** - Receipt scanning and pantry recognition
