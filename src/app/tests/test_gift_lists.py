from fastapi import FastAPI
from fastapi.testclient import TestClient

from routers.gift_lists import router


def test_get_gift_lists_contract():
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    response = client.get("/public-api/gift-lists/")
    assert response.status_code == 200

    payload = response.json()
    assert "items" in payload
    assert "total" in payload
    assert isinstance(payload["items"], list)
    assert isinstance(payload["total"], int)
    assert payload["total"] == len(payload["items"])

    first = payload["items"][0]
    expected_keys = {
        "id",
        "title",
        "description",
        "event_type",
        "gift_count",
    }
    assert expected_keys.issubset(first.keys())
