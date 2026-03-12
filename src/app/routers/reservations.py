from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session, aliased
from database.db import get_session
from models import Reservations, User, PartnerProfiles
from schemas.reservations import ReservationsSchema, ReservationsUpdateSchema, ReservationsItemSchema
from utils.security import get_current_user
from typing import List
from uuid import UUID

router = APIRouter(prefix="/reservations", tags=["Reservations"])


@router.get("/pending", response_model = List[ReservationsSchema], status_code = status.HTTP_200_OK)
def get_pending_reservations(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):

    try:

        PartnerUser = aliased(User)
        CoupleUser = aliased(User)

        query = db.query(
                Reservations.id,
                Reservations.status,
                Reservations.event_date,
                Reservations.details,
                Reservations.budget_per_reservation,
                
                # Partner Info
                PartnerUser.id.label("partner_id"),
                PartnerProfiles.business_name,
                
                # Couple Info
                CoupleUser.id.label("couple_id"),
                CoupleUser.first_name.label("couple_first_name"),
                CoupleUser.last_name.label("couple_last_name"),
                
                # Guest Info (in case couple_id is null)
                Reservations.guest_first_name,
                Reservations.guest_last_name,
                Reservations.guest_email,
                Reservations.guest_phone
            ).join(
                PartnerUser, Reservations.partner_id == PartnerUser.id # 1st Join: Get Partner
            ).outerjoin(
                PartnerProfiles, PartnerUser.id == PartnerProfiles.user_id # 2nd Join: Get Business Name
            ).outerjoin(
                CoupleUser, Reservations.couple_id == CoupleUser.id # 3rd Join: Get Couple (Outer join because it might be a guest!)
            )
        
        if current_user.role == "COUPLE":
            reservations_pending = query.filter(Reservations.couple_id == current_user.id, Reservations.status == "PENDING").all()
        elif current_user.role == "PARTNER":
            reservations_pending = query.filter(Reservations.partner_id == current_user.id, Reservations.status == "PENDING").all()
        else:
            raise HTTPException(status_code=400, detail="User Role not recognized")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return reservations_pending


@router.patch("/{reservation_id}", response_model=ReservationsItemSchema, status_code = status.HTTP_200_OK)
def update_reservation(reservation_id: UUID, reservation_update: ReservationsUpdateSchema, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):

    db_reservation = db.query(Reservations).filter(Reservations.id == reservation_id, Reservations.partner_id == current_user.id).first()

    if not db_reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    update_data = reservation_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_reservation, key, value)

    db.commit()
    db.refresh(db_reservation)
    return db_reservation
