from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.models.load import Load
from app.models.expense import Expense
from app.models.settlement_run_load import SettlementRunLoad

router = APIRouter()

def require_login_page(request: Request):
    return bool(request.session.get("user_id"))

@router.get("/app/loads/{load_id}/trend2", response_class=HTMLResponse)
def load_trend_v2(load_id: int, request: Request, db: Session = Depends(get_db)):
    if not require_login_page(request):
        return RedirectResponse(url="/login", status_code=303)

    company_id = int(request.session.get("company_id"))
    load = db.query(Load).filter(Load.company_id == company_id, Load.id == load_id).first()
    if not load:
        return HTMLResponse("<p>Load not found</p>", status_code=404)

    def money(x):
        return "$" + format(float(x), ",.2f")

    def profit_for_load(l):
        rev = float(l.rate_amount or 0)

        exps = db.query(Expense).filter(
            Expense.company_id == company_id,
            Expense.anchor_type == "load",
            Expense.anchor_id == l.id
        ).all()
        expt = sum([float(x.amount) for x in exps]) if exps else 0.0

        dp = float(db.query(func.coalesce(func.sum(SettlementRunLoad.load_pay), 0)).filter(
            SettlementRunLoad.company_id == company_id,
            SettlementRunLoad.load_id == l.id,
            SettlementRunLoad.person_type == "driver"
        ).scalar() or 0)

        dsp = float(db.query(func.coalesce(func.sum(SettlementRunLoad.load_pay), 0)).filter(
            SettlementRunLoad.company_id == company_id,
            SettlementRunLoad.load_id == l.id,
            SettlementRunLoad.person_type == "dispatcher"
        ).scalar() or 0)

        return rev - expt - dp - dsp

    current_profit = profit_for_load(load)

    recent = db.query(Load).filter(Load.company_id == company_id).order_by(Load.id.desc()).limit(50).all()
    company_profs = [profit_for_load(l) for l in recent] if recent else []
    company_avg = (sum(company_profs)/len(company_profs)) if company_profs else None

    truck_avg = None
    if load.truck_id is not None:
        t_recent = db.query(Load).filter(Load.company_id == company_id, Load.truck_id == load.truck_id).order_by(Load.id.desc()).limit(50).all()
        t_profs = [profit_for_load(l) for l in t_recent] if t_recent else []
        truck_avg = (sum(t_profs)/len(t_profs)) if t_profs else None

    dispatcher_avg = None
    if load.dispatcher_id is not None:
        d_recent = db.query(Load).filter(Load.company_id == company_id, Load.dispatcher_id == load.dispatcher_id).order_by(Load.id.desc()).limit(50).all()
        d_profs = [profit_for_load(l) for l in d_recent] if d_recent else []
        dispatcher_avg = (sum(d_profs)/len(d_profs)) if d_profs else None

    def delta(a, b):
        if b is None:
            return None
        return a - b

    def signal(a, b):
        if b is None:
            return ("N/A", "#666")
        d = a - b
        if d >= 0:
            return ("OK", "#137333")
        if d >= -100:
            return ("WATCH", "#b06000")
        return ("BAD", "#b00020")

    def row(label, avg):
        d = delta(current_profit, avg)
        sig, color = signal(current_profit, avg)
        avg_txt = money(avg) if avg is not None else "N/A"
        d_txt = money(d) if d is not None else "N/A"
        return f"<tr><td>{label}</td><td style='text-align:right;'>{avg_txt}</td><td style='text-align:right;'>{d_txt}</td><td style='text-align:right; color:{color}; font-weight:700;'>{sig}</td></tr>"

    # Cost driver breakdown (shows when profit is negative)
    load_expenses = db.query(Expense).filter(
        Expense.company_id == company_id,
        Expense.anchor_type == "load",
        Expense.anchor_id == load.id
    ).all()
    exp_total = sum([float(x.amount) for x in load_expenses]) if load_expenses else 0.0
    top_exp = sorted(load_expenses, key=lambda x: float(x.amount), reverse=True)[:3]

    driver_pay = float(db.query(func.coalesce(func.sum(SettlementRunLoad.load_pay), 0)).filter(
        SettlementRunLoad.company_id == company_id,
        SettlementRunLoad.load_id == load.id,
        SettlementRunLoad.person_type == "driver"
    ).scalar() or 0)

    dispatcher_pay = float(db.query(func.coalesce(func.sum(SettlementRunLoad.load_pay), 0)).filter(
        SettlementRunLoad.company_id == company_id,
        SettlementRunLoad.load_id == load.id,
        SettlementRunLoad.person_type == "dispatcher"
    ).scalar() or 0)

    miles = float(load.total_miles or 0)
    rpm = (float(load.rate_amount or 0) / miles) if miles > 0 else None

    exp_list = ""
    for e in top_exp:
        exp_list += f"<li>{(e.vendor_name or '')} — {money(e.amount)}</li>"

    why_html = ""
    if True:
        why_html = f"""
        <h3>Why this load is BAD (cost drivers)</h3>
        <ul>
          <li><b>Driver pay:</b> {money(driver_pay)}</li>
          <li><b>Dispatcher pay:</b> {money(dispatcher_pay)}</li>
          <li><b>Total load-anchored expenses:</b> {money(exp_total)}</li>
          <li><b>Top expenses:</b><ul>{exp_list if exp_list else "<li>None</li>"}</ul></li>
          <li><b>Revenue per mile:</b> {"N/A" if rpm is None else "$" + format(float(rpm), ",.3f")}</li>
        </ul>
        <p style="color:#666;">Next step: reduce the largest cost driver or renegotiate the lane/rate.</p>
        """

    return HTMLResponse(f"""
    <html>
    <head>
      <title>Load {load.id} Trends</title>
      <style>
        body {{ font-family: Arial, sans-serif; margin:40px; }}
        table {{ width:760px; border-collapse:collapse; }}
        th, td {{ padding:10px; border-bottom:1px solid #eee; text-align:left; }}
        th {{ font-size:12px; color:#666; text-transform:uppercase; letter-spacing:.03em; }}
        .muted {{ color:#666; font-size:12px; }}
        a {{ color:#1a73e8; text-decoration:none; }}
      </style>
    </head>
    <body>
      <h2>Load {load.id} Trends (v2)</h2>
      <p><b>Profit (this load):</b> {money(current_profit)}</p>

      <table>
        <thead>
          <tr><th>Benchmark</th><th style="text-align:right;">Avg Profit</th><th style="text-align:right;">Delta</th><th style="text-align:right;">Signal</th></tr>
        </thead>
        <tbody>
          {row("Company (recent loads)", company_avg)}
          {row(f"Truck {load.truck_id} (recent loads)" if load.truck_id is not None else "Truck (N/A)", truck_avg)}
          {row(f"Dispatcher {load.dispatcher_id} (recent loads)" if load.dispatcher_id is not None else "Dispatcher (N/A)", dispatcher_avg)}
        </tbody>
      </table>

      <p class="muted">Signals: OK = at/above benchmark • WATCH = within  below • BAD = more than  below.</p>
      <p class="muted">Benchmarks use recent loads only (v1). Date-range + lane averages come next.</p>

      {why_html}

      <p><a href="/app/loads/{load.id}">Back to Load</a></p>
    </body>
    </html>
    """)
