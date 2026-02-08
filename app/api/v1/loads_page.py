from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.load import Load
from app.models.expense import Expense

router = APIRouter()

def require_login(request: Request):
    return bool(request.session.get("user_id"))

def money(x):
    return "$" + format(float(x), ",.2f")

@router.get("/app/loads", response_class=HTMLResponse)
def loads_list(request: Request, db: Session = Depends(get_db)):
    if not require_login(request):
        return RedirectResponse(url="/login", status_code=303)

    company_id = int(request.session.get("company_id"))
    loads = db.query(Load).filter(Load.company_id == company_id).order_by(Load.id.desc()).limit(200).all()

    rows = ""
    for l in loads:
        rev = float(l.rate_amount or 0)
        miles = float(l.total_miles or 0)
        rpm = (rev / miles) if miles > 0 else None
        rows += f"<tr><td><a href='/app/loads/{l.id}'>{l.id}</a></td><td>{l.truck_id or ''}</td><td style='text-align:right;'>{money(rev)}</td><td style='text-align:right;'>{miles:,.2f}</td><td style='text-align:right;'>{('N/A' if rpm is None else '$'+format(float(rpm),',.3f'))}</td></tr>"

    return HTMLResponse(f"""
    <html>
    <head>
      <title>AxleFlow — Loads</title>
      <style>
        body {{ font-family: Arial; margin:0; background:#0b0b0b; }}
        .topbar {{ background:#111; color:#fff; padding:16px 24px; display:flex; justify-content:space-between; }}
        .topbar a {{ color:#bbb; text-decoration:none; }}
        .wrap {{ max-width:1100px; margin:0 auto; padding:24px; }}
        .card {{ background:#fff; border-radius:18px; padding:18px; box-shadow:0 10px 30px rgba(0,0,0,.18); }}
        table {{ width:100%; border-collapse:collapse; margin-top:12px; }}
        th, td {{ padding:10px; border-bottom:1px solid #eee; }}
        th {{ color:#666; font-size:12px; text-transform:uppercase; letter-spacing:.03em; text-align:left; }}
        a {{ color:#1a73e8; text-decoration:none; font-weight:800; }}
      </style>
    </head>
    <body>
      <div class="topbar">
        <div style="font-weight:800;">AxleFlow — Loads</div>
        <div><a href="/app">Dashboard</a></div>
      </div>

      <div class="wrap">
        <div class="card">
          <table>
            <thead>
              <tr>
                <th>ID</th><th>Truck</th><th style="text-align:right;">Revenue</th><th style="text-align:right;">Miles</th><th style="text-align:right;">Rev/Mile</th>
              </tr>
            </thead>
            <tbody>
              {rows if rows else "<tr><td colspan='5'>No loads</td></tr>"}
            </tbody>
          </table>
        </div>
      </div>
    </body>
    </html>
    """)

@router.get("/app/loads/{load_id}", response_class=HTMLResponse)
def load_detail(request: Request, load_id: int, db: Session = Depends(get_db)):
    if not require_login(request):
        return RedirectResponse(url="/login", status_code=303)

    company_id = int(request.session.get("company_id"))
    load = db.query(Load).filter(Load.company_id == company_id, Load.id == load_id).first()
    if not load:
        return HTMLResponse("<p>Load not found</p>", status_code=404)

    rev = float(load.rate_amount or 0)
    miles = float(load.total_miles or 0)

    # Basic expense list for this load
    exps = db.query(Expense).filter(Expense.company_id == company_id, Expense.anchor_type == "load", Expense.anchor_id == load.id).order_by(Expense.id.desc()).all()
    exp_rows = ""
    for e in exps:
        exp_rows += f"<tr><td><a href='/app/expenses/{e.id}' target='_blank'>{e.id}</a></td><td>{e.expense_category}</td><td>{e.vendor_name or ''}</td><td style='text-align:right;'>{money(e.amount)}</td></tr>"

    return HTMLResponse(f"""
    <html>
    <head>
      <title>Load {load.id}</title>
      <style>
        body {{ font-family: Arial; margin:0; background:#0b0b0b; }}
        .topbar {{ background:#111; color:#fff; padding:16px 24px; display:flex; justify-content:space-between; }}
        .topbar a {{ color:#bbb; text-decoration:none; }}
        .wrap {{ max-width:1100px; margin:0 auto; padding:24px; }}
        .card {{ background:#fff; border-radius:18px; padding:18px; box-shadow:0 10px 30px rgba(0,0,0,.18); margin-bottom:12px; }}
        .btn {{ display:inline-block; padding:10px 14px; border-radius:12px; background:#111; color:#fff; text-decoration:none; font-weight:800; margin-right:10px; }}
        table {{ width:100%; border-collapse:collapse; margin-top:12px; }}
        th, td {{ padding:10px; border-bottom:1px solid #eee; }}
        th {{ color:#666; font-size:12px; text-transform:uppercase; letter-spacing:.03em; text-align:left; }}
        a {{ color:#1a73e8; text-decoration:none; font-weight:800; }}
      </style>
    </head>
    <body>
      <div class="topbar">
        <div style="font-weight:800;">Load #{load.id}</div>
        <div><a href="/app/loads">Back to Loads</a></div>
      </div>

      <div class="wrap">
        <div class="card">
          <a class="btn" href="/app/loads/{load.id}/analytics">Analytics</a>
          <a class="btn" href="/app/expenses/new?anchor_type=load&anchor_id={load.id}">Add Expense</a>
        </div>

        <div class="card">
          <h3 style="margin-top:0;">Summary</h3>
          <p><b>Truck:</b> {load.truck_id or ''}</p>
          <p><b>Revenue:</b> {money(rev)}</p>
          <p><b>Miles:</b> {miles:,.2f}</p>
        </div>

        <div class="card">
          <h3 style="margin-top:0;">Load Expenses</h3>
          <table>
            <thead><tr><th>ID</th><th>Category</th><th>Vendor</th><th style="text-align:right;">Amount</th></tr></thead>
            <tbody>{exp_rows if exp_rows else "<tr><td colspan='4'>No load expenses</td></tr>"}</tbody>
          </table>
        </div>
      </div>
    </body>
    </html>
    """)
