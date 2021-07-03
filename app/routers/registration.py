from typing import Callable, Optional, Type, cast
from fastapi import APIRouter, HTTPException, Request, status
from fastapi_users import FastAPIUsers, models
from fastapi_users.router.common import ErrorCode, run_handler
from fastapi_users.user import (
    CreateUserProtocol,
    InvalidPasswordException,
    UserAlreadyExists,
    ValidatePasswordProtocol,
)

from ..schemas.user import User, UserCreate

# custom router to require matching passcode with new user registration
def get_register_router(
    fastapi_users: FastAPIUsers,
    register_passcode: str,
    after_register: Optional[Callable[[models.UD, Request], None]] = None
) -> APIRouter:
    router = APIRouter()
    # route to register a new user
    @router.post(
        "/register",
        response_model=User,
        status_code=status.HTTP_201_CREATED
    )
    async def register(request: Request, user: UserCreate):
        # verify user-supplied passcode matches registration passcode
        if user.passcode != register_passcode:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect registration passcode."
            )
        # the remainder of this function is based on default fastapi-users code
        user = cast(models.BaseUserCreate, user)
        if fastapi_users.validate_password:
            try:
                await fastapi_users.validate_password(user.password, user)
            except InvalidPasswordException as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                        "reason": e.reason,
                    },
                )
        try:
            created_user = await fastapi_users.create_user(user, safe=True)
        except UserAlreadyExists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
            )
        if after_register:
            await run_handler(after_register, created_user, request)
        return created_user
    return router
