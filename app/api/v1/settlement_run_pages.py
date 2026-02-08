from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.settlement_run import SettlementRun
from app.models.settlement_run_load import SettlementRunLoad
from app.models.load import Load

router = APIRouter()

def require_login(request: Request):
    return bool(request.session.get("user_id"))

def money(x):
    return "$" + format(float(x), ",.2f")

@router.get("/app/settlements/run/{run_id}", response_class=HTMLResponse)
def run_view(run_id: int, request: Request, db: Session = Depends(get_db)):
    if not require_login(request):
        return RedirectResponse(url="/login", status_code=303)

    company_id = int(request.session.get("company_id"))
    run = db.query(SettlementRun).filter(SettlementRun.company_id == company_id, SettlementRun.id == run_id).first()
    if not run:
        return HTMLResponse("<p>Run not found</p>", status_code=404)

    rows = db.query(SettlementRunLoad).filter(
        SettlementRunLoad.company_id == company_id,
        SettlementRunLoad.settlement_run_id == run.id
    ).all()

    load_ids = [r.load_id for r in rows]
    loads = db.query(Load).filter(Load.company_id == company_id, Load.id.in_(load_ids)).all()
    load_map = {l.id: l for l in loads}

    total_pay = float(run.total_pay or 0)
    total_gross = float(run.total_gross or 0)

    table_rows = ""
    for r in rows:
        l = load_map.get(r.load_id)
        rev = float(l.rate_amount or 0) if l else 0.0
        miles = float(l.total_miles or 0) if l else 0.0
        pay = float(r.load_pay or 0)

        if run.person_type == "dispatcher" and total_gross > 0:
            share = (rev / total_gross) * 100.0
        elif total_pay > 0:
            share = (pay / total_pay) * 100.0
        else:
            share = 0.0

        # ✅ Load ID clickable
        table_rows += "<tr><td><a href='/app/loads/{}' target='_blank'>{}</a></td><td style='text-align:right;'>{}</td><td style='text-align:right;'>{:,.2f}</td><td style='text-align:right;'>{}</td><td style='text-align:right;'>{:,.1f}%</td></tr>".format(
            r.load_id, r.load_id, money(rev), miles, money(pay), share
        )

    extra = ""
    if run.person_type == "driver" and run.pay_model == "cpm":
        extra += "<p><b>Total Miles Used:</b> {:,.2f}</p>".format(float(run.total_miles or 0))
    if run.person_type == "dispatcher":
        extra += "<p><b>Total Gross Used:</b> {}</p>".format(money(run.total_gross or 0))

    return HTMLResponse(f"""
    <html>
    <head>
      <title>Settlement Run #{run.id}</title>
      <style>
        body {{ font-family: Arial, sans-serif; margin:40px; }}
        table {{ width:100%; max-width:900px; border-collapse:collapse; }}
        th, td {{ padding:10px; border-bottom:1px solid #eee; }}
        th {{ text-align:left; font-size:12px; color:#666; text-transform:uppercase; letter-spacing:.03em; }}
        a {{ color:#1a73e8; text-decoration:none; }}
        .btn {{ display:inline-block; padding:10px 14px; border-radius:10px; background:#111; color:#fff; text-decoration:none; margin-right:8px; cursor:pointer; }}
        .muted {{ color:#666; font-size:12px; }}
        @media print {{
          .no-print {{ display:none; }}
          body {{ margin:20px; }}
        }}
      </style>
    </head>
    <body>
      <h2>Settlement Run #{run.id}</h2>
      <p><b>Type:</b> {run.person_type} • <b>Person:</b> {run.person_id}</p>
      <p><b>Model:</b> {run.pay_model} • <b>Rate:</b> {float(run.rate_value):,.4f}</p>
      <p><b>Total Pay:</b> {money(run.total_pay)}</p>
      {extra}

      <div class="no-print" style="margin:14px 0;">
        <!-- ✅ Real print dialog -->
        <a class="btn" href="#" onclick="window.print();return false;">Print</a>
        <!-- Download PDF already works in your system -->
        <a class="btn" href="/app/settlements/download/{run.id}">Download PDF</a>
      </div>

      <h3>Load Breakdown</h3>
      <div class="muted">Load IDs are clickable. Share % shows contribution.</div>
      <table>
        <thead>
          <tr>
            <th>Load</th>
            <th style="text-align:right;">Revenue</th>
            <th style="text-align:right;">Miles</th>
            <th style="text-align:right;">Pay</th>
            <th style="text-align:right;">Share %</th>
          </tr>
        </thead>
        <tbody>{table_rows if table_rows else "<tr><td colspan='5'>No loads</td></tr>"}</tbody>
      </table>

      <p class="no-print"><a href="/app/settlements">Back</a></p>
    </body>
    </html>
    """)

