from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.db.session import get_db

from app.models.load import Load
from app.models.load_draft import LoadDraft
from app.models.draft import Draft

from app.models.expense import Expense
from app.models.fuel_transaction import FuelTransaction
from app.models.settlement import Settlement
from app.models.settlement_run_load import SettlementRunLoad
from app.models.truck import Truck

router = APIRouter()

def bounds(range_name: str):
    now = datetime.utcnow()
    if range_name == "week":
        start = now - timedelta(days=7)
    elif range_name == "quarter":
        start = now - timedelta(days=90)
    elif range_name == "year":
        start = now - timedelta(days=365)
    else:
        start = now - timedelta(days=30)
    return start, now

def money(x): return f"${float(x):,.2f}"
def num(x): return f"{float(x):,.2f}"

def require_login_page(request: Request):
    if not request.session.get("user_id"):
        return False
    return True

@router.get("/app", response_class=HTMLResponse)
def app_home(request: Request, db: Session = Depends(get_db)):
    if not require_login_page(request):
        return HTMLResponse("<p>Not logged in. Go to <a href='/login'>/login</a>.</p>")

    user_id = int(request.session.get("user_id"))
    company_id = int(request.session.get("company_id"))
    role = request.session.get("role")

    q = request.query_params
    range_name = q.get("range", "month")
    truck_id = q.get("truck_id")
    driver_id = q.get("driver_id")

    truck_id_int = int(truck_id) if truck_id and truck_id.isdigit() else None
    driver_id_int = int(driver_id) if driver_id and driver_id.isdigit() else None

    start, end = bounds(range_name)

    trucks = db.query(Truck.id).filter(Truck.company_id == company_id).order_by(Truck.id.asc()).all()
    truck_options = [t[0] for t in trucks]

    driver_ids_primary = db.query(Settlement.primary_driver_id).filter(
        Settlement.company_id == company_id,
        Settlement.primary_driver_id.isnot(None)
    ).distinct().all()
    driver_ids_secondary = db.query(Settlement.secondary_driver_id).filter(
        Settlement.company_id == company_id,
        Settlement.secondary_driver_id.isnot(None)
    ).distinct().all()
    driver_options = sorted({d[0] for d in driver_ids_primary + driver_ids_secondary if d[0] is not None})

    scope_title = "Company Dashboard"

    load_filter = [Load.company_id == company_id, Load.created_at >= start, Load.created_at < end]
    if truck_id_int is not None:
        load_filter.append(Load.truck_id == truck_id_int)
        scope_title = f"Truck Dashboard (truck_id={truck_id_int})"

    load_count = db.query(func.count(Load.id)).filter(*load_filter).scalar() or 0
    revenue = db.query(func.coalesce(func.sum(Load.rate_amount), 0)).filter(*load_filter).scalar() or 0
    miles = db.query(func.coalesce(func.sum(Load.total_miles), 0)).filter(*load_filter).scalar() or 0

    if truck_id_int is None:
        expenses = db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
            Expense.company_id == company_id,
            Expense.created_at >= start,
            Expense.created_at < end
        ).scalar() or 0
    else:
        expenses = db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
            Expense.company_id == company_id,
            Expense.anchor_type == "truck",
            Expense.anchor_id == truck_id_int,
            Expense.created_at >= start,
            Expense.created_at < end
        ).scalar() or 0

    if truck_id_int is None:
        fuel = db.query(func.coalesce(func.sum(FuelTransaction.total_cost), 0)).filter(
            FuelTransaction.company_id == company_id,
            FuelTransaction.created_at >= start,
            FuelTransaction.created_at < end
        ).scalar() or 0
    else:
        fuel = db.query(func.coalesce(func.sum(FuelTransaction.total_cost), 0)).filter(
            FuelTransaction.company_id == company_id,
            FuelTransaction.assignment_context_type == "truck",
            FuelTransaction.assignment_context_id == truck_id_int,
            FuelTransaction.created_at >= start,
            FuelTransaction.created_at < end
        ).scalar() or 0

    if truck_id_int is None:
        settlements = db.query(func.coalesce(func.sum(Settlement.commission_pool_amount), 0)).filter(
            Settlement.company_id == company_id,
            Settlement.created_at >= start,
            Settlement.created_at < end
        ).scalar() or 0
    else:
        settlements = db.query(func.coalesce(func.sum(Settlement.commission_pool_amount), 0)).filter(
            Settlement.company_id == company_id,
            Settlement.truck_id == truck_id_int,
            Settlement.created_at >= start,
            Settlement.created_at < end
        ).scalar() or 0

    net_margin = float(revenue) - float(expenses) - float(fuel) - float(settlements)
    profit_per_mile = (net_margin / float(miles)) if float(miles) > 0 else None
    ppm_display = "N/A" if profit_per_mile is None else f"${profit_per_mile:,.3f}"

    warnings = []
    if net_margin < 0:
        warnings.append("NEGATIVE_MARGIN")

    range_opts = ["week", "month", "quarter", "year"]
    range_html = "".join([f"<option value='{r}' {'selected' if r==range_name else ''}>{r}</option>" for r in range_opts])

    truck_html = "<option value='' " + ("selected" if truck_id_int is None else "") + ">All</option>"
    for tid in truck_options:
        sel = "selected" if truck_id_int == tid else ""
        truck_html += f"<option value='{tid}' {sel}>{tid}</option>"

    driver_html = "<option value='' " + ("selected" if driver_id_int is None else "") + ">All</option>"
    for did in driver_options:
        sel = "selected" if driver_id_int == did else ""
        driver_html += f"<option value='{did}' {sel}>{did}</option>"

    warning_html = "<li>None</li>" if not warnings else "".join([f"<li>{w}</li>" for w in warnings])
    negative = net_margin < 0

    return HTMLResponse(f"""
    <html>
    <head>
      <title>AxleFlow TMS</title>
      <style>
        body {{ font-family: Arial, sans-serif; margin: 0; background:#fafafa; color:#111; }}
        .topbar {{ background:#111; color:#fff; padding:16px 24px; display:flex; justify-content:space-between; align-items:center; }}
        .topbar small {{ color:#bbb; }}
        .wrap {{ padding:24px; max-width:1100px; margin: 0 auto; }}
        .grid {{ display:grid; grid-template-columns: repeat(4, 1fr); gap:12px; }}
        .card {{ background:#fff; border:1px solid #e6e6e6; border-radius:14px; padding:14px; }}
        .label {{ color:#666; font-size:12px; text-transform: uppercase; letter-spacing:.03em; }}
        .value {{ font-size:22px; font-weight:700; margin-top:6px; }}
        .value.neg {{ color:#b00020; }}
        .value.pos {{ color:#137333; }}
        .row {{ display:grid; grid-template-columns: 2fr 1fr; gap:12px; margin-top:12px; }}
        table {{ width:100%; border-collapse: collapse; }}
        td {{ padding:10px; border-bottom:1px solid #eee; }}
        td:first-child {{ color:#444; }}
        .warnbox {{ border:1px solid #ffd6d6; background:#fff1f1; border-radius:14px; padding:14px; }}
        .muted {{ color:#666; }}
        .toolbar {{ margin-top:12px; display:flex; gap:12px; flex-wrap:wrap; background:#fff; border:1px solid #e6e6e6; border-radius:14px; padding:12px; align-items:flex-end; }}
        label {{ font-size:12px; color:#666; display:block; margin-bottom:6px; }}
        select {{ padding:8px; border:1px solid #ddd; border-radius:10px; min-width:140px; }}
        button {{ padding:10px 14px; border:0; border-radius:12px; background:#111; color:#fff; cursor:pointer; }}
        a {{ color:#bbb; text-decoration:none; }}
        @media (max-width: 900px) {{ .grid {{ grid-template-columns: repeat(2, 1fr); }} .row {{ grid-template-columns: 1fr; }} }}
      </style>
    </head>
    <body>
      <div class="topbar">
        <div>
          <div style="font-size:18px;font-weight:700;">AxleFlow TMS</div>
          <small>User {user_id} • Company {company_id} • Role {role}</small>
        </div>
        <div class="muted">
          <a href="/app/loads">Loads</a> • <a href="/app/expenses">Expenses</a> • <a href="/app/fuel">Fuel</a> • <a href="/app/settlements">Settlements</a> • <a href="/app/drivers">Drivers</a> •
          <form method="post" action="/logout" style="display:inline;">
            <button style="padding:8px 12px;border-radius:10px;border:0;cursor:pointer;background:#333;color:#fff;">Logout</button>
          </form>
        </div>
      </div>

      <div class="wrap">
        <h2 style="margin:0 0 6px 0;">{scope_title}</h2>
        <div class="muted">Range: {range_name}</div>

        <form class="toolbar" method="get" action="/app">
          <div><label>Range</label><select name="range">{range_html}</select></div>
          <div><label>Truck ID</label><select name="truck_id">{truck_html}</select></div>
          <div><label>Driver ID</label><select name="driver_id">{driver_html}</select></div>
          <div><button type="submit">Apply</button></div>
        </form>

        <div style="height:12px;"></div>

        <div class="grid">
          <div class="card"><div class="label">Revenue</div><div class="value">{money(revenue)}</div><div class="muted">Loads: {int(load_count)}</div></div>
          <div class="card"><div class="label">Miles</div><div class="value">{num(miles)}</div><div class="muted">Total miles</div></div>
          <div class="card"><div class="label">Net Margin</div><div class="value {'neg' if negative else 'pos'}">{money(net_margin)}</div><div class="muted">Revenue - costs</div></div>
          <div class="card"><div class="label">Profit / Mile</div><div class="value {'neg' if (profit_per_mile is not None and profit_per_mile < 0) else 'pos'}">{ppm_display}</div><div class="muted">Net margin / miles</div></div>
        </div>

        <div class="row">
          <div class="card">
            <div style="font-weight:700;margin-bottom:8px;">Cost Breakdown</div>
            <table>
              <tr><td>Expenses</td><td style="text-align:right;">{money(expenses)}</td></tr>
              <tr><td>Fuel</td><td style="text-align:right;">{money(fuel)}</td></tr>
              <tr><td>Settlements</td><td style="text-align:right;">{money(settlements)}</td></tr>
            </table>
          </div>

          <div class="warnbox">
            <div style="font-weight:700;margin-bottom:8px;">Warnings</div>
            <ul>{warning_html}</ul>
            <div class="muted">These flags are designed to prompt early action.</div>
          </div>
        </div>
      </div>
    </body>
    </html>
    """)

