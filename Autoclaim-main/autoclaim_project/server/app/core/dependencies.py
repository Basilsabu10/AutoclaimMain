"""
FastAPI dependencies for injection.
Provides database sessions and authentication dependencies.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import verify_token
from app.db.database import get_db

# OAuth2 scheme for token extraction from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Args:
        token: JWT token extracted from Authorization header
        
    Returns:
        Dict with user email and role
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    role: str = payload.get("role")
    
    if email is None:
        raise credentials_exception
    
    return {"email": email, "role": role}


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency that requires the current user to be an admin.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        The current user dict if admin
        
    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
