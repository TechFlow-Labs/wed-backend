from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from database.db import get_session
from models import Guests, User, Reservations
from schemas.guests import GuestCreate, GuestDashboard
from utils.security import get_current_user
from typing import List
from uuid import UUID



router = APIRouter(prefix = "/guests", tags = ["Guests"])



# CREATE GUEST



@router.post("/", response_model=GuestDashboard, status_code=status.HTTP_201_CREATED)
def create_guest(guest_in: GuestCreate, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):

    # 1. Security Check: Only couples should be building guest lists
    if current_user.role != "COUPLE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only registered couples can manage a guest list."
        )

    # 2. Validation Check: If they link a reservation, make sure they actually own it!
    if guest_in.reservation_id:
        valid_reservation = db.query(Reservations).filter(
            Reservations.id == guest_in.reservation_id,
            Reservations.couple_id == current_user.id
        ).first()

        if not valid_reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Reservation not found or does not belong to you."
            )

    # 3. Create the Guest
    new_guest = Guests(
        user_id=current_user.id,
        reservation_id=guest_in.reservation_id,
        first_name=guest_in.first_name,
        last_name=guest_in.last_name,
        email=guest_in.email,
        phone_number=guest_in.phone_number
    )

    # 4. Save to Database
    db.add(new_guest)
    db.commit()
    db.refresh(new_guest)

    return new_guest




#GET ALL THE GUESTS (FROM THE CURRENT USER)


@router.get("/", response_model=List[GuestDashboard], status_code=status.HTTP_200_OK)
def get_all_guests(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):

    all_guests = db.query(Guests).filter(Guests.user_id == current_user.id).all()
    return all_guests



@router.delete("/{guest_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_guest(guest_id: UUID, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):

    db_guest = db.query(Guests).filter(Guests.id == guest_id, Guests.user_id == current_user.id).first()

    if not db_guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    # Διαγραφή από το session
    db.delete(db_guest)
    db.commit()
    return None
