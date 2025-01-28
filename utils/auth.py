# auth.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from core.config import settings

# Generar un token de acceso
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.ALGORITHM)
    return encoded_jwt

# Verificar y decodificar un token de acceso
def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
