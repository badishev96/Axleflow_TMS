from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.load import Load

router = APIRouter()

def require_login(request: Request):
    return bool(request.session.get("user_id"))

@router.get("/app", response_class=HTMLResponse)
def app_home(request: Request, db: Session = Depends(get_db)):
    if not require_login(request):
        return RedirectResponse(url="/login", status_code=303)

    company_id = int(request.session.get("company_id"))

    loads_count = db.query(Load).filter(Load.company_id == company_id).count()

    return HTMLResponse(f"""
    <html>
    <head>
      <title>AxleFlow TMS</title>
      <style>
        body {{ font-family: Arial, sans-serif; margin:0; background:#0b0b0b; color:#111; }}
        .topbar {{ background:#111; color:#fff; padding:16px 24px; display:flex; justify-content:space-between; align-items:center; }}
        .topbar a {{ color:#bbb; text-decoration:none; margin-left:12px; }}
        .wrap {{ max-width:1100px; margin:0 auto; padding:24px; }}
        .card {{ background:#fff; border-radius:18px; padding:18px; box-shadow:0 10px 30px rgba(0,0,0,.18); }}
        .kpi {{ display:grid; grid-template-columns: repeat(3, 1fr); gap:12px; margin-top:12px; }}
        .k {{ border:1px solid #eee; border-radius:14px; padding:14px; }}
        .label {{ color:#666; font-size:12px; text-transform:uppercase; letter-spacing:.03em; }}
        .val {{ font-size:18px; font-weight:800; margin-top:8px; }}
        .btn {{ display:inline-block; padding:10px 14px; border-radius:12px; background:#111; color:#fff; text-decoration:none; font-weight:800; }}
      </style>
    </head>
    <body>
      <div class="topbar">
        <div style="font-weight:800;">AxleFlow TMS</div>
        <div>
          <a href="/app/loads">Loads</a>
          <a href="/app/expenses">Expenses</a>
          <a href="/app/settlements">Settlements</a>
          <a href="/docs">Swagger</a>
        </div>
      </div>

      <div class="wrap">
        <div class="card">
          <h2 style="margin:0;">Dashboard</h2>
          <div class="kpi">
            <div class="k"><div class="label">Company</div><div class="val">#{company_id}</div></div>
            <div class="k"><div class="label">Loads</div><div class="val">{loads_count}</div></div>
            <div class="k"><div class="label">Status</div><div class="val">Logged in</div></div>
          </div>
          <div style="margin-top:16px;">
            <a class="btn" href="/app/loads">Go to Loads</a>
          </div>
        </div>
      </div>
    </body>
    </html>
    """)
