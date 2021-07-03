import asyncio
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from humanhash import humanize
import os

from .database import Base, database, engine
from .dependencies import cookie_authentication, jwt_authentication, fastapi_users, user_db
from .routers.registration import get_register_router
from .routers.design import router as design_router
from .schemas.user import UserDB, UserCreate
from .models.user import UserTable

# Load environment variables from the .env file
load_dotenv()

# load the registration passcode
REGISTER_PASSCODE = os.getenv("ISE_REGISTER_PASSCODE", "passcode")
ADMIN_EMAIL = os.getenv("ISE_ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ISE_ADMIN_PASSWORD", "admin")

# build the FastAPI application
app = FastAPI(
    title="ISE Design Module",
    description="Industrial and Systems Engineering Design Module",
    version="2.0.0"
)

# Add GZip middleware to allow compressed responses
app.add_middleware(GZipMiddleware)

# include the router for cookie authentication
app.include_router(
    fastapi_users.get_auth_router(cookie_authentication),
    prefix="",
    tags=["auth"],
)

# include the router for jwt authentication
app.include_router(
    fastapi_users.get_auth_router(jwt_authentication),
    prefix="/auth",
    tags=["auth"],
)

# add a callback to update the user name after registering
async def on_after_register(user: UserDB, request: Request):
    user.name = humanize(user.id.hex, words=2, separator=' ')
    await user_db.update(user)
# include the router for registration
app.include_router(
    get_register_router(fastapi_users, REGISTER_PASSCODE, on_after_register),
    prefix="",
    tags=["auth"],
)

# include the router for user management
app.include_router(
    fastapi_users.get_users_router(),
    prefix="/users",
    tags=["users"],
)

# include the router for design activities
app.include_router(
    design_router,
    prefix="/designs",
    tags=["design"],
    dependencies=[]
)

# Mount a static directory to the root (/) route for any other requests
app.mount("/", StaticFiles(directory="dist", html=True), name="frontend")

# connect to the database on startup
@app.on_event("startup")
async def startup():
    Base.metadata.create_all(engine)
    await database.connect()
    try:
        await fastapi_users.create_user(
            UserCreate(
                email=ADMIN_EMAIL,
                name="admin",
                password=ADMIN_PASSWORD,
                passcode=REGISTER_PASSCODE,
                is_superuser=True,
            )
        )
    except:
        print(f'Admin account {ADMIN_EMAIL} already exists, skipping.')

# disconnect from the database on shutdown
@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
