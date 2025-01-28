from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from api.v1.router import router
from pydantic import BaseModel
from core.config import settings
from datetime import timedelta
from utils.auth import create_access_token
import logging
from utils.logging_config import setup_logging
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

#token for auth
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#Login configuration at the start of the app
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="APPY",
    description="API protegida con JWT",
    version="1.0",
    security=[{
        "BearerAuth": []
    }],
)

#initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

#middleware for rate liimter
app.state.limiter = limiter

#rate limit exceeded error handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_error(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Try again later."},
    )

#middleware to log every request
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Solicitud: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Respuesta: {response.status_code}")
    return response

#for login and generate token
class LoginRequest(BaseModel):
    username: str
    password: str

fake_users_db = {
    "admin": {"username": "admin", "password": "123456"},
}

#router endpoints
app.include_router(router)

@app.post("/login")
def login(data: LoginRequest):
    user = fake_users_db.get(data.username)
    if not user or user["password"] != data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}