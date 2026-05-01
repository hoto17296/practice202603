from asyncio import sleep

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel

from lib.session import AuthSession, clear_session, get_session, set_session
from lib.user import UserRegistrationError, UserRegistrationErrorType, register_user, verify_user
from models import HTTPExceptionBody

router = APIRouter()


class Credentials(BaseModel):
    email: str
    password: str


@router.post(
    "/signup",
    responses={
        400: {"model": HTTPExceptionBody[UserRegistrationErrorType]},
        409: {"model": HTTPExceptionBody[UserRegistrationErrorType]},
    },
)
async def post_signup(credentials: Credentials, response: Response):
    try:
        user = await register_user(credentials.email, credentials.password)
    except UserRegistrationError as exc:
        if exc.type == "ALREADY_EXISTS":
            raise HTTPException(status_code=409, detail=exc.type) from exc
        else:
            raise HTTPException(status_code=400, detail=exc.type) from exc
    set_session(response, user)


@router.post("/signin", responses={400: {"model": HTTPExceptionBody}})
async def post_signin(credentials: Credentials, response: Response):
    user = await verify_user(credentials.email, credentials.password)
    if user is None:
        await sleep(1)
        raise HTTPException(status_code=400)
    set_session(response, user)


@router.post("/signout")
async def post_signout(response: Response):
    clear_session(response)


@router.get("/session", responses={401: {"model": HTTPExceptionBody}})
async def get_session_(session: AuthSession = Depends(get_session)) -> AuthSession:
    return session
