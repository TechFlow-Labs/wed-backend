# Coolify Preview Orchestrator Contract

This repo notifies a shared preview orchestrator on every PR open/update/reopen/close.

## Workflow

- File: `.github/workflows/coolify-preview-orchestrator.yml`
- Trigger: `pull_request` (`opened`, `synchronize`, `reopened`, `closed`)
- Action mapping:
  - `opened|synchronize|reopened` -> `deploy`
  - `closed` -> `teardown`

## Preview Key Convention

The workflow derives `preview_key` from PR head branch:

1. lowercases branch name
2. replaces non `[a-z0-9]` characters with `-`
3. trims leading/trailing `-`
4. collapses repeated `-`

Fallback when empty: `pr-<number>`

Use the same branch name across `wed-backend`, `wed-main-mvp`, and `wed-ssr-mvp` to target the same unified preview environment.

## Required Secrets

- `PREVIEW_ORCHESTRATOR_URL`: HTTP endpoint that handles preview deploy/teardown

## Optional Secrets

- `PREVIEW_ORCHESTRATOR_TOKEN`: Bearer token sent as `Authorization: Bearer <token>`

## Payload Sent

```json
{
  "action": "deploy | teardown",
  "preview_key": "feature-coolify-unified-pr-previews",
  "trigger_repo": "TechFlow-Labs/<repo>",
  "pull_request_number": 123,
  "branch": "feature/coolify-unified-pr-previews",
  "base_branch": "main",
  "sha": "<head_sha>",
  "actor": "<github_user>",
  "event_action": "opened | synchronize | reopened | closed"
}
```
