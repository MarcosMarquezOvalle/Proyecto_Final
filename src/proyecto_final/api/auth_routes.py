from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from proyecto_final.api.schemas import ErrorResponse, LoginRequest, TokenResponse
from proyecto_final.infrastructure.security.jwt_auth import (
    authenticate_user,
    create_access_token,
)

router = APIRouter(tags=["auth"])


@router.post(
    "/auth/login",
    response_model=TokenResponse,
    responses={401: {"model": ErrorResponse}},
    summary="Iniciar sesión",
    description="Autentica al usuario y devuelve un JWT de acceso.",
)
def login(payload: LoginRequest) -> TokenResponse:
    username = authenticate_user(payload.username, payload.password)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    return TokenResponse(access_token=create_access_token(username), token_type="bearer")
