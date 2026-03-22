from fastapi import APIRouter, status, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session, aliased
from database.db import get_session
from collections import defaultdict
from models import Reservations, User, PartnerProfiles, Guests
from schemas.reservations import *
from utils.security import get_current_user
from typing import List
from uuid import UUID
from email_service.service import send_status_email

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
        
        return reservations_pending
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accepted", response_model = List[ReservationsSchema], status_code = status.HTTP_200_OK)
def get_accepted_reservations(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):

    try:

        # BASE QUERY
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
            reservations_accepted = query.filter(Reservations.couple_id == current_user.id, Reservations.status == "ACCEPTED").all()
        elif current_user.role == "PARTNER":
            reservations_accepted = query.filter(Reservations.partner_id == current_user.id, Reservations.status == "ACCEPTED").all()
        else:
            raise HTTPException(status_code=400, detail="User Role not recognized")
        
        if not reservations_accepted:
            return []

        # Extract all the reservation IDs we just found
        reservation_ids = [res.id for res in reservations_accepted]
        
        
        # BATCH FETCH GUESTS
        # Run ONE fast query to get all guests belonging to these reservations
        guests = db.query(Guests).filter(Guests.reservation_id.in_(reservation_ids)).all()

        # Group the guests by reservation_id for ultra-fast lookup
        guests_by_res = defaultdict(list)
        for guest in guests:
            guests_by_res[guest.reservation_id].append(guest)

        # MERGE DATA
        # Since SQLAlchemy rows are read-only tuples, we convert them to dictionaries 
        # so we can append the guests list before sending it to Pydantic
        final_results = []
        for res in reservations_accepted:
            # Convert SQLAlchemy Row to a standard Python dictionary
            res_dict = dict(res._mapping) 
            # Attach the guests (or an empty list if there are none)
            res_dict["guests"] = guests_by_res.get(res.id, [])
            final_results.append(res_dict)

        return final_results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{reservation_id}", response_model=ReservationsItemSchema, status_code = status.HTTP_200_OK)
def update_reservation(reservation_id: UUID, reservation_update: ReservationsUpdateSchema, background_tasks: BackgroundTasks, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):

    try:
        db_reservation = db.query(Reservations).filter(Reservations.id == reservation_id, Reservations.partner_id == current_user.id).first()

        if not db_reservation:
            raise HTTPException(status_code=404, detail="Reservation not found")

        update_data = reservation_update.model_dump(exclude_unset=True)

        new_status = update_data.get("status")
        status_changed = new_status in ["ACCEPTED", "REJECTED"] and db_reservation.status != new_status

        for key, value in update_data.items():
            setattr(db_reservation, key, value)

        db.commit()
        db.refresh(db_reservation)

        if status_changed:
            recipient_email = None
            
            # Figure out who to email
            if db_reservation.couple_id:
                couple_user = db.query(User).filter(User.id == db_reservation.couple_id).first()
                if couple_user:
                    recipient_email = couple_user.email
            elif db_reservation.guest_email:
                recipient_email = db_reservation.guest_email

            business_name = db.query(
                            PartnerProfiles.business_name
                        ).join(
                            User, PartnerProfiles.user_id == User.id
                        ).filter(User.id==current_user.id).first()[0]

            if recipient_email:
                # Format the date nicely, or provide a fallback string
                formatted_date = db_reservation.event_date.strftime("%B %d, %Y") if db_reservation.event_date else "the requested date"
                
                background_tasks.add_task(
                    send_status_email, 
                    to_email=recipient_email, 
                    vendor_name=business_name,
                    event_date=formatted_date,
                    new_status=new_status 
                )
                
            return db_reservation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/guest", response_model=ReservationsItemSchema, status_code=status.HTTP_201_CREATED)
def create_guest_request_for_reservation(reservation_data: ReservationPendingCreateGuestSchema, db: Session = Depends(get_session)):
    
    try:
        partner_exists = db.query(User).filter(
            User.id == reservation_data.partner_id, 
            User.role == 'PARTNER'
        ).first()
        
        if not partner_exists:
            raise HTTPException(status_code=404, detail="Vendor not found")

        new_reservation = Reservations(
            partner_id=reservation_data.partner_id,
            couple_id=None,
            guest_first_name=reservation_data.guest_first_name,
            guest_last_name=reservation_data.guest_last_name,
            guest_email=reservation_data.guest_email,
            guest_phone=reservation_data.guest_phone,
            event_date=reservation_data.event_date,
            details=reservation_data.details,
            budget_per_reservation=reservation_data.budget_per_reservation,
            status="PENDING"
        )

        db.add(new_reservation)
        db.commit()
        db.refresh(new_reservation)
        
        return new_reservation
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/pending", response_model=ReservationsItemSchema, status_code=status.HTTP_201_CREATED)
def create_request_for_reservation(reservation_data: ReservationPendingCreateSchema, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    
    try:

        if current_user.role != "COUPLE":
            raise HTTPException(status_code=403, detail="Role not authorized to create this type of reservation")

        partner_exists = db.query(User).filter(
            User.id == reservation_data.partner_id, 
            User.role == 'PARTNER'
        ).first()
        
        if not partner_exists:
            raise HTTPException(status_code=404, detail="Vendor not found")

        new_reservation = Reservations(
            partner_id=reservation_data.partner_id,
            couple_id=current_user.id,
            guest_first_name=None,
            guest_last_name=None,
            guest_email=None,
            guest_phone=None,
            event_date=reservation_data.event_date,
            details=reservation_data.details,
            budget_per_reservation=reservation_data.budget_per_reservation,
            status="PENDING"
        )

        db.add(new_reservation)
        db.commit()
        db.refresh(new_reservation)
        
        return new_reservation
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/accepted", response_model=ReservationsItemSchema, status_code=status.HTTP_201_CREATED)
def create_accepted_reservation(reservation_data: ReservationAcceptedCreateSchema, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    
    try:

        if current_user.role != "PARTNER":
            raise HTTPException(status_code=403, detail="Role not authorized to create this type of reservation")

        new_reservation = Reservations(
            partner_id=current_user.id,
            couple_id=None,
            guest_first_name=reservation_data.guest_first_name,
            guest_last_name=reservation_data.guest_last_name,
            guest_email=reservation_data.guest_email,
            guest_phone=reservation_data.guest_phone,
            event_date=reservation_data.event_date,
            details=reservation_data.details,
            budget_per_reservation=reservation_data.budget_per_reservation,
            status="ACCEPTED"
        )

        db.add(new_reservation)
        db.commit()
        db.refresh(new_reservation)
        
        return new_reservation
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))