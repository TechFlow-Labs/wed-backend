import os
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import requests
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field


class PreviewEvent(BaseModel):
    action: str = Field(pattern=r"^(deploy|teardown)$")
    preview_key: str
    trigger_repo: str
    pull_request_number: int
    branch: str
    base_branch: str
    sha: str
    actor: str
    event_action: str


@dataclass
class ServiceSpec:
    key: str
    app_name_prefix: str
    repo_url: str
    base_directory: str
    dockerfile_location: str
    port: str
    domain_prefix: str
    fallback_branch: str


class Settings:
    coolify_base_url = os.getenv("COOLIFY_BASE_URL", "").rstrip("/")
    coolify_api_token = os.getenv("COOLIFY_API_TOKEN", "")
    coolify_project_uuid = os.getenv("COOLIFY_PROJECT_UUID", "")
    coolify_environment_name = os.getenv("COOLIFY_ENVIRONMENT_NAME", "production")
    coolify_destination_uuid = os.getenv("COOLIFY_DESTINATION_UUID", "")
    coolify_server_uuid = os.getenv("COOLIFY_SERVER_UUID", "")
    preview_base_domain = os.getenv("PREVIEW_BASE_DOMAIN", "preview.techflowlabs.gr")
    shared_secret = os.getenv("PREVIEW_ORCHESTRATOR_TOKEN", "")
    request_timeout_seconds = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "25"))
    github_token = os.getenv("GITHUB_TOKEN", "")

    backend_repo_url = os.getenv("BACKEND_REPO_URL", "https://github.com/TechFlow-Labs/wed-backend.git")
    main_repo_url = os.getenv("MAIN_REPO_URL", "https://github.com/TechFlow-Labs/wed-main-mvp.git")
    ssr_repo_url = os.getenv("SSR_REPO_URL", "https://github.com/TechFlow-Labs/wed-ssr-mvp.git")

    backend_fallback_branch = os.getenv("BACKEND_FALLBACK_BRANCH", "main")
    main_fallback_branch = os.getenv("MAIN_FALLBACK_BRANCH", "main")
    ssr_fallback_branch = os.getenv("SSR_FALLBACK_BRANCH", "main")


SETTINGS = Settings()
app = FastAPI(title="Coolify Preview Orchestrator", version="0.1.0")

BACKEND_REQUIRED_ENV_KEYS = [
    "DB_USER",
    "DB_PASSWORD",
    "DB_HOST",
    "DB_PORT",
    "DB_DATABASE",
    "JWT_SECRET_KEY",
    "JWT_REFRESH_SECRET_KEY",
]


def _sanitize_preview_key(raw: str) -> str:
    key = re.sub(r"[^a-z0-9]+", "-", raw.strip().lower())
    key = re.sub(r"^-+", "", key)
    key = re.sub(r"-+$", "", key)
    key = re.sub(r"-+", "-", key)
    return key or "preview"


def _headers() -> Dict[str, str]:
    if not SETTINGS.coolify_api_token:
        raise RuntimeError("COOLIFY_API_TOKEN is required")
    return {
        "Authorization": f"Bearer {SETTINGS.coolify_api_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _coolify_request(method: str, path: str, json: Optional[dict] = None) -> dict:
    if not SETTINGS.coolify_base_url:
        raise RuntimeError("COOLIFY_BASE_URL is required")
    url = f"{SETTINGS.coolify_base_url}{path}"
    response = requests.request(
        method,
        url,
        headers=_headers(),
        json=json,
        timeout=SETTINGS.request_timeout_seconds,
    )
    if response.status_code >= 400:
        detail = response.text
        raise RuntimeError(f"Coolify API {method} {path} failed ({response.status_code}): {detail}")
    if not response.text:
        return {}
    try:
        return response.json()
    except ValueError:
        return {"raw": response.text}


def _list_applications() -> List[dict]:
    data = _coolify_request("GET", "/api/v1/applications")
    if isinstance(data, list):
        return data
    return []


def _application_by_name(name: str) -> Optional[dict]:
    for app_obj in _list_applications():
        if app_obj.get("name") == name:
            return app_obj
    return None


def _github_branch_exists(repo_url: str, branch: str) -> bool:
    # Supports standard https://github.com/owner/repo(.git)
    match = re.match(r"https://github.com/([^/]+)/([^/.]+)(?:\.git)?$", repo_url)
    if not match:
        return True

    owner, repo = match.group(1), match.group(2)
    headers = {"Accept": "application/vnd.github+json"}
    if SETTINGS.github_token:
        headers["Authorization"] = f"Bearer {SETTINGS.github_token}"

    url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}"
    try:
        resp = requests.get(url, headers=headers, timeout=SETTINGS.request_timeout_seconds)
        return resp.status_code == 200
    except requests.RequestException:
        # Don't hard fail if GitHub lookup has transient issues.
        return True


def _resolve_branch(repo_url: str, preferred: str, fallback: str) -> Tuple[str, bool]:
    if _github_branch_exists(repo_url, preferred):
        return preferred, False
    return fallback, True


