from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from app.models import GeneratePlanRequest, GeneratePlanResponse
# Import multi-provider service (supports Groq FREE, OpenAI, Anthropic)
from app.ai_service_multi import AIService

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
async def generate_plan(request: GeneratePlanRequest):
    """
    Generate a personalized meal plan and shopping list based on user's
    pantry, goals, and natural language intent.

    This is the core AI endpoint that:
    1. Takes user intent + pantry + goals
    2. Constructs a detailed prompt for the LLM
    3. Returns a structured meal plan and shopping list

    Supports multiple LLM providers (set via LLM_PROVIDER env var):
    - groq (FREE) - Default
    - openai
    - anthropic
    """
    try:
        plan = ai_service.generate_plan(request)
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
