from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal

from app.db.session import get_db
from app.models.user import User
from app.models.truck import Truck
from app.models.load import Load
from app.models.expense import Expense
from app.models.settlement_run import SettlementRun
from app.models.settlement_run_load import SettlementRunLoad

router = APIRouter()

def require_login(request: Request):
    return bool(request.session.get("user_id"))

def money(x):
    return "$" + format(float(x), ",.2f")

def list_people(db: Session, company_id: int, role: str, search: str):
    q = db.query(User).filter(User.company_id == company_id, User.role == role)
    if search:
        q = q.filter(User.email.ilike(f"%{search}%"))
    return q.order_by(User.id.asc()).all()

def unpaid_loads_driver(db: Session, company_id: int, driver_id: int):
    truck_ids = db.query(Truck.id).filter(
        Truck.company_id == company_id,
        ((Truck.primary_driver_id == driver_id) | (Truck.secondary_driver_id == driver_id))
    ).subquery()

    loads = db.query(Load).filter(Load.company_id == company_id, Load.truck_id.in_(truck_ids)).all()

    paid_ids = set([x[0] for x in db.query(SettlementRunLoad.load_id).filter(
        SettlementRunLoad.company_id == company_id,
        SettlementRunLoad.person_type == "driver",
        SettlementRunLoad.person_id == driver_id
    ).all()])

    return [l for l in loads if l.id not in paid_ids]

def unpaid_loads_dispatcher(db: Session, company_id: int, dispatcher_id: int):
    loads = db.query(Load).filter(Load.company_id == company_id, Load.dispatcher_id == dispatcher_id).all()

    paid_ids = set([x[0] for x in db.query(SettlementRunLoad.load_id).filter(
        SettlementRunLoad.company_id == company_id,
        SettlementRunLoad.person_type == "dispatcher",
        SettlementRunLoad.person_id == dispatcher_id
    ).all()])

    return [l for l in loads if l.id not in paid_ids]

def paid_runs(db: Session, company_id: int, person_type: str, person_id: int):
    return db.query(SettlementRun).filter(
        SettlementRun.company_id == company_id,
        SettlementRun.person_type == person_type,
        SettlementRun.person_id == person_id
    ).order_by(SettlementRun.id.desc()).all()

