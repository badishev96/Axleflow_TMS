from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.expense import Expense

router = APIRouter()

def require_login(request: Request):
    return bool(request.session.get("user_id"))

def money(x):
    return "$" + format(float(x), ",.2f")

def fmt_date(dt):
    try:
        s = str(dt)
        y = s[2:4]
        mm = s[5:7]
        dd = s[8:10]
        if " " in s:
            t = s.split(" ")[1][:5]
            return f"{mm}/{dd}/{y} {t}"
        return f"{mm}/{dd}/{y}"
    except Exception:
        return str(dt)

def fmt_anchor(anchor_type, anchor_id):
    if not anchor_type or anchor_id is None:
        return ""
    at = anchor_type.lower()
    if at == "truck":
        return f"Truck #{anchor_id}"
    if at == "load":
        return f"Load #{anchor_id}"
    if at == "driver":
        return f"Driver #{anchor_id}"
    return f"{anchor_type} #{anchor_id}"

@router.get("/app/expenses", response_class=HTMLResponse)
def expenses_ui(request: Request, db: Session = Depends(get_db)):
    if not require_login(request):
        return RedirectResponse(url="/login", status_code=303)

    company_id = int(request.session.get("company_id"))
    cat = request.query_params.get("cat") or "all"
    show_more = request.query_params.get("more") == "1"

    top = ["all", "fuel", "maintenance", "tolls", "permits", "escort", "other"]

    cats = db.query(Expense.expense_category).filter(
        Expense.company_id == company_id
    ).distinct().all()

    all_cats = sorted([c[0] for c in cats if c and c[0]])
    extra = [c for c in all_cats if c not in top]

    q = db.query(Expense).filter(Expense.company_id == company_id)
    if cat != "all":
        q = q.filter(Expense.expense_category == cat)

    items = q.order_by(Expense.id.desc()).limit(300).all()

    def tab(label, value):
        active = "active" if cat == value else ""
        return f'<a class="tab {active}" href="/app/expenses?cat={value}&more={"1" if show_more else "0"}">{label}</a>'

    tabs = "".join([
        tab("All", "all"),
        tab("Fuel", "fuel"),
        tab("Maintenance", "maintenance"),
        tab("Tolls", "tolls"),
        tab("Permits", "permits"),
        tab("Escort", "escort"),
        tab("Other", "other"),
    ])

    more_link = ""
    if extra:
        if show_more:
            more_link = f'<a class="more" href="/app/expenses?cat={cat}&more=0">Hide</a>'
        else:
            more_link = f'<a class="more" href="/app/expenses?cat={cat}&more=1">More…</a>'

    more_html = ""
    if show_more and extra:
        chips = "".join(
            f'<a class="chip" href="/app/expenses?cat={c}&more=1">{c}</a>'
            for c in extra
        )
        more_html = f'''
        <div class="more-box">
          <div class="muted">More categories (includes custom):</div>
          <div class="chips">{chips}</div>
        </div>
        '''

    rows = ""
    for e in items:
        rows += f'''
        <tr>
          <td class="id"><a href="/app/expenses/{e.id}" target="_blank">{e.id}</a></td>
          <td>{fmt_date(e.expense_date)}</td>
          <td class="cat">{e.expense_category}</td>
          <td>{e.vendor_name or ""}</td>
          <td class="amt">{money(e.amount)} {e.currency}</td>
          <td class="anchor">{fmt_anchor(e.anchor_type, e.anchor_id)}</td>
        </tr>
        '''

    return HTMLResponse(f'''
    <html>
    <head>
      <title>AxleFlow — Expenses</title>
      <style>
        body {{ font-family: Arial; background:#0b0b0b; margin:0; }}
        .topbar {{ background:#111;color:#fff;padding:16px 24px;display:flex;justify-content:space-between; }}
        .wrap {{ max-width:1200px;margin:0 auto;padding:24px; }}
        .card {{ background:#fff;border-radius:18px;padding:16px; }}
        .tabs {{ display:flex;gap:8px;flex-wrap:wrap; }}
        .tab {{ padding:8px 12px;border-radius:12px;border:1px solid #ddd;background:#f5f5f5;text-decoration:none;color:#111;font-weight:600;font-size:13px; }}
        .tab.active {{ background:#111;color:#fff;border-color:#111; }}
        .more {{ margin-left:auto;color:#1a73e8;font-weight:600;text-decoration:none; }}
        .actions {{ margin:12px 0;display:flex;justify-content:space-between; }}
        .btn {{ background:#111;color:#fff;padding:10px 14px;border-radius:12px;text-decoration:none;font-weight:700; }}
        table {{ width:100%;border-collapse:collapse; }}
        th, td {{ padding:10px;border-bottom:1px solid #eee; }}
        th {{ color:#666;font-size:12px;text-transform:uppercase; }}
        td.id a {{ color:#1a73e8;font-weight:700;text-decoration:none; }}
        td.amt {{ text-align:right;font-weight:700; }}
        .more-box {{ background:#fafafa;border:1px solid #eee;border-radius:14px;padding:12px;margin-top:12px; }}
        .chips {{ display:flex;gap:8px;flex-wrap:wrap;margin-top:8px; }}
        .chip {{ border:1px solid #ddd;border-radius:999px;padding:6px 10px;text-decoration:none;color:#111;font-size:13px; }}
      </style>
    </head>
    <body>
      <div class="topbar">
        <div><b>AxleFlow — Expenses</b></div>
        <div><a href="/app" style="color:#bbb;">Dashboard</a></div>
      </div>

      <div class="wrap">
        <div class="card">
          <div class="tabs">{tabs}{more_link}</div>
          {more_html}
          <div class="actions">
            <a class="btn" href="/app/expenses/new">Add Expense</a>
            <div class="muted">Fuel, maintenance, tolls, permits, escort, and custom expenses — all traceable.</div>
          </div>

          <table>
            <thead>
              <tr>
                <th>ID</th><th>Date</th><th>Category</th><th>Vendor</th>
                <th style="text-align:right;">Amount</th><th>Anchor</th>
              </tr>
            </thead>
            <tbody>
              {rows if rows else "<tr><td colspan=6>No expenses found</td></tr>"}
            </tbody>
          </table>
        </div>
      </div>
    </body>
    </html>
    ''')
