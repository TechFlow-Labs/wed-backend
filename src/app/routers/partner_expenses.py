from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from decimal import Decimal
from models import PartnerExpenses, User
from schemas.partner_expenses import PartnerExpenseItemSchema, PartnerExpenseSummarySchema, PartnerExpenseCreateSchema, PartnerExpenseUpdateSchema
from database.db import get_session
from utils.security import get_current_user
from uuid import UUID


router = APIRouter(prefix="/partner_expenses", tags=["Partner Expenses"])
@router.get("/", response_model=PartnerExpenseSummarySchema, status_code=status.HTTP_200_OK)
def get_partner_expenses(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # 1. Security Check: Only Vendors have business expenses
    if current_user.role != "PARTNER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only registered partners can access business expenses."
        )

    # 2. Fetch all expenses for this specific partner
    # We sort by the date they made the purchase, newest first!
    expenses = db.query(PartnerExpenses).filter(
        PartnerExpenses.partner_id == current_user.id
    ).order_by(
        desc(PartnerExpenses.expense_date),
        desc(PartnerExpenses.created_at)
    ).all()

    # 3. Calculate the total sum
    # If they have no expenses, this safely defaults to 0.00
    total_sum = sum((expense.amount for expense in expenses), Decimal('0.00'))

    # 4. Return the exact structure our Summary schema expects
    return {
        "total_expenses": total_sum,
        "items": expenses
    }


@router.post("/", response_model=PartnerExpenseItemSchema, status_code=status.HTTP_201_CREATED)
def create_partner_expense(expense_data: PartnerExpenseCreateSchema, db: Session = Depends(get_session),current_user: User = Depends(get_current_user)):

    # 1. Security Check: Only Vendors can have business expenses
    if current_user.role != "PARTNER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only registered partners can create business expenses."
        )

    # 2. Extract the data into a dictionary
    new_expense_dict = expense_data.model_dump(exclude_unset=True)
    
    # 3. Create the Database Object securely
    new_expense = PartnerExpenses(
        partner_id=current_user.id,
        **new_expense_dict
    )

    # 4. Save to Database
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)

    return new_expense

@router.patch("/{expense_id}", response_model=PartnerExpenseItemSchema, status_code=status.HTTP_200_OK)
def update_partner_expense(expense_id: UUID, expense_update: PartnerExpenseUpdateSchema, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    # 1. Security Check: Block Couples from hitting this route
    if current_user.role != "PARTNER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only registered partners can edit business expenses."
        )

    # 2. Fetch the expense AND ensure the logged-in vendor owns it
    db_expense = db.query(PartnerExpenses).filter(
        PartnerExpenses.id == expense_id,
        PartnerExpenses.partner_id == current_user.id  # <-- The crucial ownership lock!
    ).first()

    if not db_expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Expense not found or you do not have permission to edit it."
        )

    # 3. Extract only the fields the frontend actually sent
    update_data = expense_update.model_dump(exclude_unset=True)

    # 4. Apply the updates to the SQLAlchemy model dynamically
    for key, value in update_data.items():
        setattr(db_expense, key, value)

    # 5. Save changes to the database
    db.commit()
    db.refresh(db_expense)

    return db_expense