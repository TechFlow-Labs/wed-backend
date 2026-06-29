from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from database.db import get_session
from models import Budget, User
from models.reservations import Reservations
from models.partner_profiles import PartnerProfiles
from schemas.budget import BudgetUpdate, BudgetDashboard, BudgetSummary, VendorAllocation
from utils.security import get_current_user

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


@router.get("/summary", response_model=BudgetSummary)
def get_budget_summary(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    budget = db.query(Budget).filter(Budget.user_id == current_user.id).first()
    total_budget = float(budget.total_budget) if budget else 0.0

    rows = (
        db.query(Reservations, PartnerProfiles)
        .join(PartnerProfiles, Reservations.partner_id == PartnerProfiles.user_id)
        .filter(
            Reservations.couple_id == current_user.id,
            Reservations.status == "ACCEPTED",
            Reservations.budget_per_reservation.isnot(None),
        )
        .all()
    )

    allocations = [
        VendorAllocation(
            reservation_id=reservation.id,
            partner_id=reservation.partner_id,
            business_name=partner.business_name,
            category=partner.category,
            amount=float(reservation.budget_per_reservation),
            event_date=reservation.event_date,
        )
        for reservation, partner in rows
    ]

    spent_budget = sum(a.amount for a in allocations)

    return BudgetSummary(
        total_budget=total_budget,
        spent_budget=spent_budget,
        remaining_budget=total_budget - spent_budget,
        vendor_allocations=allocations,
    )


@router.get("/", response_model=BudgetDashboard)
def get_budget(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    budget = db.query(Budget).filter(Budget.user_id == current_user.id).first()
    if not budget:
        return {"total_budget": 0.0, "updated_at": current_user.created_at}
    return budget
