import httpx
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ..config import settings
from ..templates_config import templates

router = APIRouter()


GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {})


@router.get("/auth/github")
def github_login(request: Request):
    import secrets

    state = secrets.token_urlsafe(16)
    request.session["oauth_state"] = state

    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": f"{settings.FRONTEND_URL}/auth/github/callback",
        "scope": "user:email",
        "state": state,
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(f"{GITHUB_AUTHORIZE_URL}?{query}")


@router.get("/auth/github/callback")
async def github_callback(request: Request, code: str, state: str):
    if state != request.session.get("oauth_state"):
        return RedirectResponse(url="/login?error=state_mismatch")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BACKEND_URL}/auth/github/callback",
            params={"code": code, "state": state, "code_verifier": ""},
        )

        if response.status_code != 200:
            return RedirectResponse(url="/login?error=auth_failed")

        data = response.json()

        redirect = RedirectResponse(url="/dashboard", status_code=302)
        redirect.set_cookie(
            "access_token", data["access_token"], httponly=True, samesite="lax"
        )
        redirect.set_cookie(
            "refresh_token", data["refresh_token"], httponly=True, samesite="lax"
        )
        return redirect


def logout(request: Request):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        import httpx
        with httpx.Client(base_url=settings.BACKEND_URL) as client:
            client.post("/auth/logout", json={"refresh_token": refresh_token})

    response = RedirectResponse(url="/login")
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response