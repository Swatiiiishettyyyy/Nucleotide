from datetime import datetime, timedelta
from typing import Dict, Any
import jwt
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()

# Read secret and algorithm directly from .env
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_SECONDS = int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", 86400))


def create_access_token(data: Dict[str, Any], expires_delta: int = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(seconds=(expires_delta or ACCESS_TOKEN_EXPIRE_SECONDS))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token
