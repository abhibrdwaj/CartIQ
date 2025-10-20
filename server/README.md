# CartIQ Server (FastAPI Backend)

This is the AI brain of CartIQ - a minimal FastAPI backend that powers intelligent meal planning and shopping list generation.

## Features

- **Single AI Endpoint**: `/generate-plan` - Takes user intent + pantry + goals, returns structured meal plans
- **Claude AI Integration**: Uses Anthropic's Claude API for intelligent, context-aware planning
- **Type-Safe**: Built with Pydantic models for request/response validation
- **CORS Enabled**: Ready for frontend integration

## Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your GROQ API key
# Get your key from: https://console.groq.com/
```

Your `.env` should look like:
```
GROQ_API_KEY=sk-ant-api03-...
PORT=8000
HOST=0.0.0.0
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 3. Run the Server

```bash
# From the server directory
python -m app.main
```

The server will start on `http://localhost:8000`

## Testing

### Quick Test with Hardcoded Data

```bash
# In one terminal, start the server
python -m app.main

# In another terminal, run the test script
python tests/test_api.py
```

This will test the `/generate-plan` endpoint with realistic pantry data.

### Manual Testing with cURL

```bash
curl -X POST "http://localhost:8000/generate-plan" \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "I need a cheap, quick plan for the week using items I have",
    "days": 7,
    "pantry": [
      {"name": "Rice", "quantity": "2", "unit": "cups"},
      {"name": "Eggs", "quantity": "6", "unit": "eggs"}
    ],
    "goals": {
      "budget": "under $30",
      "household_size": 2,
      "preferences": ["quick meals"]
    }
  }'
```

## API Documentation

Once the server is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Project Structure

```
server/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app & /generate-plan endpoint
│   ├── models.py         # Pydantic request/response models
│   └── ai_service.py     # Claude AI integration
├── tests/
│   ├── __init__.py
│   └── test_api.py      # Test script with hardcoded data
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Core Endpoint

### POST `/generate-plan`

**Request Body:**
```json
{
  "intent": "Natural language description of what the user wants",
  "days": 7,
  "pantry": [
    {
      "name": "Rice",
      "quantity": "2",
      "unit": "cups",
      "expires_at": "2025-10-22"
    }
  ],
  "goals": {
    "budget": "under $50",
    "household_size": 2,
    "dietary_restrictions": ["vegetarian"],
    "preferences": ["quick meals", "low carb"]
  }
}
```

**Response:**
```json
{
  "summary": "Brief overview of the plan strategy",
  "meal_plan": [
    {
      "day": 1,
      "meal_type": "breakfast",
      "dish_name": "Scrambled Eggs with Toast",
      "ingredients_used": ["eggs", "bread"],
      "estimated_cost": "$2.50"
    }
  ],
  "shopping_list": [
    {
      "name": "Bread",
      "quantity": "1 loaf",
      "estimated_cost": "$3.50",
      "priority": "essential"
    }
  ],
  "total_estimated_cost": "$28.50",
  "tips": ["Use existing pantry items first", "Cook in batches"]
}
```

## Next Steps

- [ ] Add user authentication (integrate with Supabase Auth)
- [ ] Connect to Supabase database to fetch real user pantry/goals
- [ ] Add caching for frequently requested plans
- [ ] Add rate limiting
- [ ] Deploy to production (Railway, Render, or Fly.io)
