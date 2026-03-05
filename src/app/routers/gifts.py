from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from database.db import get_session
from models import Gifts, User
from schemas.schemas import GiftCreate, GiftDashboard
from utils.security import get_current_user
from typing import List
from uuid import UUID




router = APIRouter(prefix="/gifts", tags=["Gifts"])



# CREATE GIFT


@router.post("/", response_model = GiftDashboard, status_code = status.HTTP_201_CREATED)
def create_gift(gift_in: GiftCreate, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    new_gift = Gifts(
        user_id = current_user.id,
        item_name = gift_in.item_name,
        category = gift_in.category,
        short_description = gift_in.short_description,
        long_description  = gift_in.long_description,
        main_image_url = gift_in.main_image_url,
        gallery_image_urls = gift_in.gallery_image_urls


    )
    db.add(new_gift)
    db.commit()
    db.refresh(new_gift)

    return new_gift



# GET ALL GIFTS FROM THE USER



@router.get("/", response_model = List[GiftDashboard], status_code = status.HTTP_200_OK)
def get_all_gifts(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    all_gifts = db.query(Gifts).filter(Gifts.user_id == current_user.id).all()
    return all_gifts




@router.delete("/{gift_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_gift(gift_id: UUID, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):

    db_gift = db.query(Gifts).filter(Gifts.id == gift_id, Gifts.user_id == current_user.id).first()

    if not db_gift:
        raise HTTPException(status_code=404, detail="Gift not found")
    #  Διαγραφή από το session
    db.delete(db_gift)
    db.commit()
    return None