def _build_service_specs(preview_key: str) -> List[ServiceSpec]:
    return [
        ServiceSpec(
            key="backend",
            app_name_prefix="wed-preview-backend",
            repo_url=SETTINGS.backend_repo_url,
            base_directory="/",
            dockerfile_location="/Dockerfile",
            port="8000",
            domain_prefix="api",
            fallback_branch=SETTINGS.backend_fallback_branch,
        ),
        ServiceSpec(
            key="main",
            app_name_prefix="wed-preview-main",
            repo_url=SETTINGS.main_repo_url,
            base_directory="/",
            dockerfile_location="/Dockerfile",
            port="3000",
            domain_prefix="main",
            fallback_branch=SETTINGS.main_fallback_branch,
        ),
        ServiceSpec(
            key="ssr",
            app_name_prefix="wed-preview-ssr",
            repo_url=SETTINGS.ssr_repo_url,
            base_directory="/",
            dockerfile_location="/Dockerfile",
            port="3005",
            domain_prefix="ssr",
            fallback_branch=SETTINGS.ssr_fallback_branch,
        ),
    ]


def _app_name(spec: ServiceSpec, preview_key: str) -> str:
    return f"{spec.app_name_prefix}-{preview_key}"


def _domain(spec: ServiceSpec, preview_key: str) -> str:
    return f"{spec.domain_prefix}-{preview_key}.{SETTINGS.preview_base_domain}"


def _domain_url(spec: ServiceSpec, preview_key: str) -> str:
    return f"https://{_domain(spec, preview_key)}"


def _create_or_update_application(spec: ServiceSpec, preview_key: str, branch: str, sha: str) -> Tuple[str, bool]:
    if not SETTINGS.coolify_project_uuid or not SETTINGS.coolify_destination_uuid:
        raise RuntimeError("COOLIFY_PROJECT_UUID and COOLIFY_DESTINATION_UUID are required")

    name = _app_name(spec, preview_key)
    domain = _domain(spec, preview_key)
    app_obj = _application_by_name(name)

    create_payload = {
        "project_uuid": SETTINGS.coolify_project_uuid,
        "environment_name": SETTINGS.coolify_environment_name,
        "destination_uuid": SETTINGS.coolify_destination_uuid,
        "server_uuid": SETTINGS.coolify_server_uuid or SETTINGS.coolify_destination_uuid,
        "git_repository": spec.repo_url,
        "git_branch": branch,
        "build_pack": "dockerfile",
        "name": name,
        "domains": _domain_url(spec, preview_key),
        "ports_exposes": spec.port,
        "base_directory": spec.base_directory,
        "dockerfile_location": spec.dockerfile_location,
        "is_force_https_enabled": False,
        "force_domain_override": True,
        "git_commit_sha": sha,
        "instant_deploy": False,
    }

    update_payload = {
        "git_repository": spec.repo_url,
        "git_branch": branch,
        "build_pack": "dockerfile",
        "name": name,
        "domains": _domain_url(spec, preview_key),
        "ports_exposes": spec.port,
        "base_directory": spec.base_directory,
        "dockerfile_location": spec.dockerfile_location,
        "is_force_https_enabled": False,
        "force_domain_override": True,
        "git_commit_sha": sha,
        "instant_deploy": False,
    }

    if app_obj:
        uuid = app_obj["uuid"]
        _coolify_request("PATCH", f"/api/v1/applications/{uuid}", json=update_payload)
        return uuid, False

    created = _coolify_request("POST", "/api/v1/applications/public", json=create_payload)
    uuid = created.get("uuid")
    if not uuid:
        raise RuntimeError(f"Coolify did not return application uuid for {name}")
    return uuid, True


def _sync_env(uuid: str, env_map: Dict[str, str]) -> None:
    for key, value in env_map.items():
        payload = {
            "key": key,
            "value": value,
            "is_preview": False,
            "is_literal": True,
            "is_multiline": False,
            "is_shown_once": False,
        }
        try:
            _coolify_request("PATCH", f"/api/v1/applications/{uuid}/envs", json=payload)
        except RuntimeError as err:
            # Coolify returns 404 when PATCH targets a non-existing env key.
            # Fall back to create operation.
            if "Environment variable not found" not in str(err):
                raise
            _coolify_request("POST", f"/api/v1/applications/{uuid}/envs", json=payload)


def _trigger_deploy(uuid: str) -> dict:
    return _coolify_request("GET", f"/api/v1/applications/{uuid}/start?force=false&instant_deploy=false")


def _delete_application(uuid: str) -> None:
    _coolify_request(
        "DELETE",
        f"/api/v1/applications/{uuid}?delete_configurations=true&delete_volumes=true&docker_cleanup=true&delete_connected_networks=true",
    )


def _teardown(preview_key: str) -> dict:
    deleted: List[str] = []
    missing: List[str] = []

    for spec in _build_service_specs(preview_key):
        name = _app_name(spec, preview_key)
        app_obj = _application_by_name(name)
        if not app_obj:
            missing.append(name)
            continue
        _delete_application(app_obj["uuid"])
        deleted.append(name)

    return {"deleted": deleted, "missing": missing}


