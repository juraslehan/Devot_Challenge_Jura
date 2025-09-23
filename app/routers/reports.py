from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import func

from ..db import get_db
from .. import models, schemas
from ..auth.security import get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/balance", response_model=schemas.BalanceRead)
def balance(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # sum of the users expenses
    total_expenses = (
        db.query(func.coalesce(func.sum(models.Expense.amount), 0))
        .filter(models.Expense.user_id == current_user.id)
        .scalar()
    )

    # starting balance
    starting = current_user.starting_balance

    return schemas.BalanceRead(
        starting_balance=starting,
        total_expenses=total_expenses,
        balance=Decimal(starting) - Decimal(total_expenses),
    )

def _period_range(period: str, year: int, month: Optional[int] = None, quarter: Optional[int] = None):
    if period == "month":
        if not month:
            raise ValueError("Month is required when period=month.")
        from calendar import monthrange
        start = date(year, month, 1)
        last_day = monthrange(year, month)[1]
        end = date(year, month, last_day)
        return start, end

    if period == "quarter":
        if not quarter or quarter not in (1, 2, 3, 4):
            raise ValueError("Quarter must be 1,2,3,4 when period=quarter.")
        start_month = (quarter - 1) * 3 + 1
        start = date(year, start_month, 1)
        end_month = start_month + 2
        from calendar import monthrange
        last_day = monthrange(year, end_month)[1]
        end = date(year, end_month, last_day)
        return start, end

    if period == "year":
        return date(year, 1, 1), date(year, 12, 31)

    raise ValueError("Period must be one of: month, quarter, year.")


@router.get("/summary", response_model=schemas.ReportSummary)
def summary(
    period: str,                          # month, quarter, year
    year: Optional[int] = None,           # default is current year
    month: Optional[int] = None,          # required if period=month
    quarter: Optional[int] = None,        # required if period=quarter
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    today = date.today()
    year = year or today.year
    try:
        start, end = _period_range(period, year, month, quarter)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # totals per category
    rows = (
        db.query(
            models.Category.id.label("category_id"),
            models.Category.name.label("name"),
            func.coalesce(func.sum(models.Expense.amount), 0).label("total"),
        )
        .join(models.Category, models.Category.id == models.Expense.category_id)
        .filter(
            models.Expense.user_id == current_user.id,
            models.Expense.date >= start,
            models.Expense.date <= end,
        )
        .group_by(models.Category.id, models.Category.name)
        .order_by(func.sum(models.Expense.amount).desc())
        .all()
    )

    # total for the period
    period_total = sum((r.total for r in rows), Decimal("0"))

    return schemas.ReportSummary(
        period=period,
        start=start,
        end=end,
        total_expenses=period_total,
        category_totals=[
            schemas.CategoryTotal(category_id=r.category_id, name=r.name, total=r.total) for r in rows
        ],
    )
