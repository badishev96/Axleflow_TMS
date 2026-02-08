from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.load import Load
from app.models.expense import Expense
from app.models.fuel_transaction import FuelTransaction
from app.models.settlement import Settlement

router = APIRouter()

def require_login(request: Request):
    if not request.session.get("user_id"):
        raise HTTPException(status_code=401, detail="Not logged in")
    return request.session

def get_period_bounds(range_name: str):
    now = datetime.utcnow()
    if range_name == "week":
        start = now - timedelta(days=7)
    elif range_name == "month":
        start = now - timedelta(days=30)
    elif range_name == "quarter":
        start = now - timedelta(days=90)
    elif range_name == "year":
        start = now - timedelta(days=365)
    else:
        raise HTTPException(status_code=422, detail="range must be one of: week, month, quarter, year")
    end = now
    prev_start = start - (end - start)
    prev_end = start
    return start, end, prev_start, prev_end

def pct_change(curr, prev):
    if prev == 0 or prev is None:
        return None
    return (curr - prev) / prev

def build_summary(company_id: int, start, end, db: Session, truck_id: int | None = None):
    load_filter = [Load.company_id == company_id, Load.created_at >= start, Load.created_at < end]
    if truck_id is not None:
        load_filter.append(Load.truck_id == truck_id)

    load_count = db.query(func.count(Load.id)).filter(*load_filter).scalar() or 0
    revenue = db.query(func.coalesce(func.sum(Load.rate_amount), 0)).filter(*load_filter).scalar() or 0
    miles = db.query(func.coalesce(func.sum(Load.total_miles), 0)).filter(*load_filter).scalar() or 0

    if truck_id is None:
        expenses = db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
            Expense.company_id == company_id,
            Expense.created_at >= start,
            Expense.created_at < end
        ).scalar() or 0
    else:
        expenses = db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
            Expense.company_id == company_id,
            Expense.anchor_type == "truck",
            Expense.anchor_id == truck_id,
            Expense.created_at >= start,
            Expense.created_at < end
        ).scalar() or 0

    if truck_id is None:
        fuel = db.query(func.coalesce(func.sum(FuelTransaction.total_cost), 0)).filter(
            FuelTransaction.company_id == company_id,
            FuelTransaction.created_at >= start,
            FuelTransaction.created_at < end
        ).scalar() or 0
    else:
        fuel = db.query(func.coalesce(func.sum(FuelTransaction.total_cost), 0)).filter(
            FuelTransaction.company_id == company_id,
            FuelTransaction.assignment_context_type == "truck",
            FuelTransaction.assignment_context_id == truck_id,
            FuelTransaction.created_at >= start,
            FuelTransaction.created_at < end
        ).scalar() or 0

    if truck_id is None:
        settlements = db.query(func.coalesce(func.sum(Settlement.commission_pool_amount), 0)).filter(
            Settlement.company_id == company_id,
            Settlement.created_at >= start,
            Settlement.created_at < end
        ).scalar() or 0
    else:
        settlements = db.query(func.coalesce(func.sum(Settlement.commission_pool_amount), 0)).filter(
            Settlement.company_id == company_id,
            Settlement.truck_id == truck_id,
            Settlement.created_at >= start,
            Settlement.created_at < end
        ).scalar() or 0

    net_margin = float(revenue) - float(expenses) - float(fuel) - float(settlements)
    profit_per_mile = (net_margin / float(miles)) if float(miles) > 0 else None
    fuel_share = (float(fuel) / float(revenue)) if float(revenue) > 0 else None
    settlement_share = (float(settlements) / float(revenue)) if float(revenue) > 0 else None

    return {
        "loads_count": int(load_count),
        "revenue_total": float(revenue),
        "miles_total": float(miles),
        "expenses_total": float(expenses),
        "fuel_total": float(fuel),
        "settlements_total": float(settlements),
        "net_margin": float(net_margin),
        "profit_per_mile": profit_per_mile,
        "fuel_share": fuel_share,
        "settlement_share": settlement_share,
    }

