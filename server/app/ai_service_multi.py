import os
import json
from typing import Dict, Any
from enum import Enum
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from app.models import GeneratePlanRequest, GeneratePlanResponse


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    GROQ = "groq"           # FREE - Fast, generous free tier
    OPENAI = "openai"       # Paid
    ANTHROPIC = "anthropic" # Paid


class AIService:
    """
    Multi-provider AI service for meal planning

    Supports:
    - Groq (FREE - recommended for testing)
    - OpenAI
    - Anthropic (Claude)
    """

    def __init__(self, provider: str = None):
        """
        Initialize AI service with specified provider

        Args:
            provider: One of 'groq', 'openai', 'anthropic'
                     Defaults to env var LLM_PROVIDER or 'groq'
        """
        self.provider = provider or os.getenv("LLM_PROVIDER", "groq")

        # Set up Jinja2 template environment
        prompts_dir = Path(__file__).parent.parent / "prompts"
        self.jinja_env = Environment(loader=FileSystemLoader(prompts_dir))

        if self.provider == LLMProvider.GROQ:
            self._init_groq()
        elif self.provider == LLMProvider.OPENAI:
            self._init_openai()
        elif self.provider == LLMProvider.ANTHROPIC:
            self._init_anthropic()
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _init_groq(self):
        """Initialize Groq client (FREE tier available)"""
        from groq import Groq
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"  # Fast and instant
        print(f"✓ Using Groq with {self.model} (FREE tier)")

    def _init_openai(self):
        """Initialize OpenAI client"""
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4-turbo-preview"
        print(f"✓ Using OpenAI with {self.model}")

    def _init_anthropic(self):
        """Initialize Anthropic (Claude) client"""
        from anthropic import Anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
        print(f"✓ Using Anthropic with {self.model}")

    def _build_prompt(self, request: GeneratePlanRequest) -> str:
        """Construct a detailed prompt for the LLM using Jinja2 template"""

        # Build pantry section
        pantry_items = "\n".join([
            f"  - {item.name}: {item.quantity} {item.unit or ''}"
            + (f" (expires: {item.expires_at})" if item.expires_at else "")
            for item in request.pantry
        ])

        # Build goals section
        goals_text = ""
        if request.goals:
            goals_parts = []
            if request.goals.budget:
                goals_parts.append(f"  - Budget: {request.goals.budget}")
            if request.goals.household_size:
                goals_parts.append(f"  - Household size: {request.goals.household_size} people")
            if request.goals.dietary_restrictions:
                goals_parts.append(f"  - Dietary restrictions: {', '.join(request.goals.dietary_restrictions)}")
            if request.goals.preferences:
                goals_parts.append(f"  - Preferences: {', '.join(request.goals.preferences)}")
            goals_text = "\n".join(goals_parts)

        # Load and render template
        template = self.jinja_env.get_template("meal_planner.j2")
        prompt = template.render(
            intent=request.intent,
            pantry_items=pantry_items,
            goals_text=goals_text,
            days=request.days
        )

        return prompt

    def _call_groq(self, prompt: str) -> str:
        """Call Groq API"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=1.0,
            max_tokens=4096
        )
        return response.choices[0].message.content

    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=1.0,
            max_tokens=4096
        )
        return response.choices[0].message.content

    def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic (Claude) API"""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            temperature=1.0,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    def generate_plan(self, request: GeneratePlanRequest) -> GeneratePlanResponse:
        """
        Generate a meal plan using configured LLM provider

        Args:
            request: The plan generation request

        Returns:
            A structured meal plan and shopping list
        """
        try:
            prompt = self._build_prompt(request)

            # Call appropriate provider
            if self.provider == LLMProvider.GROQ:
                response_text = self._call_groq(prompt)
            elif self.provider == LLMProvider.OPENAI:
                response_text = self._call_openai(prompt)
            elif self.provider == LLMProvider.ANTHROPIC:
                response_text = self._call_anthropic(prompt)
            else:
                raise ValueError(f"Unknown provider: {self.provider}")

            # Clean up potential markdown code blocks
            if response_text.startswith("```json"):
                response_text = response_text.split("```json")[1]
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
            if response_text.endswith("```"):
                response_text = response_text.rsplit("```", 1)[0]

            response_text = response_text.strip()

            # Parse JSON response
            plan_data = json.loads(response_text)

            # Validate and return as Pydantic model
            return GeneratePlanResponse(**plan_data)

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response as JSON: {str(e)}")
        except Exception as e:
            raise Exception(f"Error generating plan: {str(e)}")
