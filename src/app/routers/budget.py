from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from database.db import get_session
from models import Budget, User
from schemas.budget import BudgetUpdate, BudgetDashboard
from utils.security import get_current_user
from typing import List


router = APIRouter(prefix="/budget", tags=["Budgets"])


@router.post("/", response_model=BudgetDashboard, status_code=status.HTTP_201_CREATED)
def set_or_update_budget(budget_in: BudgetUpdate, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):



    # Αναζήτηση το budget του current user
    db_budget = db.query(Budget).filter(Budget.user_id == current_user.id).first()


    # Αν το budget υπάρχει ήδη, κάνουμε update την τιμή
    if db_budget:

        db_budget.total_budget = budget_in.total_budget

    else:
        # Αν δεν υπάρχει, δημιουργούμε νέα εγγραφή


        db_budget = Budget(
            user_id=current_user.id,
            total_budget=budget_in.total_budget
        )
        db.add(db_budget)


    db.commit()
    db.refresh(db_budget)

    return db_budget


@router.get("/", response_model=BudgetDashboard)
def get_budget(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    budget = db.query(Budget).filter(Budget.user_id == current_user.id).first()
    if not budget:
        return {"total_budget": 0.0, "updated_at": current_user.created_at}
    return budget
