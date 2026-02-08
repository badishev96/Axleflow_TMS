from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.api.v1.router import router as v1_router

from app.api.v1.web_auth_pages import router as web_auth_router
from app.api.v1.app_shell import router as app_shell_router
from app.api.v1.loads_page import router as loads_page_router
from app.api.v1.load_analytics_page import router as load_analytics_router
from app.api.v1.expenses_page import router as expenses_page_router
from app.api.v1.expenses_ui_v2 import router as expenses_ui_v2_router
from app.api.v1.fuel_page import router as fuel_page_router
from app.api.v1.settlements_page import router as settlements_page_router
from app.api.v1.settlement_run_pages import router as settlement_run_pages_router
from app.api.v1.load_trend_v2 import router as load_trend_v2_router

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    same_site="lax",
    https_only=False
)

@app.get("/")
def root():
    return {"app": settings.APP_NAME, "status": "ok"}

# Website routes (no /api/v1 prefix)
app.include_router(web_auth_router)
app.include_router(app_shell_router)
app.include_router(loads_page_router)
app.include_router(load_analytics_router)   # ensure analytics page is authoritative
app.include_router(expenses_ui_v2_router)
app.include_router(expenses_page_router)
app.include_router(fuel_page_router)
app.include_router(settlements_page_router)
app.include_router(settlement_run_pages_router)
app.include_router(load_trend_v2_router)

# API routes
app.include_router(v1_router, prefix="/api/v1")




