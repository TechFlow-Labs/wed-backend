from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from environs import Env
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database.db import get_session
from models import User

env = Env()
env.read_env()

# JWT Settings 
SECRET_KEY = env.str("JWT_SECRET_KEY", "secret")
ALGORITHM = env.str("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = env.int("ACCESS_TOKEN_EXPIRE_MINUTES", 30)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hashing the password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Επαλήθευση αν το απλό κείμενο (password) ταιριάζει με το hash που έχουμε αποθηκευμένο.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    """
    Δημιουργεί ένα αληθινό JWT Token με τα δεδομένα του χρήστη.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(db: Session = Depends(get_session), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials",)
    try:
        # Αποκωδικοποιούμε το token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub") 
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    
    # Ψάχνουμε τον χρήστη στη βάση
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user    