revenue = float(load.rate_amount or 0)
    miles = float(load.total_miles or 0)

    # Load-anchored expenses (net commission transparency starts here)
    load_expenses = db.query(Expense).filter(
        Expense.company_id == company_id,
        Expense.anchor_type == "load",
        Expense.anchor_id == load.id
    ).order_by(Expense.id.desc()).all()
    total_expenses = sum([float(e.amount) for e in load_expenses]) if load_expenses else 0.0

    # Driver pay + Dispatcher pay from settlement runs
    # (per your rule: one load can be settled once per person type)
    driver_pay = db.query(func.coalesce(func.sum(SettlementRunLoad.load_pay), 0)).filter(
        SettlementRunLoad.company_id == company_id,
        SettlementRunLoad.load_id == load.id,
        SettlementRunLoad.person_type == "driver"
    ).scalar() or 0

    dispatcher_pay = db.query(func.coalesce(func.sum(SettlementRunLoad.load_pay), 0)).filter(
        SettlementRunLoad.company_id == company_id,
        SettlementRunLoad.load_id == load.id,
        SettlementRunLoad.person_type == "dispatcher"
    ).scalar() or 0

    driver_pay = float(driver_pay)
    dispatcher_pay = float(dispatcher_pay)

    profit = revenue - total_expenses - driver_pay - dispatcher_pay

    def money(x): return f"${float(x):,.2f}"

    exp_rows = ""
    for e in load_expenses:
        exp_rows += f'<tr><td><a href="/app/expenses/{e.id}" target="_blank">{e.id}</a></td><td>{e.expense_category}</td><td>{e.vendor_name}</td><td style="text-align:right;">{money(e.amount)}</td></tr>'

    warning = ""
    if profit < 0:
        warning = "<div style='margin-top:12px;padding:12px;border-radius:12px;border:1px solid #ffd6d6;background:#fff1f1;'><b>Warning:</b> Negative profit on this load.</div>"

    return HTMLResponse(f"""
    <html><head><title>Load {load.id}</title>
    <style>
      body {{ font-family: Arial, sans-serif; margin:0; background:#fafafa; color:#111; }}
      .topbar {{ background:#111; color:#fff; padding:16px 24px; display:flex; justify-content:space-between; }}
      .wrap {{ padding:24px; max-width:1100px; margin:0 auto; }}
      .card {{ background:#fff; border:1px solid #e6e6e6; border-radius:14px; padding:14px; margin-bottom:12px; }}
      table {{ width:100%; border-collapse:collapse; }}
      th, td {{ padding:10px; border-bottom:1px solid #eee; text-align:left; }}
      th {{ font-size:12px; color:#666; text-transform:uppercase; letter-spacing:.03em; }}
      a {{ color:#bbb; text-decoration:none; }}
      .kpi {{ display:grid; grid-template-columns: repeat(5, 1fr); gap:10px; }}
      .k {{ background:#fff; border:1px solid #e6e6e6; border-radius:14px; padding:12px; }}
      .label {{ color:#666; font-size:12px; text-transform:uppercase; letter-spacing:.03em; }}
      .val {{ font-size:20px; font-weight:700; margin-top:6px; }}
      @media(max-width:900px){{ .kpi{{grid-template-columns: repeat(2, 1fr);}} }}
    </style></head>
    <body>
      <div class="topbar">
        <div style="font-weight:700;">AxleFlow — Load Detail</div>
        <div><a href="/app/loads" style="color:#bbb;">Back to Loads</a></div>
      </div>

      <div class="wrap">
        <h2 style="margin-top:0;">Load #{load.id}</h2><div style="margin:8px 0 16px 0;"><a href="/app/loads/{load.id}/analytics" style="padding:10px 14px;border-radius:10px;background:#111;color:#fff;text-decoration:none;">Analytics</a> <a href="#" onclick="openDrawer('/app/expenses/new?anchor_type=load&anchor_id={load.id}','Add Expense'); return false;" style="margin-left:10px;padding:10px 14px;border-radius:10px;background:#f5f5f5;color:#111;text-decoration:none;border:1px solid #ddd;">Add Expense</a></div>
        <div class="card">
          <div><b>Truck:</b> {load.truck_id or ''} &nbsp; | &nbsp; <b>Dispatcher:</b> {load.dispatcher_id or ''}</div>
          <div><b>Pickup:</b> {load.pickup_address or ''}</div>
          <div><b>Delivery:</b> {load.delivery_address or ''}</div>
        </div>

        <div class="kpi">
          <div class="k"><div class="label">Revenue</div><div class="val">{money(revenue)}</div></div>
          <div class="k"><div class="label">Miles</div><div class="val">{miles:,.2f}</div></div>
          <div class="k"><div class="label">Expenses</div><div class="val">{money(total_expenses)}</div></div>
          <div class="k"><div class="label">Driver Pay</div><div class="val">{money(driver_pay)}</div></div>
          <div class="k"><div class="label">Dispatcher Pay</div><div class="val">{money(dispatcher_pay)}</div></div>
        </div>

        <div class="card">
          <div class="label">Profit</div>
          <div class="val">{money(profit)}</div>{warning}</div>

        <div class="card">
          <div class="muted">Trends are optional.</div>
          <p><a href="/app/loads/{load.id}/trend2" target="_blank">View Trends (opens in new tab)</a></p>
        </div>

        <div class="card">
          <h3 style="margin-top:0;">Load Expenses (Anchor: load)</h3>
          <table>
            <thead><tr><th>ID</th><th>Category</th><th>Vendor</th><th style="text-align:right;">Amount</th></tr></thead>
            <tbody>
              {exp_rows if exp_rows else '<tr><td colspan="4">No load-anchored expenses</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>
    {DRAWER_HTML}</body></html>
    """)