def build_response(company_id: int, range: str, db: Session, truck_id: int | None = None):
    start, end, prev_start, prev_end = get_period_bounds(range)

    curr = build_summary(company_id, start, end, db, truck_id=truck_id)
    prev = build_summary(company_id, prev_start, prev_end, db, truck_id=truck_id)

    deltas = {
        "revenue_pct_change": pct_change(curr["revenue_total"], prev["revenue_total"]),
        "net_margin_pct_change": pct_change(curr["net_margin"], prev["net_margin"]),
        "profit_per_mile_pct_change": pct_change(curr["profit_per_mile"], prev["profit_per_mile"]) if (curr["profit_per_mile"] is not None and prev["profit_per_mile"] not in [None, 0]) else None,
        "fuel_share_change": (curr["fuel_share"] - prev["fuel_share"]) if (curr["fuel_share"] is not None and prev["fuel_share"] is not None) else None,
        "settlement_share_change": (curr["settlement_share"] - prev["settlement_share"]) if (curr["settlement_share"] is not None and prev["settlement_share"] is not None) else None,
    }

    warnings = []
    if curr["net_margin"] < 0:
        warnings.append("NEGATIVE_MARGIN")
    if deltas["profit_per_mile_pct_change"] is not None and deltas["profit_per_mile_pct_change"] < 0:
        warnings.append("PROFIT_PER_MILE_DOWN")
    if deltas["net_margin_pct_change"] is not None and deltas["net_margin_pct_change"] < 0:
        warnings.append("NET_MARGIN_DOWN")
    if deltas["fuel_share_change"] is not None and deltas["fuel_share_change"] > 0:
        warnings.append("FUEL_SHARE_UP")
    if deltas["settlement_share_change"] is not None and deltas["settlement_share_change"] > 0:
        warnings.append("SETTLEMENT_SHARE_UP")

    if prev["revenue_total"] == 0 and curr["revenue_total"] > 0:
        warnings.append("INSUFFICIENT_HISTORY_FOR_TRENDS")

    return {
        "company_id": company_id,
        "truck_id": truck_id,
        "range": range,
        "current_period": {
            "start": start.isoformat() + "Z",
            "end": end.isoformat() + "Z",
            **curr
        },
        "previous_period": {
            "start": prev_start.isoformat() + "Z",
            "end": prev_end.isoformat() + "Z",
            **prev
        },
        "deltas": deltas,
        "warnings": warnings
    }

@router.get("/dashboard/{company_id}")
def company_dashboard(company_id: int, range: str = "month", request: Request = None, db: Session = Depends(get_db)):
    require_login(request)
    return build_response(company_id, range, db, truck_id=None)

@router.get("/dashboard/truck/{truck_id}")
def truck_dashboard(truck_id: int, company_id: int = 2, range: str = "month", request: Request = None, db: Session = Depends(get_db)):
    require_login(request)
    return build_response(company_id, range, db, truck_id=truck_id)

@router.get("/dashboard/driver/{driver_id}")
def driver_dashboard(driver_id: int, company_id: int = 2, range: str = "month", request: Request = None, db: Session = Depends(get_db)):
    require_login(request)

    start, end, prev_start, prev_end = get_period_bounds(range)

    def earnings(s, e):
        primary_sum = db.query(func.coalesce(func.sum(Settlement.primary_driver_amount), 0)).filter(
            Settlement.company_id == company_id,
            Settlement.primary_driver_id == driver_id,
            Settlement.created_at >= s,
            Settlement.created_at < e
        ).scalar() or 0

        secondary_sum = db.query(func.coalesce(func.sum(Settlement.secondary_driver_amount), 0)).filter(
            Settlement.company_id == company_id,
            Settlement.secondary_driver_id == driver_id,
            Settlement.created_at >= s,
            Settlement.created_at < e
        ).scalar() or 0

        count = db.query(func.count(Settlement.id)).filter(
            Settlement.company_id == company_id,
            Settlement.created_at >= s,
            Settlement.created_at < e,
            ((Settlement.primary_driver_id == driver_id) | (Settlement.secondary_driver_id == driver_id))
        ).scalar() or 0

        total = float(primary_sum) + float(secondary_sum)
        return int(count), float(primary_sum), float(secondary_sum), float(total)

    c_count, c_primary, c_secondary, c_total = earnings(start, end)
    p_count, p_primary, p_secondary, p_total = earnings(prev_start, prev_end)

    deltas = {
        "earnings_pct_change": pct_change(c_total, p_total),
        "settlements_count_change": (c_count - p_count),
    }

    warnings = []
    if p_total == 0 and c_total > 0:
        warnings.append("INSUFFICIENT_HISTORY_FOR_TRENDS")
    if deltas["earnings_pct_change"] is not None and deltas["earnings_pct_change"] < 0:
        warnings.append("DRIVER_EARNINGS_DOWN")

    return {
        "company_id": company_id,
        "driver_id": driver_id,
        "range": range,
        "current_period": {
            "start": start.isoformat() + "Z",
            "end": end.isoformat() + "Z",
            "settlements_count": c_count,
            "primary_earnings": c_primary,
            "secondary_earnings": c_secondary,
            "total_earnings": c_total,
        },
        "previous_period": {
            "start": prev_start.isoformat() + "Z",
            "end": prev_end.isoformat() + "Z",
            "settlements_count": p_count,
            "primary_earnings": p_primary,
            "secondary_earnings": p_secondary,
            "total_earnings": p_total,
        },
        "deltas": deltas,
        "warnings": warnings
    }
