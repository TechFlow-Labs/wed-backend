from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models import User, PartnerProfiles
from schemas.users import UserProfileResponseSchema, UserProfileUpdateSchema
from database.db import get_session
from utils.security import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserProfileResponseSchema, status_code=status.HTTP_200_OK)
def get_my_profile(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    
    try:
        # Run a single, flat query using an outer join
        profile_data = db.query(
            User.id,
            User.role,
            User.username,
            User.email,
            User.first_name,
            User.last_name,
            User.created_at,
            
            # Pull the partner fields (these will be NULL if the user is a COUPLE)
            PartnerProfiles.business_name,
            PartnerProfiles.category,
            PartnerProfiles.description
        ).outerjoin(
            PartnerProfiles, User.id == PartnerProfiles.user_id
        ).filter(
            User.id == current_user.id
        ).first()

        if not profile_data:
            raise HTTPException(status_code=404, detail="User profile not found")

        return profile_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.patch("/me", response_model=UserProfileResponseSchema, status_code=status.HTTP_200_OK)
def update_my_profile(profile_update: UserProfileUpdateSchema, db: Session = Depends(get_session),current_user: User = Depends(get_current_user)):

    # 1. Extract the data the frontend actually sent
    update_data = profile_update.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided to update.")

    # Define which fields belong to which table
    user_fields = {"first_name", "last_name"}
    partner_fields = {"business_name", "category", "description"}

    # 2. UPDATE THE USER TABLE
    # (Since we used `current_user = Depends(...)`, we already have the User object)
    for field in user_fields:
        if field in update_data:
            setattr(current_user, field, update_data[field])

    # 3. UPDATE THE PARTNER PROFILE TABLE (If applicable)
    provided_partner_fields = {k: v for k, v in update_data.items() if k in partner_fields}
    
    if provided_partner_fields:
        # Security check: Make sure Couples aren't trying to update business fields
        if current_user.role != "PARTNER":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Couples cannot update business profile fields."
            )
        
        # Fetch the partner's profile row
        db_profile = db.query(PartnerProfiles).filter(
            PartnerProfiles.user_id == current_user.id
        ).first()
        
        # Upsert Logic: If they are a partner but somehow don't have a profile row yet, create it!
        if not db_profile:
            db_profile = PartnerProfiles(user_id=current_user.id)
            db.add(db_profile)
            
        # Apply the updates to the profile
        for key, value in provided_partner_fields.items():
            setattr(db_profile, key, value)

    # 4. Save all changes
    db.commit()

    # 5. FETCH AND RETURN THE UPDATED FLAT RECORD
    updated_profile = db.query(
        User.id,
        User.role,
        User.username,
        User.email,
        User.first_name,
        User.last_name,
        User.created_at,
        PartnerProfiles.business_name,
        PartnerProfiles.category,
        PartnerProfiles.description
    ).outerjoin(
        PartnerProfiles, User.id == PartnerProfiles.user_id
    ).filter(
        User.id == current_user.id
    ).first()

    return updated_profile