@router.get("/app/loads/{load_id}/trend", response_class=HTMLResponse)
def load_trend_debug(load_id: int, request: Request, db: Session = Depends(get_db)):
    if not require_login_page(request):
        return RedirectResponse(url="/login", status_code=303)

    company_id = int(request.session.get("company_id"))

    load = db.query(Load).filter(Load.company_id == company_id, Load.id == load_id).first()
    if not load:
        return HTMLResponse("<p>Load not found</p>", status_code=404)

    # Current load profit
    revenue = float(load.rate_amount or 0)
    load_expenses = db.query(Expense).filter(
        Expense.company_id == company_id,
        Expense.anchor_type == "load",
        Expense.anchor_id == load.id
    ).all()
    total_expenses = sum([float(e.amount) for e in load_expenses]) if load_expenses else 0.0

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

    profit = revenue - total_expenses - driver_pay - dispatcher_pay

    # Company benchmark (last 30 days): avg profit per load
    loads_30 = db.query(Load).filter(Load.company_id == company_id).order_by(Load.id.desc()).limit(50).all()
    # NOTE: simple benchmark using recent loads only (v1)
    profs = []
    for l in loads_30:
        rev = float(l.rate_amount or 0)
        exps = db.query(Expense).filter(Expense.company_id == company_id, Expense.anchor_type == "load", Expense.anchor_id == l.id).all()
        expt = sum([float(x.amount) for x in exps]) if exps else 0.0
        dp = float(db.query(func.coalesce(func.sum(SettlementRunLoad.load_pay), 0)).filter(
            SettlementRunLoad.company_id == company_id, SettlementRunLoad.load_id == l.id, SettlementRunLoad.person_type == "driver"
        ).scalar() or 0)
        dsp = float(db.query(func.coalesce(func.sum(SettlementRunLoad.load_pay), 0)).filter(
            SettlementRunLoad.company_id == company_id, SettlementRunLoad.load_id == l.id, SettlementRunLoad.person_type == "dispatcher"
        ).scalar() or 0)
        profs.append(rev - expt - dp - dsp)

    avg_profit = sum(profs)/len(profs) if profs else None
    delta = (profit - avg_profit) if avg_profit is not None else None
    delta_pct = ((profit - avg_profit)/avg_profit) if (avg_profit not in [None, 0]) else None

    def money(x): return f"${float(x):,.2f}"
    def pct(x): return f"{x*100:,.1f}%" if x is not None else "N/A"

    return HTMLResponse(f"""
    <html><body style="font-family:Arial;margin:40px;">
      <h2>Load {load.id} Trend Debug</h2>
      <p><b>Profit:</b> {money(profit)}</p>
      <p><b>Company Avg (recent loads):</b> {money(avg_profit) if avg_profit is not None else "N/A"}</p>
      <p><b>Delta:</b> {money(delta) if delta is not None else "N/A"} ({pct(delta_pct)})</p>
      <p><a href="/app/loads/{load.id}">Back to Load</a></p>
    {DRAWER_HTML}</body></html>
    """)

