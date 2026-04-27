from fastapi import HTTPException, Request, status
from fastapi.responses import RedirectResponse

from .http import BackendClient


def get_backend_client(request: Request) -> BackendClient | RedirectResponse:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/login"},
        )
    return BackendClient(token)


def get_portal_context(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/login"},
        )

    client = BackendClient(token)

    response = client.get("/auth/me")
    if response.status_code == 401:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/login"},
        )

    user = response.json()
    return {"client": client, "user": user}
