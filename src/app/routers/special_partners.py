from fastapi import APIRouter, status
from schemas.special_partners import SpecialPartnersResponse

router = APIRouter(prefix="/public-api/special-partners", tags=["Special Partners"])

MOCK_SPECIAL_PARTNERS = [
    {
        "id": "sp-001",
        "name": "Golden Olive Events",
        "category": "Venue",
        "city": "Athens",
        "shortDescription": "Industrial-chic venue with indoor/outdoor wedding setups.",
        "badge": "Top Rated",
        "featuredImage": "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=1200&q=80",
        "rating": 4.9,
    },
    {
        "id": "sp-002",
        "name": "Velvet Bloom Studio",
        "category": "Florist",
        "city": "Thessaloniki",
        "shortDescription": "Custom floral design focused on elegant seasonal palettes.",
        "badge": "Editor's Pick",
        "featuredImage": "https://images.unsplash.com/photo-1472141521881-95d0e87e2e39?w=1200&q=80",
        "rating": 4.8,
    },
    {
        "id": "sp-003",
        "name": "Aegean Film Collective",
        "category": "Photography",
        "city": "Heraklion",
        "shortDescription": "Documentary-style photo and film coverage for destination weddings.",
        "badge": "Featured",
        "featuredImage": "https://images.unsplash.com/photo-1511285560929-80b456fea0bc?w=1200&q=80",
        "rating": 4.7,
    },
]


@router.get("", response_model=SpecialPartnersResponse, status_code=status.HTTP_200_OK)
@router.get("/", response_model=SpecialPartnersResponse, status_code=status.HTTP_200_OK)
def get_special_partners():
    return {"items": MOCK_SPECIAL_PARTNERS}
