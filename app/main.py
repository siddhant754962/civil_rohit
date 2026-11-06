from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from app.config import settings
from app.database import Base, engine
from app import models
from app.routes.public import router as public_router
from app.routes.admin import router as admin_router

app = FastAPI(title="DynamicBuilds", description="Engineering and architectural consultancy")
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key, same_site="lax", https_only=settings.secure_cookies, session_cookie="dynamicbuilds_session")
Path("static/uploads").mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")
app.include_router(public_router); app.include_router(admin_router)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health(): return {"status": "ok", "service": "DynamicBuilds"}

@app.exception_handler(404)
async def not_found(request: Request, exc):
    from fastapi.templating import Jinja2Templates
    return Jinja2Templates(directory="templates").TemplateResponse(request=request, name="404.html", status_code=404, context={"request": request})
