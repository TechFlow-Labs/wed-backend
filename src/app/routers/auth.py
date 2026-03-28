from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.users import UserRegisterRequest, UserRegisterResponse, Token, VendorCreateResponse, VendorCreateRequest
from datetime import datetime
from utils.security import hash_password, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from models import User, Reservations, PartnerProfiles
from database.db import get_session
import uuid
from fastapi.security import OAuth2PasswordRequestForm
from utils.security import get_current_user

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
        role="COUPLE"
    )

    # Αποθήκευση στη βάση
    db.add(new_user)
    db.commit()
    db.refresh(new_user) # Παίρνουμε πίσω το ID και το CreatedAt που έφτιαξε η βάση


    # -------------------------------------------------------------------
    # LINK PAST GUEST RESERVATIONS
    # Find any reservations made with this email before they registered,
    # and link them to this newly created user ID.
    # -------------------------------------------------------------------
    db.query(Reservations).filter(
        Reservations.guest_email == new_user.email,
        Reservations.couple_id.is_(None) # Safety check: Only claim unassigned ones
    ).update(
        {"couple_id": new_user.id}, 
        synchronize_session=False
    )
    
    # Commit the updates to the reservations table
    db.commit()
    # -------------------------------------------------------------------

    return new_user


@router.post("/register/partners", response_model=VendorCreateResponse, status_code=status.HTTP_201_CREATED)
def create_vendor_account(vendor_data: VendorCreateRequest, db: Session = Depends(get_session),current_user: User = Depends(get_current_user)):
    
    # 1. SECURITY CHECK: Only Admins allowed!
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You do not have permission to perform this action"
        )

    # 2. Check if username or email already exists
    user_exists = db.query(User).filter(
        (User.email == vendor_data.email) | (User.username == vendor_data.username)
    ).first()
    
    if user_exists:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    # 3. Hash the password
    hashed_pwd = hash_password(vendor_data.password)

    # 4. Create the User record (Role = PARTNER)
    new_user = User(
        username=vendor_data.username,
        email=vendor_data.email,
        password_hash=hashed_pwd,
        first_name=vendor_data.first_name,
        last_name=vendor_data.last_name,
        role="PARTNER" # Hardcoded, so the admin can't accidentally make another admin
    )

    db.add(new_user)
    
    # flush() pushes the new user to PostgreSQL to generate the UUID, 
    # but it DOES NOT permanently save (commit) it yet. 
    # If anything fails after this point, the whole process rolls back!
    db.flush() 

    # 5. Create the linked Partner Profile using the brand new ID
    new_profile = PartnerProfiles(
        user_id=new_user.id,
        business_name=vendor_data.business_name,
        category=vendor_data.category,
        description=vendor_data.description
    )
    
    db.add(new_profile)

    # 6. Commit BOTH records permanently to the database
    db.commit()
    
    # 7. Return a custom response dictionary combining the data
    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role,
        "business_name": new_profile.business_name
    }


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(login_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):

   # Endpoint για το Login. Δέχεται Form Data (για το Swagger) και επιστρέφει JWT Token.

    # Αναζήτηση χρήστη με βάση το username
    user = db.query(User).filter(User.username == login_data.username).first()

    # Έλεγχος αν υπάρχει ο χρήστης
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Επαλήθευση κωδικού
    try:
        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Δημιουργία του JWT Token (βάζουμε το ID του χρήστη στο 'sub')
        access_token = create_access_token(data={"sub": str(user.id)})
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Some error occurred during password verification"
        )

    response = {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Μετατροπή λεπτών σε δευτερόλεπτα
        "role": user.role,
    }

    return response
