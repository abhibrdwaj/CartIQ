"""
Quick test script to verify Groq API connection
"""
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Initialize Groq client
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("❌ GROQ_API_KEY not found in .env file")
    exit(1)

print(f"✓ API Key found: {api_key[:20]}...")

client = Groq(api_key=api_key)
model = "llama-3.1-8b-instant"

print(f"✓ Using model: {model}")
print("\n" + "="*60)
print("Testing Groq API with a simple meal planning request...")
print("="*60 + "\n")

# Test request
test_prompt = """You are CartIQ, an AI meal planning assistant.

USER REQUEST: I need cheap meals for 3 days using what I have.

PANTRY:
- Rice: 2 cups
- Eggs: 6 eggs
- Canned tomatoes: 2 cans

BUDGET: Under $15

Please generate a simple meal plan in JSON format with this structure:
{
  "summary": "brief overview",
  "meal_plan": [
    {"day": 1, "meal_type": "breakfast", "dish_name": "dish", "ingredients_used": ["rice", "eggs"]}
  ],
  "shopping_list": [
    {"name": "item", "quantity": "amount", "estimated_cost": "$X"}
  ]
}

Return ONLY the JSON, no markdown.
"""

try:
    print("🔄 Calling Groq API...")
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": test_prompt}],
        temperature=1.0,
        max_tokens=2048
    )

    result = response.choices[0].message.content

    print("\n✅ SUCCESS! Groq API Response:")
    print("="*60)
    print(result)
    print("="*60)

    # Try to parse as JSON
    import json
    try:
        # Clean up markdown if present
        if result.startswith("```json"):
            result = result.split("```json")[1]
        if result.startswith("```"):
            result = result.split("```")[1]
        if result.endswith("```"):
            result = result.rsplit("```", 1)[0]

        result = result.strip()
        data = json.loads(result)

        print("\n✅ JSON Parse: SUCCESS")
        print(f"   - Summary: {data.get('summary', 'N/A')[:100]}...")
        print(f"   - Meals: {len(data.get('meal_plan', []))} meals")
        print(f"   - Shopping items: {len(data.get('shopping_list', []))} items")

    except json.JSONDecodeError as e:
        print(f"\n⚠️  JSON Parse: FAILED - {e}")
        print("The response is not valid JSON. May need prompt adjustment.")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("Check your API key and internet connection.")
