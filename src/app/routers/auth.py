from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.schemas import UserRegisterRequest, UserRegisterResponse, Token
from datetime import datetime
from utils.security import hash_password, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from models import User
from database.db import get_session
import uuid
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegisterRequest, db: Session = Depends(get_session)):



    # Έλεγχος αν υπάρχει ήδη το email Ή το username
    user_exists = db.query(User).filter((User.email == user_data.email) | (User.username == user_data.username)).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="Username or email already registered")


    # Hashing του password
    hashed_pwd = hash_password(user_data.password)

    # Δημιουργία του νέου χρήστη (Model)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        password_hash=hashed_pwd,
        role=user_data.role
    )

    # Αποθήκευση στη βάση
    db.add(new_user)
    db.commit()
    db.refresh(new_user) # Παίρνουμε πίσω το ID και το CreatedAt που έφτιαξε η βάση

    return new_user

@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(login_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):

   # Endpoint για το Login. Δέχεται Form Data (για το Swagger) και επιστρέφει JWT Token.

    # Αναζήτηση χρήστη με βάση το username
    user = db.query(User).filter(User.username == login_data.username).first()

    # Έλεγχος αν υπάρχει ο χρήστης
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Επαλήθευση κωδικού
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Δημιουργία του JWT Token (βάζουμε το ID του χρήστη στο 'sub')
    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Μετατροπή λεπτών σε δευτερόλεπτα
    }
