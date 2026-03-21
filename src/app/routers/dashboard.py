from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_session
from schemas.dashboard import DashboardResponse
from utils.security import get_current_user
from models import User, Tasks, Gifts, Budget, Guests

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/", response_model=DashboardResponse)
def get_dashboard_data(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):

   # Επιστρέφει όλα τα δεδομένα του Dashboard για τον συνδεδεμένο χρήστη.

    # Φέρνουμε το Budget (Αν δεν υπάρχει, επιστρέφουμε 0)
    budget = db.query(Budget).filter(Budget.user_id == current_user.id).first()
    if not budget:
        from datetime import datetime
        budget = {
            "total_budget": 0.0,
            "updated_at": datetime.utcnow()
        }

    # Φέρνουμε τα Tasks, Gifts και Guests που ανήκουν στον χρήστη
    tasks = db.query(Tasks).filter(Tasks.user_id == current_user.id).all()
    gifts = db.query(Gifts).filter(Gifts.user_id == current_user.id).all()
    guests = db.query(Guests).filter(Guests.user_id == current_user.id).all()

    return {
        "user": current_user,
        "budget": budget,
        "tasks": tasks,
        "gifts": gifts,
        "guests": guests
    }
