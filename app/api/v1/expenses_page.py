from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import get_db

from app.models.expense import Expense
from app.models.draft import Draft
from app.models.expense_draft import ExpenseDraft

router = APIRouter()

def money(x): return f"${float(x):,.2f}"

def require_login(request: Request):
    return bool(request.session.get("user_id"))

@router.get("/app/expenses", response_class=HTMLResponse)
def expenses_page(request: Request, db: Session = Depends(get_db)):
    if not require_login(request):
        return RedirectResponse(url="/login", status_code=303)

    company_id = int(request.session.get("company_id"))
    expenses = db.query(Expense).filter(Expense.company_id == company_id).order_by(Expense.id.desc()).all()

    rows = ""
    for e in expenses:
        rows += f"""
        <tr>
          <td><a href="/app/expenses/{e.id}" target="_blank">{e.id}</a></td>
          <td>{e.expense_date}</td>
          <td>{e.expense_category}</td>
          <td>{e.anchor_type}:{e.anchor_id}</td>
          <td>{e.vendor_name}</td>
          <td style="text-align:right;">{money(e.amount)}</td>
        </tr>
        """

    return HTMLResponse(f"""
    <html><head><title>AxleFlow — Expenses</title>
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
        <div style="font-weight:700;">AxleFlow — Expenses</div>
        <div><a href="/app" style="color:#bbb;">Dashboard</a> • <a href="/app/loads" style="color:#bbb;">Loads</a></div>
      </div>
      <div class="wrap">
        <div style="margin-bottom:12px;">
          <a class="btn" href="/app/expenses/new">Add Expense</a>
        </div>
        <div class="card">
          <h3 style="margin-top:0;">Expenses (company_id={company_id})</h3>
          <table>
            <thead>
              <tr>
                <th>ID</th><th>Date</th><th>Category</th><th>Anchor</th><th>Vendor</th><th style="text-align:right;">Amount</th>
              </tr>
            </thead>
            <tbody>
              {rows if rows else '<tr><td colspan="6">No expenses found</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>
    </body></html>
    """)

@router.get("/app/expenses/new", response_class=HTMLResponse)
def expenses_new_page(request: Request):
    if not require_login(request):
        return RedirectResponse(url="/login", status_code=303)

    return HTMLResponse("""
    <html><head><title>Add Expense</title>
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
        <div style="font-weight:700;">AxleFlow — Add Expense</div>
        <div><a href="/app/expenses">Back to Expenses</a></div>
      </div>

      <div class="wrap">
        <div class="card">
          <form method="post" action="/app/expenses/new">
            <label>Date (M/D/YY) or (M/D/YY H:MM AM)</label>
            <input name="expense_dt" placeholder="2/5/25 or 2/5/25 8:00 AM" required />

            <div class="row">
              <div>
                <label>Category</label>
                <select name="expense_category">
                  <option value="fuel">fuel</option>
                  <option value="maintenance">maintenance</option>
                  <option value="toll">toll</option>
                  <option value="lumper">lumper</option>
                  <option value="other">other</option>
                </select>
              </div>
              <div>
                <label>Amount</label>
                <input name="amount" type="number" step="0.01" required />
              </div>
            </div>

            <div class="row">
              <div>
                <label>Anchor Type</label>
                <select name="anchor_type">
                  <option value="truck">truck</option>
                  <option value="load">load</option>
                  <option value="company">company</option>
                </select>
              </div>
              <div>
                <label>Anchor ID</label>
                <input name="anchor_id" type="number" required />
              </div>
            </div>

            <label>Vendor Name</label>
            <input name="vendor_name" required />

            <label>Notes (optional)</label>
            <input name="notes" />

            <button type="submit">Create Expense</button>
          </form>
        </div>
      </div>
    </body></html>
    """)

def parse_dt_user(s: str):
    s = (s or "").strip()
    # Accept: M/D/YY  OR  M/D/YY H:MM AM/PM
    fmts = ["%m/%d/%y", "%m/%d/%y %I:%M %p"]
    for f in fmts:
        try:
            dt = datetime.strptime(s, f)
            # If user provided only date, default to 00:00 per your lock
            if f == "%m/%d/%y":
                return datetime(dt.year, dt.month, dt.day, 0, 0)
            return dt
        except ValueError:
            pass
    raise ValueError("Use M/D/YY or M/D/YY H:MM AM (example: 2/5/25 or 2/5/25 8:00 AM)")

