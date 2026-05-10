from pydantic import BaseModel
from typing import List


class GiftListItem(BaseModel):
    id: str
    title: str
    description: str
    event_type: str
    gift_count: int


class GiftListsResponse(BaseModel):
    items: List[GiftListItem]
    total: int
