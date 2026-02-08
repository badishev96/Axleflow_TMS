from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.settlement_run import SettlementRun
from app.models.settlement_run_load import SettlementRunLoad

router = APIRouter()

def require_login(request: Request):
    return bool(request.session.get("user_id"))

def money(x):
    return "$" + format(float(x), ",.2f")

@router.get("/app/settlements/print/{run_id}", response_class=HTMLResponse)
def print_run(run_id: int, request: Request, db: Session = Depends(get_db)):
    if not require_login(request):
        return RedirectResponse(url="/login", status_code=303)

    company_id = int(request.session.get("company_id"))
    run = db.query(SettlementRun).filter(
        SettlementRun.company_id == company_id,
        SettlementRun.id == run_id
    ).first()

    if not run:
        return HTMLResponse("<p>Run not found</p>", status_code=404)

    rows = db.query(SettlementRunLoad).filter(
        SettlementRunLoad.company_id == company_id,
        SettlementRunLoad.settlement_run_id == run.id
    ).all()

    row_html = ""
    for r in rows:
        row_html += f"<tr><td>{r.load_id}</td><td style='text-align:right;'>{money(r.load_pay)}</td></tr>"

    return HTMLResponse(f"""
    <html>
    <head>
      <title>Settlement Run #{run.id}</title>
      <style>
        body {{ font-family: Arial, sans-serif; margin:40px; }}
        table {{ width:520px; border-collapse:collapse; }}
        td, th {{ padding:10px; border-bottom:1px solid #eee; }}
        th {{ text-align:left; }}
        .btn {{ display:inline-block; padding:10px 14px; border-radius:10px; background:#111; color:#fff; text-decoration:none; margin-bottom:16px; }}
        @media print {{ .btn {{ display:none; }} }}
      </style>
    </head>
    <body>
      <a class="btn" href="#" onclick="window.print();return false;">Print / Download (PDF)</a>

      <h2>Settlement Run #{run.id}</h2>
      <p><b>Type:</b> {run.person_type}</p>
      <p><b>Person ID:</b> {run.person_id}</p>
      <p><b>Pay Model:</b> {run.pay_model}</p>
      <p><b>Rate:</b> {float(run.rate_value):,.4f}</p>
      <p><b>Total Pay:</b> {money(run.total_pay)}</p>

      <h3>Loads</h3>
      <table>
        <thead>
          <tr><th>Load ID</th><th style="text-align:right;">Pay</th></tr>
        </thead>
        <tbody>
          {row_html}
        </tbody>
      </table>
    </body>
    </html>
    """)

@router.get("/app/settlements/run/{run_id}", response_class=HTMLResponse)
def view_run(run_id: int, request: Request, db: Session = Depends(get_db)):
    if not require_login(request):
        return RedirectResponse(url="/login", status_code=303)

    company_id = int(request.session.get("company_id"))
    run = db.query(SettlementRun).filter(
        SettlementRun.company_id == company_id,
        SettlementRun.id == run_id
    ).first()

    if not run:
        return HTMLResponse("<p>Run not found</p>", status_code=404)

    rows = db.query(SettlementRunLoad).filter(
        SettlementRunLoad.company_id == company_id,
        SettlementRunLoad.settlement_run_id == run.id
    ).all()

    row_html = ""
    for r in rows:
        row_html += f"<tr><td>{r.load_id}</td><td style='text-align:right;'>{money(r.load_pay)}</td></tr>"

    return HTMLResponse(f"""
    <html>
    <head>
      <title>Settlement Run {run.id}</title>
      <style>
        body {{ font-family: Arial, sans-serif; margin:40px; }}
        table {{ width:520px; border-collapse:collapse; }}
        td, th {{ padding:10px; border-bottom:1px solid #eee; }}
        th {{ text-align:left; }}
        a {{ color:#1a73e8; text-decoration:none; }}
        .btn {{ display:inline-block; padding:10px 14px; border-radius:10px; background:#111; color:#fff; text-decoration:none; }}
      </style>
    </head>
    <body>
      <h2>Settlement Run #{run.id}</h2>
      <p><b>Type:</b> {run.person_type} • <b>Person ID:</b> {run.person_id}</p>
      <p><b>Model:</b> {run.pay_model} • <b>Rate:</b> {float(run.rate_value):,.4f}</p>
      <p><b>Total Pay:</b> {money(run.total_pay)}</p>

      <p><a class="btn" href="/app/settlements/print/{run.id}">Print / Download</a></p>

      <h3>Loads</h3>
      <table>
        <thead><tr><th>Load ID</th><th style="text-align:right;">Pay</th></tr></thead>
        <tbody>{row_html}</tbody>
      </table>

      <p><a href="/app/settlements">Back</a></p>
    </body>
    </html>
    """)