@router.get("/app/loads/{load_id}/trend", response_class=HTMLResponse)
def load_trend_debug(load_id: int, request: Request, db: Session = Depends(get_db)):
    if not require_login_page(request):
        return RedirectResponse(url="/login", status_code=303)

    company_id = int(request.session.get("company_id"))
    load = db.query(Load).filter(Load.company_id == company_id, Load.id == load_id).first()
    if not load:
        return HTMLResponse("<p>Load not found</p>", status_code=404)

    revenue = float(load.rate_amount or 0)

    load_expenses = db.query(Expense).filter(
        Expense.company_id == company_id,
        Expense.anchor_type == "load",
        Expense.anchor_id == load.id
    ).all()
    total_expenses = sum([float(e.amount) for e in load_expenses]) if load_expenses else 0.0

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

    profit = revenue - total_expenses - driver_pay - dispatcher_pay

    # v1 benchmark: average profit over last 50 loads (quick + safe)
    loads_50 = db.query(Load).filter(Load.company_id == company_id).order_by(Load.id.desc()).limit(50).all()
    profs = []
    for l in loads_50:
        rev = float(l.rate_amount or 0)
        exps = db.query(Expense).filter(Expense.company_id == company_id, Expense.anchor_type == "load", Expense.anchor_id == l.id).all()
        expt = sum([float(x.amount) for x in exps]) if exps else 0.0
        dp = float(db.query(func.coalesce(func.sum(SettlementRunLoad.load_pay), 0)).filter(
            SettlementRunLoad.company_id == company_id, SettlementRunLoad.load_id == l.id, SettlementRunLoad.person_type == "driver"
        ).scalar() or 0)
        dsp = float(db.query(func.coalesce(func.sum(SettlementRunLoad.load_pay), 0)).filter(
            SettlementRunLoad.company_id == company_id, SettlementRunLoad.load_id == l.id, SettlementRunLoad.person_type == "dispatcher"
        ).scalar() or 0)
        profs.append(rev - expt - dp - dsp)

    avg_profit = (sum(profs) / len(profs)) if profs else None
    delta = (profit - avg_profit) if avg_profit is not None else None

    def money(x): return f"${float(x):,.2f}"

    return HTMLResponse(f"""
    <html><body style="font-family:Arial;margin:40px;">
      <h2>Load {load.id} Trend Debug</h2>
      <p><b>Profit:</b> {money(profit)}</p>
      <p><b>Company Avg Profit (recent loads):</b> {money(avg_profit) if avg_profit is not None else "N/A"}</p>
      <p><b>Delta:</b> {money(delta) if delta is not None else "N/A"}</p>
      <p><a href="/app/loads/{load.id}">Back to Load</a></p>
    {DRAWER_HTML}</body></html>
    """)