@router.get("/app/settlements", response_class=HTMLResponse)
def settlements(request: Request, db: Session = Depends(get_db)):
    if not require_login(request):
        return RedirectResponse(url="/login", status_code=303)

    company_id = int(request.session.get("company_id"))
    q = request.query_params

    role_tab = (q.get("role_tab") or "drivers").strip().lower()
    tab = (q.get("tab") or "unpaid").strip().lower()
    search = (q.get("search") or "").strip().lower()
    person_id = q.get("person_id")
    person_id_int = int(person_id) if person_id and person_id.isdigit() else None

    if role_tab == "dispatchers":
        role = "dispatcher"
        person_type = "dispatcher"
        title = "Dispatchers"
    else:
        role = "driver"
        person_type = "driver"
        title = "Drivers"

    people = list_people(db, company_id, role, search)

    left = ""
    for p in people:
        active = "style='font-weight:700;'" if person_id_int == p.id else ""
        left += f"<li><a {active} href='/app/settlements?role_tab={role_tab}&person_id={p.id}&tab={tab}&search={search}'>{p.id} — {p.email}</a></li>"

    right = "<div class='card'><div class='muted'>Select a person on the left.</div></div>"

    if person_id_int:
        p = db.query(User).filter(User.company_id == company_id, User.id == person_id_int).first()
        if not p:
            return HTMLResponse("<p>Person not found</p>", status_code=404)

        if not p.pay_model or p.pay_rate is None:
            if person_type == "dispatcher":
                model_opts = "<option value='commission_gross'>Commission — Gross</option>"
            else:
                model_opts = "<option value='cpm'>CPM</option><option value='commission_gross'>Commission — Gross</option><option value='commission_net'>Commission — Net</option>"

            right = f"""
            <div class="card">
              <h3 style="margin-top:0;">{title[:-1]} {p.id}</h3>
              <p><b>Pay profile missing.</b> Set it once.</p>
              <form method="post" action="/app/settlements/set-pay-profile">
                <input type="hidden" name="role_tab" value="{role_tab}"/>
                <input type="hidden" name="person_id" value="{p.id}"/>
                <label>Pay Model</label>
                <select name="pay_model">{model_opts}</select>
                <label>Pay Rate</label>
                <input name="pay_rate" type="number" step="0.0001" required />
                <button type="submit">Save Pay Profile</button>
              </form>
            </div>
            """
        else:
            unpaid = unpaid_loads_dispatcher(db, company_id, p.id) if person_type == "dispatcher" else unpaid_loads_driver(db, company_id, p.id)
            runs = paid_runs(db, company_id, person_type, p.id)

            if tab == "paid":
                rows = ""
                for r in runs:
                    rows += f"<tr><td><a href='/app/settlements/run/{r.id}'>{r.id}</a></td><td>{r.pay_model}</td><td style='text-align:right;'>{money(r.total_pay)}</td><td>{r.created_at}</td></tr>"

                right = f"""
                <div class="card">
                  <h3 style="margin-top:0;">{title[:-1]} {p.id} — Paid</h3>
                  <table>
                    <thead><tr><th>Run</th><th>Model</th><th style="text-align:right;">Total Pay</th><th>Created</th></tr></thead>
                    <tbody>{rows if rows else "<tr><td colspan='4'>No runs yet</td></tr>"}</tbody>
                  </table>
                </div>
                """
            else:
                rows = ""
                for l in sorted(unpaid, key=lambda x: x.id, reverse=True):
                    rev = float(l.rate_amount or 0)
                    miles = float(l.total_miles or 0)
                    rows += f"<tr><td><input class='cb' type='checkbox' name='load_id' value='{l.id}'></td><td>{l.id}</td><td>{l.truck_id or ''}</td><td style='text-align:right;'>{money(rev)}</td><td style='text-align:right;'>{miles:,.2f}</td></tr>"

                right = f"""
                <div class="card">
                  <h3 style="margin-top:0;">{title[:-1]} {p.id} — Unpaid</h3>
                  <div class="muted">Select loads → Generate one settlement run</div>
                  <form method="post" action="/app/settlements/generate-run">
                    <input type="hidden" name="role_tab" value="{role_tab}"/>
                    <input type="hidden" name="person_id" value="{p.id}"/>
                    <div style="display:flex;gap:10px;margin:10px 0;">
                      <button type="button" onclick="document.querySelectorAll('.cb').forEach(cb=>cb.checked=true);">Select All</button>
                      <button type="button" onclick="document.querySelectorAll('.cb').forEach(cb=>cb.checked=false);">Clear</button>
                      <button type="submit">Generate Settlement Run</button>
                    </div>
                    <label>Total Miles (only for CPM when load miles are missing)</label>
                    <input name="entered_total_miles" placeholder="Optional" />
                    <table>
                      <thead><tr><th></th><th>Load</th><th>Truck</th><th style="text-align:right;">Revenue</th><th style="text-align:right;">Miles</th></tr></thead>
                      <tbody>{rows if rows else "<tr><td colspan='5'>No unpaid loads</td></tr>"}</tbody>
                    </table>
                  </form>
                </div>
                """

    drivers_tab = f"/app/settlements?role_tab=drivers&tab={tab}&search={search}"
    dispatchers_tab = f"/app/settlements?role_tab=dispatchers&tab={tab}&search={search}"
    unpaid_link = f"/app/settlements?role_tab={role_tab}&person_id={person_id_int or ''}&tab=unpaid&search={search}"
    paid_link = f"/app/settlements?role_tab={role_tab}&person_id={person_id_int or ''}&tab=paid&search={search}"

    return HTMLResponse(f"""
    <html><head><title>Settlements</title>
    <style>
      body {{ font-family: Arial, sans-serif; margin:0; background:#fafafa; }}
      .topbar {{ background:#111; color:#fff; padding:16px 24px; display:flex; justify-content:space-between; }}
      .wrap {{ padding:24px; max-width:1200px; margin:0 auto; }}
      .layout {{ display:grid; grid-template-columns: 320px 1fr; gap:12px; }}
      .card {{ background:#fff; border:1px solid #e6e6e6; border-radius:14px; padding:14px; }}
      .muted {{ color:#666; font-size:12px; }}
      a {{ color:#1a73e8; text-decoration:none; }}
      table {{ width:100%; border-collapse:collapse; }}
      th, td {{ padding:10px; border-bottom:1px solid #eee; }}
      button {{ padding:10px 12px; border-radius:12px; background:#111; color:#fff; border:0; cursor:pointer; }}
      input, select {{ width:100%; padding:10px; border:1px solid #ddd; border-radius:10px; margin-top:6px; }}
    </style></head>
    <body>
      <div class="topbar">
        <div style="font-weight:700;">AxleFlow — Settlements</div>
        <div><a href="/app" style="color:#bbb;">Dashboard</a></div>
      </div>

      <div class="wrap">
        <div style="margin-bottom:12px;">
          <a href="{drivers_tab}">Drivers</a> • <a href="{dispatchers_tab}">Dispatchers</a> • <span class="muted">Employees (coming soon)</span>
          <div style="margin-top:8px;">
            <a href="{unpaid_link}">Unpaid</a> • <a href="{paid_link}">Paid</a>
          </div>
        </div>

        <div class="layout">
          <div class="card">
            <h3 style="margin-top:0;">{title}</h3>
            <form method="get" action="/app/settlements">
              <input type="hidden" name="role_tab" value="{role_tab}"/>
              <input type="hidden" name="tab" value="{tab}"/>
              <label>Search</label>
              <input name="search" value="{search}" placeholder="email contains..." />
              <button type="submit" style="margin-top:10px;">Search</button>
            </form>
            <ul style="margin-top:10px;">{left if left else "<li>No people</li>"}</ul>
          </div>
          {right}
        </div>
      </div>
    </body></html>
    """)

