# Special Partners Feature

## What was added
- New mock endpoint: `GET /public-api/special-partners/`
- Static response payload for frontend integration with no DB dependency.

## Endpoint contract
Response body:

```json
{
  "items": [
    {
      "id": "string",
      "name": "string",
      "category": "string",
      "city": "string",
      "shortDescription": "string",
      "badge": "string",
      "featuredImage": "string",
      "rating": 4.8
    }
  ]
}
```

## Local testing
- API run command (existing workflow), then:
  - `curl http://localhost:8060/public-api/special-partners/`
- Test command:
  - `cd src/app && pytest tests/test_special_partners.py`

## Preview URL pattern (PR deploy)
- `https://api-feature-special-partners-page.preview.techflowlabs.gr`

## Chore
- Added maintenance note for preview branch workflow consistency.
