from fastapi import APIRouter, status
from schemas.gift_lists import GiftListsResponse

router = APIRouter(prefix="/public-api/gift-lists", tags=["Gift Lists"])

MOCK_GIFT_LISTS = [
    {
        "id": "gl-001",
        "title": "Μοντέρνο Σπίτι",
        "description": "Χρήσιμα δώρα για νέο σπίτι με minimal αισθητική.",
        "event_type": "wedding",
        "gift_count": 18,
    },
    {
        "id": "gl-002",
        "title": "Weekend Getaway",
        "description": "Εμπειρίες και travel essentials για μήνα του μέλιτος.",
        "event_type": "wedding",
        "gift_count": 12,
    },
    {
        "id": "gl-003",
        "title": "Νέο Ξεκίνημα",
        "description": "Επιλεγμένα δώρα για βάπτιση και οικογενειακές ανάγκες.",
        "event_type": "baptism",
        "gift_count": 10,
    },
]


@router.get("/", response_model=GiftListsResponse, status_code=status.HTTP_200_OK)
def get_gift_lists():
    return {"items": MOCK_GIFT_LISTS, "total": len(MOCK_GIFT_LISTS)}
