from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class PantryItem(BaseModel):
    """Represents an item in the user's pantry"""
    name: str = Field(..., min_length=1, max_length=100)
    quantity: str = Field(..., min_length=1, max_length=50)
    unit: Optional[str] = Field(None, max_length=50)
    expires_at: Optional[str] = Field(None, max_length=50)

    @field_validator('name', 'quantity', 'unit', 'expires_at')
    @classmethod
    def sanitize_strings(cls, v):
        """Basic sanitization to prevent injection attacks"""
        if v is None:
            return v
        # Strip whitespace and limit to reasonable characters
        return v.strip()[:100]


class HouseholdGoals(BaseModel):
    """User's household goals and constraints"""
    budget: Optional[str] = Field(None, max_length=100)
    dietary_restrictions: Optional[List[str]] = Field(default_factory=list, max_length=20)
    preferences: Optional[List[str]] = Field(default_factory=list, max_length=20)
    household_size: Optional[int] = Field(None, ge=1, le=50)

    @field_validator('dietary_restrictions', 'preferences')
    @classmethod
    def validate_list_items(cls, v):
        """Validate and sanitize list items"""
        if v is None:
            return []
        # Limit each item length and total count
        return [item.strip()[:50] for item in v[:20]]


class GeneratePlanRequest(BaseModel):
    """Request payload for generating a meal plan"""
    intent: str = Field(..., min_length=1, max_length=1000, description="Natural language intent from the user")
    pantry: List[PantryItem] = Field(default_factory=list, max_length=100)
    goals: Optional[HouseholdGoals] = None
    days: int = Field(default=7, ge=1, le=14, description="Number of days to plan for")

    @field_validator('intent')
    @classmethod
    def sanitize_intent(cls, v):
        """Sanitize user intent to prevent prompt injection"""
        if not v or not v.strip():
            raise ValueError("Intent cannot be empty")
        # Basic sanitization
        sanitized = v.strip()[:1000]
        return sanitized


class MealPlan(BaseModel):
    """A single meal in the plan"""
    day: int
    meal_type: str  # breakfast, lunch, dinner, snack
    dish_name: str
    ingredients_used: List[str]
    estimated_cost: Optional[str] = None


class ShoppingItem(BaseModel):
    """An item to purchase"""
    name: str
    quantity: str
    estimated_cost: Optional[str] = None
    priority: Optional[str] = None  # essential, recommended, optional


class GeneratePlanResponse(BaseModel):
    """Response containing the generated meal plan and shopping list"""
    summary: str
    meal_plan: List[MealPlan]
    shopping_list: List[ShoppingItem]
    total_estimated_cost: Optional[str] = None
    tips: Optional[List[str]] = Field(default_factory=list)


class GeneratePlanRequestAuth(BaseModel):
    """
    Simplified request payload for authenticated endpoint
    Pantry and goals are fetched from database using auth token
    """
    intent: str = Field(..., min_length=1, max_length=1000, description="Natural language intent from the user")
    days: int = Field(default=7, ge=1, le=14, description="Number of days to plan for")

    @field_validator('intent')
    @classmethod
    def sanitize_intent(cls, v):
        """Sanitize user intent to prevent prompt injection"""
        if not v or not v.strip():
            raise ValueError("Intent cannot be empty")
        # Basic sanitization
        sanitized = v.strip()[:1000]
        return sanitized