@router.get("/app/loads/{load_id}/analytics", response_class=HTMLResponse)
def load_analytics(load_id: int, request: Request, db: Session = Depends(get_db)):
    if not require_login_page(request):
        return RedirectResponse(url="/login", status_code=303)

    company_id = int(request.session.get("company_id"))
    load = db.query(Load).filter(
        Load.company_id == company_id,
        Load.id == load_id
    ).first()

    if not load:
        return HTMLResponse("<p>Load not found</p>", status_code=404)

    revenue = float(load.rate_amount or 0)

    expenses = db.query(Expense).filter(
        Expense.company_id == company_id,
        Expense.anchor_type == "load",
        Expense.anchor_id == load.id
    ).all()
    expense_total = sum(float(e.amount) for e in expenses)

    driver_pay = float(
        db.query(func.coalesce(func.sum(SettlementRunLoad.load_pay), 0))
        .filter(
            SettlementRunLoad.company_id == company_id,
            SettlementRunLoad.load_id == load.id,
            SettlementRunLoad.person_type == "driver"
        ).scalar() or 0
    )

    dispatcher_pay = float(
        db.query(func.coalesce(func.sum(SettlementRunLoad.load_pay), 0))
        .filter(
            SettlementRunLoad.company_id == company_id,
            SettlementRunLoad.load_id == load.id,
            SettlementRunLoad.person_type == "dispatcher"
        ).scalar() or 0
    )

    profit = revenue - expense_total - driver_pay - dispatcher_pay

    rows = ""
    for e in expenses:
        rows += f"<tr><td>{e.expense_category}</td><td>{e.vendor_name or ''}</td><td style='text-align:right;'></td></tr>"

    return HTMLResponse(f'''
    <html>
    <head>
      <title>Load {load.id} Analytics</title>
      <style>
        body {{ font-family: Arial; margin:40px; }}
        table {{ width:100%; border-collapse:collapse; }}
        th, td {{ padding:10px; border-bottom:1px solid #eee; }}
        th {{ text-align:left; font-size:12px; color:#666; }}
        .card {{ border:1px solid #ddd; border-radius:12px; padding:16px; margin-bottom:16px; }}
      </style>
    </head>
    <body>
      <h2>Load {load.id} — Analytics</h2>

      <div class="card">
        <p><b>Revenue:</b> </p>
        <p><b>Load Expenses:</b> </p>
        <p><b>Driver Pay:</b> </p>
        <p><b>Dispatcher Pay:</b> </p>
        <p><b>Net Profit:</b> </p>
      </div>

      <div class="card">
        <h3>Expenses Affecting This Load</h3>
        <table>
          <thead>
            <tr>
              <th>Type</th>
              <th>Vendor</th>
              <th style="text-align:right;">Amount</th>
            </tr>
          </thead>
          <tbody>
            {rows if rows else "<tr><td colspan='3'>No expenses</td></tr>"}
          </tbody>
        </table>
      </div>

      <p><a href="/app/loads/{load.id}">← Back to Load</a></p>
    </body>
    </html>
    ''')








