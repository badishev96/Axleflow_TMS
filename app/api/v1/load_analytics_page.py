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

def money(x):
    return "$" + format(float(x), ",.2f")

@router.get("/app/loads/{load_id}/analytics", response_class=HTMLResponse)
def load_analytics(load_id: int, request: Request, db: Session = Depends(get_db)):
    if not require_login_page(request):
        return RedirectResponse(url="/login", status_code=303)

    company_id = int(request.session.get("company_id"))
    load = db.query(Load).filter(Load.company_id == company_id, Load.id == load_id).first()
    if not load:
        return HTMLResponse("<p>Load not found</p>", status_code=404)

    revenue = float(load.rate_amount or 0)
    miles = float(load.total_miles or 0)
    rpm = (revenue / miles) if miles > 0 else None

    expenses = db.query(Expense).filter(
        Expense.company_id == company_id,
        Expense.anchor_type == "load",
        Expense.anchor_id == load.id
    ).order_by(Expense.id.desc()).all()
    expense_total = sum(float(e.amount) for e in expenses) if expenses else 0.0

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

    profit = revenue - expense_total - driver_pay - dispatcher_pay

    # Settlement run links
    driver_run_ids = [x[0] for x in db.query(SettlementRunLoad.settlement_run_id).filter(
        SettlementRunLoad.company_id == company_id,
        SettlementRunLoad.load_id == load.id,
        SettlementRunLoad.person_type == "driver"
    ).distinct().all()]

    dispatcher_run_ids = [x[0] for x in db.query(SettlementRunLoad.settlement_run_id).filter(
        SettlementRunLoad.company_id == company_id,
        SettlementRunLoad.load_id == load.id,
        SettlementRunLoad.person_type == "dispatcher"
    ).distinct().all()]

    def run_links(ids):
        if not ids:
            return "None"
        return " ".join([f"<a href='/app/settlements/run/{rid}' target='_blank'>#{rid}</a>" for rid in ids])

    driver_runs_html = run_links(driver_run_ids)
    dispatcher_runs_html = run_links(dispatcher_run_ids)

    # Expense rows with clickable IDs
    exp_rows = ""
    for e in expenses:
        exp_rows += f"""<tr>
<td><a href='/app/expenses/{e.id}' target='_blank'>{e.id}</a></td>
<td>{e.expense_category}</td>
<td>{e.vendor_name or ''}</td>
<td style='text-align:right;'>{money(e.amount)}</td>
</tr>"""

    warn = ""
    if profit < 0:
        warn = "<div class='warn'><b>Warning:</b> Negative profit on this load.</div>"

    trend_link = f"/app/loads/{load.id}/trend2"

    return HTMLResponse(f"""
    <html>
    <head>
      <title>Load {load.id} Analytics</title>
      <style>
        body {{ font-family: Arial, sans-serif; margin:0; background:#fafafa; color:#111; }}
        .topbar {{ background:#111; color:#fff; padding:16px 24px; display:flex; justify-content:space-between; }}
        .wrap {{ padding:24px; max-width:1100px; margin:0 auto; }}
        .card {{ background:#fff; border:1px solid #e6e6e6; border-radius:14px; padding:14px; margin-bottom:12px; }}
        .section-title {{ font-weight:700; margin:0 0 8px 0; }}
        .muted {{ color:#666; font-size:12px; }}
        table {{ width:100%; border-collapse:collapse; }}
        th, td {{ padding:10px; border-bottom:1px solid #eee; text-align:left; }}
        th {{ font-size:12px; color:#666; text-transform:uppercase; letter-spacing:.03em; }}
        a {{ color:#1a73e8; text-decoration:none; }}
        .kpi {{ display:grid; grid-template-columns: repeat(4, 1fr); gap:10px; }}
        .k {{ background:#fff; border:1px solid #e6e6e6; border-radius:14px; padding:12px; }}
        .label {{ color:#666; font-size:12px; text-transform:uppercase; letter-spacing:.03em; }}
        .val {{ font-size:18px; font-weight:700; margin-top:6px; }}
        .warn {{ margin-top:10px; padding:12px; border-radius:12px; border:1px solid #ffd6d6; background:#fff1f1; }}
        @media(max-width:900px){{ .kpi{{grid-template-columns: repeat(2, 1fr);}} }}
      </style>
    </head>
    <body>
      <div class="topbar">
        <div style="font-weight:700;">AxleFlow — Load Analytics</div>
        <div><a href="/app/loads/{load.id}" style="color:#bbb;">Back to Load</a></div>
      </div>

      <div class="wrap">
        <div class="card">
          <div class="section-title">Load {load.id} — Summary</div>
          <div class="muted">Truck: {load.truck_id or ''} • Dispatcher: {load.dispatcher_id or ''}</div>
          <div class="muted">Pickup: {load.pickup_address or ''}</div>
          <div class="muted">Delivery: {load.delivery_address or ''}</div>
        </div>

        <div class="card">
          <div class="section-title">Revenue & Distance</div>
          <div class="kpi">
            <div class="k"><div class="label">Revenue</div><div class="val">{money(revenue)}</div></div>
            <div class="k"><div class="label">Miles</div><div class="val">{miles:,.2f}</div></div>
            <div class="k"><div class="label">Revenue/Mile</div><div class="val">{("N/A" if rpm is None else "$" + format(float(rpm), ",.3f"))}</div></div>
            <div class="k"><div class="label">Trends</div><div class="val"><a href="{trend_link}" target="_blank">Open</a></div></div>
          </div>
        </div>

        <div class="card">
          <div class="section-title">Direct Load Costs</div>
          <div class="kpi">
            <div class="k"><div class="label">Load Expenses</div><div class="val">{money(expense_total)}</div></div>
            <div class="k"><div class="label">Driver Pay</div><div class="val">{money(driver_pay)}</div></div>
            <div class="k"><div class="label">Dispatcher Pay</div><div class="val">{money(dispatcher_pay)}</div></div>
            <div class="k"><div class="label">Net Profit</div><div class="val">{money(profit)}</div></div>
          </div>
          {warn}
          <div style="margin-top:10px;">
            <div class="muted"><b>Driver Settlement Run(s):</b> {driver_runs_html}</div>
            <div class="muted"><b>Driver Settlement Status:</b> {"Paid ✅" if driver_run_ids else "Unpaid ⏳"}</div>
            <div class="muted" style="margin-top:6px;"><b>Dispatcher Settlement Run(s):</b> {dispatcher_runs_html}</div>
            <div class="muted"><b>Dispatcher Settlement Status:</b> {"Paid ✅" if dispatcher_run_ids else "Unpaid ⏳"}</div>
            <div class="muted" style="margin-top:6px;">(View-only proof links.)</div>
          </div>
          <div class="muted" style="margin-top:8px;">Overhead/fixed-cost context comes later (Phase 4).</div>
        </div>

        <div class="card">
          <div class="section-title">Expenses Affecting This Load</div>
          <table>
            <thead><tr><th>ID</th><th>Category</th><th>Vendor</th><th style="text-align:right;">Amount</th></tr></thead>
            <tbody>
              {exp_rows if exp_rows else "<tr><td colspan='4'>No load-anchored expenses</td></tr>"}
            </tbody>
          </table>
          <div class="muted" style="margin-top:8px;">Edit expenses in Expenses module (read-only here).</div>
        </div>
      </div>
    </body>
    </html>
    """)


