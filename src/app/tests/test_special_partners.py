from fastapi import FastAPI
from fastapi.testclient import TestClient

from routers.special_partners import router


def test_get_special_partners_contract():
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    response = client.get("/public-api/special-partners/")
    assert response.status_code == 200

    payload = response.json()
    assert "items" in payload
    assert isinstance(payload["items"], list)
    assert len(payload["items"]) > 0

    first = payload["items"][0]
    expected_keys = {
        "id",
        "name",
        "category",
        "city",
        "shortDescription",
        "badge",
        "featuredImage",
        "rating",
    }
    assert expected_keys.issubset(first.keys())
