from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from uuid import UUID


class BudgetDashboard(BaseModel):
    total_budget: float
    updated_at: datetime

    class Config:
        from_attributes = True


class BudgetUpdate(BaseModel):
    total_budget: float


class VendorAllocation(BaseModel):
    reservation_id: UUID
    partner_id: UUID
    business_name: str
    category: Optional[str] = None
    amount: float
    event_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class BudgetSummary(BaseModel):
    total_budget: float
    spent_budget: float
    remaining_budget: float
    vendor_allocations: List[VendorAllocation]