@router.post("/app/expenses/new")
async def expenses_new_action(request: Request, db: Session = Depends(get_db)):
    if not require_login(request):
        return RedirectResponse(url="/login", status_code=303)

    form = await request.form()
    company_id = int(request.session.get("company_id"))
    user_id = int(request.session.get("user_id"))

    try:
        expense_dt = parse_dt_user(str(form.get("expense_dt") or ""))
    except Exception as e:
        return HTMLResponse(f"<p>{e}</p><p><a href='/app/expenses/new'>Back</a></p>", status_code=422)

    expense_category = str(form.get("expense_category") or "").strip()
    amount = float(form.get("amount") or 0)
    anchor_type = str(form.get("anchor_type") or "").strip()
    anchor_id = int(form.get("anchor_id") or 0)
    vendor_name = str(form.get("vendor_name") or "").strip()
    notes = str(form.get("notes") or "").strip() or None

    # Draft container
    draft = Draft(
        company_id=company_id,
        draft_type="expense",
        status="draft",
        created_by_user_id=user_id,
        updated_by_user_id=user_id,
        source="manual",
        source_ref=None
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)

    # ExpenseDraft typed
    ed = ExpenseDraft(
        draft_id=draft.id,
        expense_date=expense_dt,
        amount=amount,
        currency="USD",
        expense_category=expense_category,
        anchor_type=anchor_type,
        anchor_id=anchor_id,
        vendor_name=vendor_name,
        reference_number=None,
        notes=notes
    )
    db.add(ed)
    db.commit()
    db.refresh(ed)

    # Review gate checks (minimum required)
    missing = []
    if not ed.expense_date: missing.append("expense_date")
    if ed.amount is None: missing.append("amount")
    if not ed.expense_category: missing.append("expense_category")
    if not ed.anchor_type: missing.append("anchor_type")
    if ed.anchor_id is None: missing.append("anchor_id")
    if not ed.vendor_name: missing.append("vendor_name")
    if missing:
        return HTMLResponse(f"<p>Missing required fields: {missing}</p><p><a href='/app/expenses/new'>Back</a></p>", status_code=422)

    draft.status = "reviewing"
    db.commit()

    # Submit -> final Expense
    expense = Expense(
        company_id=company_id,
        expense_date=ed.expense_date,
        amount=ed.amount,
        currency=ed.currency,
        expense_category=ed.expense_category,
        anchor_type=ed.anchor_type,
        anchor_id=ed.anchor_id,
        vendor_name=ed.vendor_name,
        reference_number=ed.reference_number,
        notes=ed.notes
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)

    draft.status = "submitted"
    draft.submitted_by_user_id = user_id
    draft.submitted_at = datetime.utcnow()
    draft.target_entity_type = "expense"
    draft.target_entity_id = expense.id
    db.commit()

    return RedirectResponse(url="/app/expenses", status_code=303)

@router.get("/app/expenses/{expense_id}", response_class=HTMLResponse)
def expense_detail(expense_id: int, request: Request, db: Session = Depends(get_db)):
    if not require_login(request):
        return RedirectResponse(url="/login", status_code=303)

    company_id = int(request.session.get("company_id"))
    e = db.query(Expense).filter(Expense.company_id == company_id, Expense.id == expense_id).first()
    if not e:
        return HTMLResponse("<p>Expense not found</p>", status_code=404)

    def money(x): return "$" + format(float(x), ",.2f")

    return HTMLResponse(f"""
    <html>
    <head>
      <title>Expense {e.id}</title>
      <style>
        body {{ font-family: Arial, sans-serif; margin:40px; background:#fafafa; }}
        .card {{ background:#fff; border:1px solid #e6e6e6; border-radius:14px; padding:14px; max-width:700px; }}
        .row {{ display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #eee; }}
        .row:last-child {{ border-bottom:none; }}
        .label {{ color:#666; }}
        a {{ color:#1a73e8; text-decoration:none; }}
      </style>
    </head>
    <body>
      <h2>Expense #{e.id}</h2>
      <div class="card">
        <div class="row"><div class="label">Date</div><div>{e.expense_date}</div></div>
        <div class="row"><div class="label">Category</div><div>{e.expense_category}</div></div>
        <div class="row"><div class="label">Vendor</div><div>{e.vendor_name or ""}</div></div>
        <div class="row"><div class="label">Amount</div><div>{money(e.amount)} {e.currency}</div></div>
        <div class="row"><div class="label">Anchor</div><div>{e.anchor_type}:{e.anchor_id}</div></div>
        <div class="row"><div class="label">Reference</div><div>{e.reference_number or ""}</div></div>
        <div class="row"><div class="label">Notes</div><div>{e.notes or ""}</div></div>
        <div class="row"><div class="label">Created</div><div>{e.created_at}</div></div>
      </div>

      <p><a href="/app/expenses">← Back to Expenses</a></p>
    </body>
    </html>
    """)

