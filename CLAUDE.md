# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CartIQ is an AI-powered household meal planning assistant that generates contextual shopping plans based on:
- User's natural language intent
- Current pantry inventory
- Household goals and constraints

The system uses a **multi-provider LLM architecture** supporting Groq (FREE), OpenAI, and Anthropic.

## Development Commands

### Client (Frontend) Setup

```bash
cd client
npm install
cp .env.example .env  # Configure Supabase and API URLs
npm run dev           # Runs on http://localhost:5173
```

### Client Build Commands

```bash
cd client
npm run build    # Production build
npm run preview  # Preview production build
npm run lint     # Run ESLint
```

### Server (Backend) Setup

```bash
cd server
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Configure LLM provider and API keys
python -m app.main        # Runs on http://localhost:8000 with auto-reload
```

### Testing

```bash
# From server directory with venv activated:

# Health check
curl http://localhost:8000/health

# API integration test (hardcoded data)
python tests/test_api.py

# Quick LLM provider connection test
python test_groq.py
```

### API Documentation

Interactive docs available when server is running:
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
├── client/                      # React frontend (Vite)
│   ├── src/
│   │   ├── main.jsx            # App entry point
│   │   ├── App.jsx             # Router and route definitions
│   │   ├── contexts/
│   │   │   └── AuthContext.jsx # Supabase auth state management
│   │   ├── components/
│   │   │   ├── ProtectedRoute.jsx  # Auth route wrapper
│   │   │   └── BrandingPanel.jsx   # Shared branding component
│   │   ├── pages/
│   │   │   ├── Login.jsx       # Login page
│   │   │   ├── SignUp.jsx      # Registration page
│   │   │   └── Dashboard.jsx   # Main authenticated view
│   │   └── lib/
│   │       └── supabase.js     # Supabase client initialization
│   ├── package.json
│   └── .env.example
│
└── server/                      # Python FastAPI backend
    ├── app/
    │   ├── main.py              # FastAPI app, /generate-plan endpoint
    │   ├── models.py            # Pydantic models with validation
    │   ├── ai_service_multi.py  # Multi-provider LLM service
    │   └── ai_service.py        # Legacy single-provider service
    ├── prompts/
    │   └── meal_planner.j2      # Jinja2 prompt template
    ├── tests/
    │   └── test_api.py          # API integration test
    ├── test_groq.py             # Quick LLM connection test
    ├── requirements.txt
    └── .env.example
```

## Frontend Architecture

### Authentication Flow

The frontend uses **Supabase Auth** with a React Context pattern:

1. **AuthContext** (`contexts/AuthContext.jsx`):
   - Centralized auth state management
   - Provides `user`, `session`, `loading` state
   - Exports `signUp()`, `signIn()`, `signOut()` methods
   - Auto-syncs with Supabase auth state changes

2. **ProtectedRoute** component:
   - Wraps authenticated routes
   - Redirects to `/login` if user not authenticated
   - Shows loading state during auth initialization

3. **Route structure** (in `App.jsx`):
   - Public: `/login`, `/signup`
   - Protected: `/dashboard` (requires auth)
   - Default: Redirects `/` to `/login`

### Client Configuration

**Environment variables** (`client/.env`):
- `VITE_SUPABASE_URL` - Supabase project URL
- `VITE_SUPABASE_ANON_KEY` - Supabase anonymous key
- `VITE_API_URL` - Backend API URL (default: http://localhost:8000)

**Key dependencies**:
- React 19.1 with React Router DOM 7.9
- Supabase JS client 2.76
- Vite 7.1 (build tool with HMR)

## Full-Stack Integration

The application is designed for eventual integration of:

**Current state:**
- Frontend: Authentication (Supabase) + routing + basic UI
- Backend: LLM-powered meal planning API (standalone, no auth yet)

**Integration points to implement:**
- Connect backend `/generate-plan` to authenticated frontend
- Add pantry CRUD operations (frontend → Supabase DB)
- Add household goals management (frontend → Supabase DB)
- Backend to fetch user data from Supabase before calling LLM

**Future extensions:**
- RAG/Store APIs - Real-time product pricing and availability
- Computer Vision - Receipt scanning and pantry recognition
- Lifecycle management - Expiration tracking and notifications
