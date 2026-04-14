from fastapi import APIRouter, status, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from database.db import get_session
from models import User, PartnerProfiles
from schemas.vendors import VendorListResponse

router = APIRouter(prefix="/vendors", tags=["Vendors"])


@router.get("/", response_model=VendorListResponse,  status_code = status.HTTP_200_OK)
def get_public_vendors(
    # These parameters allow the frontend to filter and paginate via the URL
    # Example: /vendors?category=Catering&limit=20&skip=0
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_session)
):
    try:
        # Prepare the query for the vendors
        query = db.query(
            User.id.label("partner_id"),
            PartnerProfiles.business_name,
            PartnerProfiles.category,
            PartnerProfiles.description
        ).join(
            PartnerProfiles, User.id == PartnerProfiles.user_id
        ).filter(
            User.role == 'PARTNER'
        )


        # Get the total count of vendors before applying pagination
        total_count = query.count()

        # Execute the query With sorting and pagination)
        vendors = query.order_by(
            PartnerProfiles.business_name.asc(),  # Primary Sort: A to Z
            User.id.asc()                         # Tie-breaker: Unique ID
        ).offset(skip).limit(limit).all()

        # Return the results in the expected schema
        return {
            "total": total_count,
            "items": vendors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))