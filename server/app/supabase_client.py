import os
from typing import List, Optional, Dict, Any
from supabase import create_client, Client
import jwt
from dotenv import load_dotenv

load_dotenv()


class SupabaseService:
    """
    Service for interacting with Supabase database and auth

    Handles:
    - JWT token verification
    - Fetching user pantry items
    - Fetching user household goals
    """

    def __init__(self):
        """Initialize Supabase client"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment variables"
            )

        self.client: Client = create_client(supabase_url, supabase_key)
        self.jwt_secret = os.getenv("SUPABASE_JWT_SECRET")

        if not self.jwt_secret:
            raise ValueError("SUPABASE_JWT_SECRET must be set in environment variables")

        print("✓ Supabase client initialized")

    def verify_token(self, token: str) -> str:
        """
        Verify JWT token and extract user_id

        Args:
            token: JWT token from Authorization header

        Returns:
            user_id: The authenticated user's ID

        Raises:
            ValueError: If token is invalid or expired
        """
        try:
            # Decode JWT token
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=["HS256"],
                audience="authenticated"
            )

            # Extract user ID from token payload
            user_id = payload.get("sub")
            if not user_id:
                raise ValueError("Token does not contain user ID")

            return user_id

        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {str(e)}")

    def get_pantry_items(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Fetch all pantry items for a user

        Args:
            user_id: The user's ID

        Returns:
            List of pantry items as dictionaries
        """
        try:
            response = self.client.table("pantry_items")\
                .select("*")\
                .eq("user_id", user_id)\
                .execute()

            return response.data if response.data else []

        except Exception as e:
            raise Exception(f"Error fetching pantry items: {str(e)}")

    def get_household_goals(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch household goals for a user

        Args:
            user_id: The user's ID

        Returns:
            Household goals as dictionary, or None if not set
        """
        try:
            response = self.client.table("household_goals")\
                .select("*")\
                .eq("user_id", user_id)\
                .single()\
                .execute()

            return response.data if response.data else None

        except Exception as e:
            # It's okay if user hasn't set goals yet
            if "No rows found" in str(e) or "PGRST116" in str(e):
                return None
            raise Exception(f"Error fetching household goals: {str(e)}")

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch user profile information

        Args:
            user_id: The user's ID

        Returns:
            User profile as dictionary, or None if not found
        """
        try:
            response = self.client.table("users")\
                .select("*")\
                .eq("id", user_id)\
                .single()\
                .execute()

            return response.data if response.data else None

        except Exception as e:
            raise Exception(f"Error fetching user profile: {str(e)}")


# Singleton instance
_supabase_service: Optional[SupabaseService] = None


def get_supabase_service() -> SupabaseService:
    """
    Get or create Supabase service singleton

    Returns:
        SupabaseService instance
    """
    global _supabase_service
    if _supabase_service is None:
        _supabase_service = SupabaseService()
    return _supabase_service