@router.post("/app/settlements/set-pay-profile")
async def set_pay_profile(request: Request, db: Session = Depends(get_db)):
    if not require_login(request):
        return RedirectResponse(url="/login", status_code=303)

    form = await request.form()
    company_id = int(request.session.get("company_id"))

    role_tab = str(form.get("role_tab") or "drivers").strip().lower()
    person_id = int(form.get("person_id") or 0)
    pay_model = str(form.get("pay_model") or "").strip()
    pay_rate = Decimal(str(form.get("pay_rate") or "0"))

    p = db.query(User).filter(User.company_id == company_id, User.id == person_id).first()
    if not p:
        return HTMLResponse("<p>Person not found</p>", status_code=404)

    p.pay_model = pay_model
    p.pay_rate = pay_rate
    db.commit()

    return RedirectResponse(url=f"/app/settlements?role_tab={role_tab}&person_id={person_id}&tab=unpaid", status_code=303)

@router.post("/app/settlements/generate-run")
async def generate_run(request: Request, db: Session = Depends(get_db)):
    if not require_login(request):
        return RedirectResponse(url="/login", status_code=303)

    form = await request.form()
    company_id = int(request.session.get("company_id"))
    role_tab = str(form.get("role_tab") or "drivers").strip().lower()

    person_type = "dispatcher" if role_tab == "dispatchers" else "driver"
    person_id = int(form.get("person_id") or 0)

    p = db.query(User).filter(User.company_id == company_id, User.id == person_id).first()
    if not p or not p.pay_model or p.pay_rate is None:
        return HTMLResponse("<p>Pay profile missing</p>", status_code=422)

    load_ids = [int(x) for x in form.getlist("load_id") if str(x).isdigit()]
    if not load_ids:
        return HTMLResponse("<p>No loads selected</p>", status_code=422)

    loads = db.query(Load).filter(Load.company_id == company_id, Load.id.in_(load_ids)).all()

    dup = db.query(SettlementRunLoad).filter(
        SettlementRunLoad.company_id == company_id,
        SettlementRunLoad.person_type == person_type,
        SettlementRunLoad.person_id == person_id,
        SettlementRunLoad.load_id.in_(load_ids)
    ).first()
    if dup:
        return HTMLResponse("<p>Blocked: one or more loads already paid for this person.</p>", status_code=409)

    if person_type == "dispatcher":
        if p.pay_model != "commission_gross":
            return HTMLResponse("<p>Dispatcher supports Commission — Gross only (v1)</p>", status_code=422)

        pct = Decimal(str(p.pay_rate))
        gross = sum([Decimal(str(l.rate_amount or 0)) for l in loads])
        total_pay = (gross * pct) / Decimal("100") if gross > 0 else Decimal("0")

        run = SettlementRun(
            company_id=company_id,
            person_type="dispatcher",
            person_id=person_id,
            status="paid",
            pay_model="commission_gross",
            rate_value=pct,
            total_miles=None,
            total_gross=float(gross),
            total_net=float(gross),
            total_pay=float(total_pay),
            notes="dispatcher run"
        )
        db.add(run)
        db.commit()
        db.refresh(run)

        for l in loads:
            rev = Decimal(str(l.rate_amount or 0))
            share = (rev / gross) if gross > 0 else Decimal("0")
            lp = total_pay * share
            db.add(SettlementRunLoad(
                company_id=company_id,
                settlement_run_id=run.id,
                person_type="dispatcher",
                person_id=person_id,
                load_id=l.id,
                load_pay=float(lp)
            ))
        db.commit()

        return RedirectResponse(url=f"/app/settlements?role_tab=dispatchers&person_id={person_id}&tab=paid", status_code=303)

    # Driver CPM
    if p.pay_model != "cpm":
        return HTMLResponse("<p>Driver UI supports CPM only (v1)</p>", status_code=422)

    rate = Decimal(str(p.pay_rate))
    miles_list = [Decimal(str(l.total_miles or 0)) for l in loads]
    sum_miles = sum(miles_list)

    entered_total = str(form.get("entered_total_miles") or "").strip()
    if sum_miles <= 0:
        if not entered_total:
            return HTMLResponse("<p>CPM requires miles. Enter total miles if loads have no miles.</p>", status_code=422)
        total_miles = Decimal(entered_total)
        total_pay = total_miles * rate
        alloc = [total_pay / Decimal(len(loads)) for _ in loads]
    else:
        total_miles = sum_miles
        total_pay = total_miles * rate
        alloc = []
        for m in miles_list:
            share = (m / sum_miles) if sum_miles > 0 else Decimal("0")
            alloc.append(total_pay * share)

    run = SettlementRun(
        company_id=company_id,
        person_type="driver",
        person_id=person_id,
        status="paid",
        pay_model="cpm",
        rate_value=rate,
        total_miles=float(total_miles),
        total_gross=float(sum([Decimal(str(l.rate_amount or 0)) for l in loads])),
        total_net=float(sum([Decimal(str(l.rate_amount or 0)) for l in loads])),
        total_pay=float(total_pay),
        notes="driver cpm run"
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    for l, lp in zip(loads, alloc):
        db.add(SettlementRunLoad(
            company_id=company_id,
            settlement_run_id=run.id,
            person_type="driver",
            person_id=person_id,
            load_id=l.id,
            load_pay=float(lp)
        ))
    db.commit()

    return RedirectResponse(url=f"/app/settlements?role_tab=drivers&person_id={person_id}&tab=paid", status_code=303)
