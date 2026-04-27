import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ..dependencies import get_portal_context
from ..templates_config import templates

router = APIRouter()


def rewrite_links(links: dict) -> dict:
    result = {}
    for key, url in links.items():
        if url:
            # replace /api/profiles with /profiles
            result[key] = url.replace("/api/profiles", "/profiles")
        else:
            result[key] = None
    return result


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, ctx: Annotated[dict, Depends(get_portal_context)]):
    client = ctx["client"]

    response = client.get("/api/profiles", params={"limit": 1})
    total = response.json().get("total", 0)

    male = (
        client.get("/api/profiles", params={"gender": "male", "limit": 1})
        .json()
        .get("total", 0)
    )
    female = (
        client.get("/api/profiles", params={"gender": "female", "limit": 1})
        .json()
        .get("total", 0)
    )

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "user": ctx["user"],
            "metrics": {"total": total, "male": male, "female": female},
        },
    )


@router.get("/profiles", response_class=HTMLResponse)
def list_profiles(
    request: Request,
    ctx: Annotated[dict, Depends(get_portal_context)],
    gender: str = None,
    country_id: str = None,
    age_group: str = None,
    page: int = 1,
    limit: int = 10,
):
    client = ctx["client"]
    params = {
        k: v
        for k, v in {
            "gender": gender,
            "country_id": country_id,
            "age_group": age_group,
            "page": page,
            "limit": limit,
        }.items()
        if v is not None and v != ""
    }

    body = client.get("/api/profiles", params=params).json()

    return templates.TemplateResponse(
        request,
        "profiles/list.html",
        {
            "user": ctx["user"],
            "profiles": body.get("data", []),
            "page": body.get("page", 1),
            "total_pages": body.get("total_pages", 1),
            "total": body.get("total", 0),
            "links": rewrite_links(body.get("links", {})),
            "filters": {
                "gender": gender,
                "country_id": country_id,
                "age_group": age_group,
            },
        },
    )


@router.get("/profiles/{id}", response_class=HTMLResponse)
def profile_detail(
    id: str, request: Request, ctx: Annotated[dict, Depends(get_portal_context)]
):
    client = ctx["client"]
    profile = client.get(f"/api/profiles/{id}").json().get("data", {})
    csrf_token = secrets.token_urlsafe(16)
    request.session["csrf_token"] = csrf_token

    return templates.TemplateResponse(
        request,
        "profiles/detail.html",
        {
            "user": ctx["user"],
            "profile": profile,
            "csrf_token": csrf_token,
        },
    )


@router.post("/profiles/{id}/delete")
async def delete_profile(
    id: str, request: Request, ctx: dict = Depends(get_portal_context)
):
    form = await request.form()
    if form.get("csrf_token") != request.session.get("csrf_token"):
        return RedirectResponse(url=f"/profiles/{id}?error=csrf", status_code=302)

    ctx["client"].delete(f"/api/profiles/{id}")
    return RedirectResponse(url="/profiles", status_code=302)


@router.get("/search", response_class=HTMLResponse)
def search(request: Request, ctx: dict = Depends(get_portal_context), q: str = None):
    client = ctx["client"]
    profiles = []

    if q and q.strip():
        body = client.get("/api/profiles/search", params={"q": q}).json()
        profiles = body.get("data", [])

    return templates.TemplateResponse(
        request,
        "profiles/search.html",
        {
            "user": ctx["user"],
            "profiles": profiles,
            "query": q if q else "",
        },
    )


@router.get("/account", response_class=HTMLResponse)
def account(request: Request, ctx: dict = Depends(get_portal_context)):
    return templates.TemplateResponse(
        request,
        "account.html",
        {
            "user": ctx["user"],
        },
    )
