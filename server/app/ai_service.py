import os
import json
from typing import Dict, Any
from anthropic import Anthropic
from app.models import GeneratePlanRequest, GeneratePlanResponse


class AIService:
    """Service for interacting with Claude AI for meal planning"""

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"

    def _build_prompt(self, request: GeneratePlanRequest) -> str:
        """Construct a detailed prompt for Claude"""

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

        prompt = f"""You are CartIQ, an AI household planning assistant. Your job is to create practical, contextual meal plans and shopping lists.

USER INTENT:
{request.intent}

CURRENT PANTRY INVENTORY:
{pantry_items if pantry_items else "  (Empty pantry)"}

HOUSEHOLD GOALS & CONSTRAINTS:
{goals_text if goals_text else "  (No specific constraints provided)"}

PLANNING PERIOD: {request.days} days

Based on the above context, generate a comprehensive meal plan that:
1. Maximizes use of existing pantry items (especially those expiring soon)
2. Respects the household goals and constraints
3. Addresses the user's intent
4. Minimizes waste and cost
5. Provides variety and nutrition

Return your response as a JSON object with this exact structure:
{{
  "summary": "A 2-3 sentence overview of the plan strategy",
  "meal_plan": [
    {{
      "day": 1,
      "meal_type": "breakfast",
      "dish_name": "Name of the dish",
      "ingredients_used": ["ingredient1", "ingredient2"],
      "estimated_cost": "$X.XX"
    }}
  ],
  "shopping_list": [
    {{
      "name": "item name",
      "quantity": "amount with unit",
      "estimated_cost": "$X.XX",
      "priority": "essential|recommended|optional"
    }}
  ],
  "total_estimated_cost": "$XX.XX",
  "tips": ["helpful tip 1", "helpful tip 2"]
}}

IMPORTANT: Return ONLY the JSON object, no additional text or markdown formatting."""

        return prompt

    def generate_plan(self, request: GeneratePlanRequest) -> GeneratePlanResponse:
        """
        Generate a meal plan using Claude AI

        Args:
            request: The plan generation request

        Returns:
            A structured meal plan and shopping list
        """
        try:
            prompt = self._build_prompt(request)

            # Call Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=1.0,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract and parse the response
            response_text = message.content[0].text

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
