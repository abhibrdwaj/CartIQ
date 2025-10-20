"""
Test script for the CartIQ API with hardcoded data
Run this after starting the server to test the /generate-plan endpoint
"""
import requests
import json
from pprint import pprint

# API endpoint
BASE_URL = "http://localhost:8000"

# Hardcoded test data representing a typical user scenario
test_request = {
    "intent": "I need a cheap, quick plan for the week using the items I already have. I'm trying to save money this month.",
    "days": 7,
    "pantry": [
        {
            "name": "Rice",
            "quantity": "2",
            "unit": "cups"
        },
        {
            "name": "Chicken breast",
            "quantity": "1",
            "unit": "lb",
            "expires_at": "2025-10-22"
        },
        {
            "name": "Canned tomatoes",
            "quantity": "2",
            "unit": "cans"
        },
        {
            "name": "Pasta",
            "quantity": "1",
            "unit": "box"
        },
        {
            "name": "Eggs",
            "quantity": "6",
            "unit": "eggs"
        },
        {
            "name": "Onions",
            "quantity": "3",
            "unit": "whole"
        },
        {
            "name": "Garlic",
            "quantity": "1",
            "unit": "head"
        },
        {
            "name": "Olive oil",
            "quantity": "1/2",
            "unit": "bottle"
        },
        {
            "name": "Frozen vegetables",
            "quantity": "1",
            "unit": "bag"
        }
    ],
    "goals": {
        "budget": "under $30 for the week",
        "household_size": 2,
        "dietary_restrictions": [],
        "preferences": ["quick meals", "minimal cleanup"]
    }
}


def test_health_check():
    """Test the health check endpoint"""
    print("\n" + "="*60)
    print("Testing Health Check...")
    print("="*60)

    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        pprint(response.json())
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_generate_plan():
    """Test the meal plan generation endpoint"""
    print("\n" + "="*60)
    print("Testing Meal Plan Generation...")
    print("="*60)
    print("\nRequest Data:")
    print(json.dumps(test_request, indent=2))

    try:
        response = requests.post(
            f"{BASE_URL}/generate-plan",
            json=test_request,
            headers={"Content-Type": "application/json"}
        )

        print(f"\nStatus Code: {response.status_code}")

        if response.status_code == 200:
            plan = response.json()
            print("\n✅ SUCCESS! Generated Plan:")
            print("\n" + "-"*60)
            print("SUMMARY:")
            print("-"*60)
            print(plan.get("summary", ""))

            print("\n" + "-"*60)
            print("MEAL PLAN:")
            print("-"*60)
            for meal in plan.get("meal_plan", [])[:5]:  # Show first 5 meals
                print(f"Day {meal['day']} - {meal['meal_type'].title()}: {meal['dish_name']}")
            print(f"... ({len(plan.get('meal_plan', []))} total meals)")

            print("\n" + "-"*60)
            print("SHOPPING LIST:")
            print("-"*60)
            for item in plan.get("shopping_list", [])[:10]:  # Show first 10 items
                priority = item.get('priority', 'N/A')
                cost = item.get('estimated_cost', 'N/A')
                print(f"  • {item['name']} - {item['quantity']} [{priority}] {cost}")

            print("\n" + "-"*60)
            print(f"TOTAL ESTIMATED COST: {plan.get('total_estimated_cost', 'N/A')}")
            print("-"*60)

            if plan.get("tips"):
                print("\n" + "-"*60)
                print("TIPS:")
                print("-"*60)
                for tip in plan["tips"]:
                    print(f"  💡 {tip}")

            return True
        else:
            print(f"❌ Error: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 CartIQ API Test Suite")
    print("="*60)

    # Test health check
    health_ok = test_health_check()

    if not health_ok:
        print("\n❌ Server is not healthy. Make sure it's running!")
        print("Start the server with: cd server && python -m app.main")
        return

    # Test plan generation
    test_generate_plan()

    print("\n" + "="*60)
    print("✅ Tests Complete!")
    print("="*60)


if __name__ == "__main__":
    main()
