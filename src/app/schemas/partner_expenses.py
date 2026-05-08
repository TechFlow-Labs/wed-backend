from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime

class PartnerExpenseItemSchema(BaseModel):
    id: UUID
    title: str
    amount: Decimal
    category: Optional[str] = None
    expense_date: date
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PartnerExpenseSummarySchema(BaseModel):
    total_expenses: Decimal
    items: List[PartnerExpenseItemSchema]

class PartnerExpenseCreateSchema(BaseModel):
    title: str
    amount: Decimal
    category: Optional[str] = None
    expense_date: Optional[date] = None

class PartnerExpenseUpdateSchema(BaseModel):
    title: Optional[str] = None
    amount: Optional[Decimal] = None
    category: Optional[str] = None
    expense_date: Optional[date] = None