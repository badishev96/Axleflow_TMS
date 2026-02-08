from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.db.session import get_db

from app.models.fuel_transaction import FuelTransaction
from app.models.draft import Draft
from app.models.fuel_transaction_draft import FuelTransactionDraft
from app.models.fuel_card import FuelCard

router = APIRouter()

def money(x): return f"${float(x):,.2f}"
def num(x): return f"{float(x):,.2f}"

def require_login(request: Request):
    return bool(request.session.get("user_id"))

def parse_dt_user(s: str):
    s = (s or "").strip()
    fmts = ["%m/%d/%y", "%m/%d/%y %I:%M %p"]
    for f in fmts:
        try:
            dt = datetime.strptime(s, f)
            if f == "%m/%d/%y":
                return datetime(dt.year, dt.month, dt.day, 0, 0)  # default 00:00 per lock
            return dt
        except ValueError:
            pass
    raise ValueError("Use M/D/YY or M/D/YY H:MM AM (example: 2/5/25 or 2/5/25 8:00 AM)")

@router.get("/app/fuel", response_class=HTMLResponse)
def fuel_page(request: Request, db: Session = Depends(get_db)):
    if not require_login(request):
        return RedirectResponse(url="/login", status_code=303)

    company_id = int(request.session.get("company_id"))
    txs = db.query(FuelTransaction).filter(FuelTransaction.company_id == company_id).order_by(FuelTransaction.id.desc()).all()

    rows = ""
    for t in txs:
        rows += f"""
        <tr>
          <td><a href="/app/fuel/{t.id}" target="_blank">{t.id}</a></td>
          <td>{t.transaction_datetime}</td>
          <td>{t.state}</td>
          <td>{t.fuel_card_number or ""}</td>
          <td>{t.assignment_context_type or ""}:{t.assignment_context_id or ""}</td>
          <td style="text-align:right;">{num(t.gallons)}</td>
          <td style="text-align:right;">{money(t.total_cost)}</td>
          <td>{t.vendor_name or ""}</td>
        </tr>
        """

    return HTMLResponse(f"""
    <html><head><title>AxleFlow — Fuel</title>
    <style>
      body {{ font-family: Arial, sans-serif; margin:0; background:#fafafa; }}
      .topbar {{ background:#111; color:#fff; padding:16px 24px; display:flex; justify-content:space-between; }}
      .wrap {{ padding:24px; max-width:1100px; margin:0 auto; }}
      .card {{ background:#fff; border:1px solid #e6e6e6; border-radius:14px; padding:14px; }}
      table {{ width:100%; border-collapse:collapse; }}
      th, td {{ padding:10px; border-bottom:1px solid #eee; text-align:left; }}
      th {{ font-size:12px; color:#666; text-transform:uppercase; letter-spacing:.03em; }}
      a {{ color:#bbb; text-decoration:none; }}
      .btn {{ padding:10px 12px; border-radius:12px; background:#111; color:#fff; text-decoration:none; }}
    </style></head>
    <body>
      <div class="topbar">
        <div style="font-weight:700;">AxleFlow — Fuel</div>
        <div><a href="/app" style="color:#bbb;">Dashboard</a> • <a href="/app/loads" style="color:#bbb;">Loads</a> • <a href="/app/expenses" style="color:#bbb;">Expenses</a></div>
      </div>
      <div class="wrap">
        <div style="margin-bottom:12px;">
          <a class="btn" href="/app/fuel/new">Add Fuel</a>
        </div>
        <div class="card">
          <h3 style="margin-top:0;">Fuel Transactions (company_id={company_id})</h3>
          <table>
            <thead>
              <tr>
                <th>ID</th><th>Date</th><th>State</th><th>Card</th><th>Assigned</th><th style="text-align:right;">Gallons</th><th style="text-align:right;">Total Cost</th><th>Vendor</th>
              </tr>
            </thead>
            <tbody>
              {rows if rows else '<tr><td colspan="8">No fuel transactions found</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>
    </body></html>
    """)

