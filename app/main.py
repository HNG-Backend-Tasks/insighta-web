from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from .config import settings
from .routes import auth, profiles

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if (
        exc.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        and "Location" in exc.headers
    ):
        return RedirectResponse(url=exc.headers["Location"])
    return JSONResponse(
        status_code=exc.status_code, content={"status": "error", "message": exc.detail}
    )


app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="app/templates")

app.include_router(auth.router)
app.include_router(profiles.router)


@app.get("/")
def root():
    return RedirectResponse(url="/dashboard")