def _deploy(event: PreviewEvent, preview_key: str) -> dict:
    api_domain = _domain(ServiceSpec("backend", "", "", "", "", "", "api", ""), preview_key)

    results = []
    fallback_repos = []

    for spec in _build_service_specs(preview_key):
        chosen_branch, used_fallback = _resolve_branch(spec.repo_url, event.branch, spec.fallback_branch)
        if used_fallback:
            fallback_repos.append({"service": spec.key, "branch": chosen_branch})

        app_uuid, created = _create_or_update_application(spec, preview_key, chosen_branch, event.sha)

        env_map: Dict[str, str] = {}
        if spec.key == "backend":
            env_map.update(_backend_env_map(preview_key))
        elif spec.key == "main":
            env_map["EXPO_PUBLIC_API_URL"] = f"https://{api_domain}"
        elif spec.key == "ssr":
            env_map["NEXT_PUBLIC_API_URL"] = f"https://{api_domain}"
            env_map["API_INTERNAL_URL"] = f"http://wed-preview-backend-{preview_key}:8000"

        if env_map:
            _sync_env(app_uuid, env_map)

        deploy_resp = _trigger_deploy(app_uuid)
        results.append(
            {
                "service": spec.key,
                "app_uuid": app_uuid,
                "created": created,
                "domain": f"https://{_domain(spec, preview_key)}",
                "branch": chosen_branch,
                "deployment": deploy_resp,
            }
        )

    return {
        "preview_key": preview_key,
        "services": results,
        "fallback_repos": fallback_repos,
    }


def _backend_env_map(preview_key: str) -> Dict[str, str]:
    env_map: Dict[str, str] = {}

    # Required backend envs are sourced from ORCH_BACKEND_<KEY> on orchestrator.
    missing: List[str] = []
    for key in BACKEND_REQUIRED_ENV_KEYS:
        source_key = f"ORCH_BACKEND_{key}"
        value = os.getenv(source_key, "").strip()
        if not value:
            missing.append(source_key)
            continue
        env_map[key] = value

    if missing:
        raise RuntimeError(
            "Missing required orchestrator env vars for backend preview app: "
            + ", ".join(missing)
        )

    # Optional backend settings
    optional_pairs = {
        "APP_MODULE": os.getenv("ORCH_BACKEND_APP_MODULE", ""),
        "ACCESS_TOKEN_EXPIRE_MINUTES": os.getenv("ORCH_BACKEND_ACCESS_TOKEN_EXPIRE_MINUTES", ""),
        "REFRESH_TOKEN_EXPIRE_MINUTES": os.getenv("ORCH_BACKEND_REFRESH_TOKEN_EXPIRE_MINUTES", ""),
        "ALGORITHM": os.getenv("ORCH_BACKEND_ALGORITHM", ""),
        "MAIL_USERNAME": os.getenv("ORCH_BACKEND_MAIL_USERNAME", ""),
        "MAIL_PASSWORD": os.getenv("ORCH_BACKEND_MAIL_PASSWORD", ""),
        "MAIL_FROM": os.getenv("ORCH_BACKEND_MAIL_FROM", ""),
        "MAIL_PORT": os.getenv("ORCH_BACKEND_MAIL_PORT", ""),
        "MAIL_SERVER": os.getenv("ORCH_BACKEND_MAIL_SERVER", ""),
        "APP_DOMAIN": f"api-{preview_key}.{SETTINGS.preview_base_domain}",
    }
    for key, value in optional_pairs.items():
        value = value.strip()
        if value:
            env_map[key] = value

    # Ensure API binds correctly in container runtime.
    env_map["API_HOST"] = "0.0.0.0"
    env_map["API_PORT"] = "8000"

    return env_map


def _authorize(authorization: Optional[str]) -> None:
    if not SETTINGS.shared_secret:
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    if token != SETTINGS.shared_secret:
        raise HTTPException(status_code=401, detail="Invalid bearer token")


@app.get("/healthz")
def healthz() -> dict:
    return {"ok": True}


@app.post("/preview-events")
def preview_events(payload: PreviewEvent, authorization: Optional[str] = Header(default=None)) -> dict:
    _authorize(authorization)

    preview_key = _sanitize_preview_key(payload.preview_key)

    try:
        if payload.action == "teardown":
            result = _teardown(preview_key)
            return {"ok": True, "action": "teardown", "preview_key": preview_key, **result}

        # On PR synchronize (new commit pushed), rebuild from a clean slate:
        # delete existing preview apps for this preview key, then recreate/redeploy.
        if payload.event_action == "synchronize":
            teardown_result = _teardown(preview_key)
            deploy_result = _deploy(payload, preview_key)
            return {
                "ok": True,
                "action": "deploy",
                "mode": "teardown_then_deploy",
                "teardown": teardown_result,
                **deploy_result,
            }

        result = _deploy(payload, preview_key)
        return {"ok": True, "action": "deploy", **result}
    except RuntimeError as err:
        raise HTTPException(status_code=500, detail=str(err)) from err
