from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from app.models import GeneratePlanRequest, GeneratePlanResponse, GeneratePlanRequestAuth, PantryItem, HouseholdGoals
# Import multi-provider service (supports Groq FREE, OpenAI, Anthropic)
from app.ai_service_multi import AIService
from app.auth import get_current_user_id
from app.supabase_client import get_supabase_service, SupabaseService
import pdb

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="CartIQ API",
    description="AI-powered household meal planning and shopping assistant",
    version="1.0.0"
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI service (provider is set via LLM_PROVIDER env var)
ai_service = AIService()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "CartIQ API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    provider = os.getenv("LLM_PROVIDER", "groq")
    api_key_var = {
        "groq": "GROQ_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY"
    }.get(provider, "GROQ_API_KEY")

    return {
        "status": "healthy",
        "ai_provider": provider,
        "ai_model": getattr(ai_service, 'model', 'unknown'),
        "api_key_configured": bool(os.getenv(api_key_var))
    }


@app.post("/generate-plan", response_model=GeneratePlanResponse)
async def generate_plan(
    request: GeneratePlanRequestAuth,
    user_id: str = Depends(get_current_user_id),
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """
    Generate a personalized meal plan and shopping list (AUTHENTICATED)

    This endpoint:
    1. Verifies JWT token from Authorization header
    2. Fetches user's pantry and goals from Supabase database
    3. Generates AI-powered meal plan using configured LLM provider

    Required header:
        Authorization: Bearer <jwt_token>

    Request body:
        - intent: Natural language description of what you want
        - days: Number of days to plan for (default: 7)

    The user's pantry inventory and household goals are automatically
    fetched from the database using their authenticated user ID.

    Supports multiple LLM providers (set via LLM_PROVIDER env var):
    - groq (FREE) - Default
    - openai
    - anthropic
    """
    try:
        pdb.set_trace()
        # Fetch user's pantry items from database
        pantry_data = supabase.get_pantry_items(user_id)
        pantry_items = [
            PantryItem(
                name=item["name"],
                quantity=item["quantity"],
                unit=item.get("unit"),
                expires_at=item.get("expires_at")
            )
            for item in pantry_data
        ]

        # Fetch user's household goals from database
        goals_data = supabase.get_household_goals(user_id)
        household_goals = None
        if goals_data:
            household_goals = HouseholdGoals(
                budget=goals_data.get("budget"),
                household_size=goals_data.get("household_size"),
                dietary_restrictions=goals_data.get("dietary_restrictions", []),
                preferences=goals_data.get("preferences", [])
            )

        # Construct full request for AI service
        full_request = GeneratePlanRequest(
            intent=request.intent,
            pantry=pantry_items,
            goals=household_goals,
            days=request.days
        )

        # Generate plan using AI service
        plan = ai_service.generate_plan(full_request)
        return plan

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