@router.get("/app/fuel/new", response_class=HTMLResponse)
def fuel_new_page(request: Request):
    if not require_login(request):
        return RedirectResponse(url="/login", status_code=303)

    return HTMLResponse("""
    <html><head><title>Add Fuel</title>
    <style>
      body { font-family: Arial, sans-serif; background:#fafafa; margin:0; }
      .topbar { background:#111; color:#fff; padding:16px 24px; display:flex; justify-content:space-between; }
      .wrap { padding:24px; max-width:800px; margin:0 auto; }
      .card { background:#fff; border:1px solid #e6e6e6; border-radius:14px; padding:14px; }
      label { display:block; margin-top:12px; color:#444; font-size:12px; }
      input, select { width:100%; padding:10px; border:1px solid #ddd; border-radius:10px; margin-top:6px; }
      button { margin-top:14px; padding:10px 14px; border:0; border-radius:12px; background:#111; color:#fff; cursor:pointer; }
      a { color:#bbb; text-decoration:none; }
      .row { display:grid; grid-template-columns: 1fr 1fr; gap:12px; }
      @media(max-width:800px){ .row{grid-template-columns:1fr;} }
    </style></head>
    <body>
      <div class="topbar">
        <div style="font-weight:700;">AxleFlow — Add Fuel</div>
        <div><a href="/app/fuel">Back to Fuel</a></div>
      </div>

      <div class="wrap">
        <div class="card">
          <form method="post" action="/app/fuel/new">
            <label>Date (M/D/YY) or (M/D/YY H:MM AM)</label>
            <input name="tx_dt" placeholder="2/5/25 or 2/5/25 8:00 AM" required />

            <div class="row">
              <div>
                <label>State (2 letters)</label>
                <input name="state" placeholder="TX" required />
              </div>
              <div>
                <label>Fuel Card Number (optional)</label>
                <input name="fuel_card_number" placeholder="CARD-1001" />
              </div>
            </div>

            <div class="row">
              <div>
                <label>Gallons</label>
                <input name="gallons" type="number" step="0.001" required />
              </div>
              <div>
                <label>Total Cost</label>
                <input name="total_cost" type="number" step="0.01" required />
              </div>
            </div>

            <label>Vendor Name</label>
            <input name="vendor_name" required />

            <label>Notes (optional)</label>
            <input name="notes" />

            <button type="submit">Create Fuel Transaction</button>
          </form>
        </div>
      </div>
    </body></html>
    """)

@router.post("/app/fuel/new")
async def fuel_new_action(request: Request, db: Session = Depends(get_db)):
    if not require_login(request):
        return RedirectResponse(url="/login", status_code=303)

    form = await request.form()
    company_id = int(request.session.get("company_id"))
    user_id = int(request.session.get("user_id"))

    try:
        tx_dt = parse_dt_user(str(form.get("tx_dt") or ""))
    except Exception as e:
        return HTMLResponse(f"<p>{e}</p><p><a href='/app/fuel/new'>Back</a></p>", status_code=422)

    state = str(form.get("state") or "").strip().upper()
    fuel_card_number = str(form.get("fuel_card_number") or "").strip() or None
    gallons = float(form.get("gallons") or 0)
    total_cost = float(form.get("total_cost") or 0)
    vendor_name = str(form.get("vendor_name") or "").strip()
    notes = str(form.get("notes") or "").strip() or None

    # Draft container
    draft = Draft(
        company_id=company_id,
        draft_type="fuel",
        status="draft",
        created_by_user_id=user_id,
        updated_by_user_id=user_id,
        source="manual",
        source_ref=None
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)

    # FuelDraft typed
    fd = FuelTransactionDraft(
        draft_id=draft.id,
        fuel_card_number=fuel_card_number,
        transaction_datetime=tx_dt,
        state=state,
        gallons=gallons,
        total_cost=total_cost,
        vendor_name=vendor_name,
        notes=notes,
        assignment_context_type=None,
        assignment_context_id=None
    )
    db.add(fd)
    db.commit()
    db.refresh(fd)

    # Review gate checks (minimum required)
    missing = []
    if not fd.transaction_datetime: missing.append("transaction_datetime")
    if not fd.state: missing.append("state")
    if fd.gallons is None: missing.append("gallons")
    if fd.total_cost is None: missing.append("total_cost")
    if missing:
        return HTMLResponse(f"<p>Missing required fields: {missing}</p><p><a href='/app/fuel/new'>Back</a></p>", status_code=422)

    draft.status = "reviewing"
    db.commit()

    # Submit -> final FuelTransaction (auto-assign from fuel card if exists)
    assignment_type = None
    assignment_id = None
    if fuel_card_number:
        card = db.query(FuelCard).filter(
            FuelCard.company_id == company_id,
            FuelCard.card_number == fuel_card_number
        ).first()
        if card and card.assigned_to_type and card.assigned_to_id:
            assignment_type = card.assigned_to_type
            assignment_id = card.assigned_to_id

    tx = FuelTransaction(
        company_id=company_id,
        fuel_card_number=fuel_card_number,
        transaction_datetime=tx_dt,
        state=state,
        gallons=gallons,
        total_cost=total_cost,
        assignment_context_type=assignment_type,
        assignment_context_id=assignment_id,
        vendor_name=vendor_name,
        notes=notes
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)

    draft.status = "submitted"
    draft.submitted_by_user_id = user_id
    draft.submitted_at = datetime.utcnow()
    draft.target_entity_type = "fuel_transaction"
    draft.target_entity_id = tx.id
    db.commit()

    return RedirectResponse(url="/app/fuel", status_code=303)



