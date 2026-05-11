from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status
from schemas.websites import WeddingWebsiteGenerateRequest, WeddingWebsiteResponse, WebsiteScheduleItem, WebsiteFaqItem

router = APIRouter(prefix="/websites", tags=["Websites"])

WEBSITE_STORE: dict[str, WeddingWebsiteResponse] = {}


def _default_schedule() -> list[WebsiteScheduleItem]:
    return [
        WebsiteScheduleItem(time="16:30", title="Arrival", description="Welcome drinks"),
        WebsiteScheduleItem(time="18:00", title="Ceremony", description="Wedding ceremony starts"),
        WebsiteScheduleItem(time="20:00", title="Dinner", description="Seated dinner"),
        WebsiteScheduleItem(time="22:00", title="Party", description="Music and dancing"),
    ]


def _default_faq() -> list[WebsiteFaqItem]:
    return [
        WebsiteFaqItem(question="What should I wear?", answer="Semi-formal attire is perfect."),
        WebsiteFaqItem(question="Can I bring a plus-one?", answer="Please RSVP with your invitation details."),
        WebsiteFaqItem(question="Is parking available?", answer="Yes, on-site parking is available."),
    ]


@router.post("/generate", response_model=WeddingWebsiteResponse, status_code=status.HTTP_201_CREATED)
def generate_website(payload: WeddingWebsiteGenerateRequest):
    now = datetime.utcnow()
    existing = WEBSITE_STORE.get(payload.slug)

    schedule = payload.schedule if payload.schedule else _default_schedule()
    faq = payload.faq if payload.faq else _default_faq()

    item = WeddingWebsiteResponse(
        slug=payload.slug,
        couple_names=payload.couple_names,
        wedding_date=payload.wedding_date,
        venue=payload.venue,
        story=payload.story,
        schedule=schedule,
        faq=faq,
        rsvp_enabled=True,
        rsvp_deadline=payload.wedding_date - timedelta(days=21),
        public_path=f"/w/{payload.slug}",
        created_at=existing.created_at if existing else now,
        updated_at=now,
    )
    WEBSITE_STORE[payload.slug] = item
    return item


@router.get("/{slug}", response_model=WeddingWebsiteResponse)
def get_website(slug: str):
    item = WEBSITE_STORE.get(slug)
    if not item:
        raise HTTPException(status_code=404, detail="Wedding website not found")
    return item
