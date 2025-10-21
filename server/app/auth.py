from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.supabase_client import get_supabase_service, SupabaseService


# Security scheme for Bearer token
security = HTTPBearer()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: SupabaseService = Depends(get_supabase_service)
) -> str:
    """
    FastAPI dependency to extract and verify JWT token from Authorization header

    Args:
        credentials: HTTP Bearer token from Authorization header
        supabase: Supabase service instance

    Returns:
        user_id: The authenticated user's ID

    Raises:
        HTTPException: 401 Unauthorized if token is invalid or missing
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        user_id = supabase.verify_token(token)
        return user_id
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}"
        )