# ----------------------------
# Phase 4 UI Foundation
# Global Drawer HTML (stored as string; injected into pages later)
# ----------------------------
DRAWER_HTML = r"""

# ----------------------------
# Phase 4 UI Foundation
# Global Drawer HTML (stored as string; injected into pages later)
# ----------------------------
DRAWER_HTML = r"""
<!-- Global Drawer Container (Phase 4) -->
<div id="global-drawer-overlay" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:9998;" onclick="closeDrawer()"></div>

<div id="global-drawer" style="display:none;position:fixed;top:0;right:0;width:520px;max-width:90%;height:100%;background:#fff;z-index:9999;box-shadow:-4px 0 12px rgba(0,0,0,.15);overflow:auto;">
  <div style="padding:16px;border-bottom:1px solid #eee;display:flex;justify-content:space-between;align-items:center;">
    <strong id="drawer-title">Panel</strong>
    <button onclick="closeDrawer()" style="border:none;background:#eee;padding:6px 10px;border-radius:6px;cursor:pointer;">Close</button>
  </div>
  <div id="drawer-content" style="padding:16px;"></div>
</div>

<script>
function openDrawer(url, title){
  document.getElementById('drawer-title').innerText = title || 'Panel';
  document.getElementById('drawer-content').innerHTML = '<p>Loading...</p>';
  document.getElementById('global-drawer').style.display = 'block';
  document.getElementById('global-drawer-overlay').style.display = 'block';
  fetch(url).then(r=>r.text()).then(html=>{
    document.getElementById('drawer-content').innerHTML = html;
  });
}
function closeDrawer(){
  document.getElementById('global-drawer').style.display = 'none';
  document.getElementById('global-drawer-overlay').style.display = 'none';
  document.getElementById('drawer-content').innerHTML = '';
}
</script>

