from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.db import get_session
from uuid import UUID
from models import Notes, Reservations, User
from schemas.notes import NoteCreateSchema, NoteResponseSchema, NoteUpdateSchema
from utils.security import get_current_user
from typing import List

router = APIRouter(prefix="/notes", tags=["Notes"])


@router.post("/", response_model=NoteResponseSchema, status_code=status.HTTP_201_CREATED)
def create_note(note_data: NoteCreateSchema,db: Session = Depends(get_session),current_user: User = Depends(get_current_user)):
    try:
        # Validation Check: If they are linking a reservation, do they have access to it?
        if note_data.reservation_id:
            valid_reservation = db.query(Reservations).filter(
                Reservations.id == note_data.reservation_id
            ).first()

            if not valid_reservation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Reservation not found."
                )
                
            # Security: The user must be either the Couple OR the Partner on this specific reservation
            if current_user.id not in [valid_reservation.couple_id, valid_reservation.partner_id]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, 
                    detail="You do not have permission to add notes to this reservation."
                )

        # Create the Note
        new_note = Notes(
            author_id=current_user.id,
            reservation_id=note_data.reservation_id,
            content=note_data.content
        )

        # 3. Save to Database
        db.add(new_note)
        db.commit()
        db.refresh(new_note)

        return new_note
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{note_id}", response_model=NoteResponseSchema, status_code=status.HTTP_200_OK)
def update_note(note_id: UUID,note_update: NoteUpdateSchema,db: Session = Depends(get_session),current_user: User = Depends(get_current_user)):
    
    # 1. Fetch the note AND ensure the logged-in user is the author
    db_note = db.query(Notes).filter(
        Notes.id == note_id,
        Notes.author_id == current_user.id
    ).first()

    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Note not found or you don't have permission to edit it."
        )


    # 2. Security Check: If they are trying to link a NEW reservation_id
    if note_update.reservation_id:
        valid_reservation = db.query(Reservations).filter(
            Reservations.id == note_update.reservation_id
        ).first()
        
        if not valid_reservation:
            raise HTTPException(status_code=404, detail="Target reservation not found.")
            
        # Ensure they have access to this new reservation
        if current_user.id not in [valid_reservation.couple_id, valid_reservation.partner_id]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="You do not have permission to link a note to this reservation."
            )

    # 3. Extract the data the frontend actually sent
    update_data = note_update.model_dump(exclude_unset=True)

    # 4. Apply the updates to the SQLAlchemy model
    for key, value in update_data.items():
        setattr(db_note, key, value)

    # 5. Save changes
    db.commit()
    db.refresh(db_note)

    return db_note

@router.get("/", response_model=List[NoteResponseSchema], status_code=status.HTTP_200_OK)
def get_global_notes(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    
    # Query the database for this specific user's notes
    global_notes = db.query(Notes).filter(
        Notes.author_id == current_user.id,     # 1. Must belong to the logged-in user
        Notes.reservation_id.is_(None)          # 2. MUST NOT have a reservation attached
    ).order_by(
        Notes.updated_at.desc()                 # 3. Sort by newest/most recently updated first!
    ).all()

    return global_notes