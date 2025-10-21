# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CartIQ is an AI-powered household meal planning assistant that generates contextual shopping plans based on:
- User's natural language intent
- Current pantry inventory (stored in Supabase)
- Household goals and constraints (stored in Supabase)

The system uses:
- **Supabase** for authentication and data persistence
- **Multi-provider LLM architecture** supporting Groq (FREE), OpenAI, and Anthropic

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

### Database Setup

1. Create a Supabase project at https://app.supabase.com/
2. Run the SQL schema from `database/schema.sql` in the Supabase SQL editor
3. Copy your Supabase credentials to `.env`:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY` (from Settings > API)
   - `SUPABASE_JWT_SECRET` (from Settings > API > JWT Secret)

### Testing

```bash
# Health check
curl http://localhost:8000/health

# Test authenticated endpoint (requires valid JWT token)
curl -X POST http://localhost:8000/generate-plan \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"intent": "Plan meals for the week", "days": 7}'
```

### API Documentation

Interactive docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Architecture

### Supabase Authentication & Data Persistence

**Key files:**
- `server/app/supabase_client.py` - Supabase client and data access
- `server/app/auth.py` - JWT authentication dependency
- `server/database/schema.sql` - Database schema

**Authentication Flow:**
1. User signs up/logs in through Supabase Auth → receives JWT token
2. Client sends requests with `Authorization: Bearer <token>` header
3. FastAPI dependency (`get_current_user_id`) verifies JWT and extracts user_id
4. Backend fetches user's pantry and goals from database
5. AI generates personalized meal plan using user's data

**Database Tables:**
- `users` - User profiles (first_name, last_name) linked to Supabase Auth
- `pantry_items` - User's pantry inventory
- `household_goals` - User's budget, dietary restrictions, preferences

**Row Level Security (RLS):**
- All tables have RLS policies enabled
- Users can only access their own data
- Service role key bypasses RLS for backend queries

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

1. **Client** sends POST to `/generate-plan` with:
   - Authorization header with JWT token
   - Request body: `{"intent": "...", "days": 7}`

2. **Authentication** (`app/auth.py`):
   - Verifies JWT token signature
   - Extracts user_id from token payload
   - Returns 401 if invalid/expired

3. **Data Fetching** (`app/supabase_client.py`):
   - Fetches user's pantry items from database
   - Fetches user's household goals from database
   - Constructs full `GeneratePlanRequest` internally

4. **AI Service** (`app/ai_service_multi.py`):
   - Builds prompt using Jinja2 template with user's data
   - Calls configured LLM provider
   - Cleans markdown artifacts from response
   - Parses JSON response

5. **Response** returned as structured `GeneratePlanResponse` model

### Data Models

**File:** `server/app/models.py`

Key models:
- `GeneratePlanRequestAuth` - Simplified authenticated request (intent + days only)
- `GeneratePlanRequest` - Internal model with full data (intent + pantry + goals)
- `GeneratePlanResponse` - Meal plan + shopping list + tips
- `PantryItem` - Individual pantry inventory item
- `HouseholdGoals` - Budget, dietary restrictions, preferences

**Security features:**
- JWT token authentication required for all endpoints
- Field validators sanitize all string inputs
- Length limits prevent DOS attacks (intent: 1000 chars, pantry: 100 items)
- Range validation for numerical fields (days: 1-14, household_size: 1-50)
- Row Level Security (RLS) ensures users only access their own data

## Configuration

### Environment Variables

**File:** `server/.env` (copy from `.env.example`)

Required:
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY` - Service role key from Supabase settings
- `SUPABASE_JWT_SECRET` - JWT secret for token verification
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
│   │   ├── auth.py              # JWT authentication dependency
│   │   ├── supabase_client.py   # Supabase client & data access
│   │   └── ai_service.py        # Legacy single-provider service
│   ├── database/
│   │   └── schema.sql           # Supabase database schema
│   ├── prompts/
│   │   └── meal_planner.j2      # Jinja2 prompt template
│   ├── tests/
│   │   └── test_api.py          # API integration test
│   ├── test_groq.py             # Quick LLM connection test
│   ├── requirements.txt
│   └── .env.example
└── CLAUDE.md
```

## Future Integration Points

The backend is designed to integrate with:
- **Frontend** - React/Svelte/Vue.js with CORS pre-configured
- **RAG/Store APIs** - Real-time product pricing and availability
- **Computer Vision** - Receipt scanning and pantry recognition

## Supabase Integration (COMPLETED)

✅ **Authentication** - JWT token-based authentication with Supabase Auth
✅ **User Profiles** - User table with first_name, last_name
✅ **Pantry Management** - Store and fetch user's pantry items
✅ **Household Goals** - Store user preferences, dietary restrictions, budget
✅ **Row Level Security** - Database policies ensure data isolation
