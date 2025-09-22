from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date

from ..db import get_db
from .. import models, schemas
from ..auth.security import get_current_user

from fastapi import Query

router = APIRouter(prefix="/expenses", tags=["expenses"])

@router.post("", response_model=schemas.ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(
    data: schemas.ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    #category has to exist and belong to this user
    category = (
        db.query(models.Category)
        .filter(models.Category.id == data.category_id, models.Category.user_id == current_user.id)
        .first()
    )
    if not category:
        raise HTTPException(status_code=400, detail="Invalid category")

    expense = models.Expense(
        description=data.description,
        amount=data.amount,
        date=data.date,
        category_id=category.id,
        user_id=current_user.id,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense

@router.get("/{expense_id}", response_model=schemas.ExpenseRead)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    row = (
        db.query(models.Expense)
        .filter(models.Expense.id == expense_id, models.Expense.user_id == current_user.id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Expense not found")
    return row

@router.put("/{expense_id}", response_model=schemas.ExpenseRead)
def update_expense(
    expense_id: int,
    data: schemas.ExpenseCreate,  
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    exp = (
        db.query(models.Expense)
        .filter(models.Expense.id == expense_id, models.Expense.user_id == current_user.id)
        .first()
    )
    if not exp:
        raise HTTPException(status_code=404, detail="Expense not found")

    cat = (
        db.query(models.Category)
        .filter(models.Category.id == data.category_id, models.Category.user_id == current_user.id)
        .first()
    )
    if not cat:
        raise HTTPException(status_code=400, detail="Invalid category")

    exp.description = data.description
    exp.amount = data.amount
    exp.date = data.date
    exp.category_id = data.category_id

    db.commit()
    db.refresh(exp)
    return exp

@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    exp = (
        db.query(models.Expense)
        .filter(models.Expense.id == expense_id, models.Expense.user_id == current_user.id)
        .first()
    )
    if not exp:
        raise HTTPException(status_code=404, detail="Expense not found")

    db.delete(exp)
    db.commit()
    return

@router.get("", response_model=List[schemas.ExpenseRead])
def list_expenses(
    category_id: Optional[int] = Query(None, alias="categoryId"),
    amount_min: Optional[float] = None,
    amount_max: Optional[float] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Expense).filter(models.Expense.user_id == current_user.id)

    if category_id is not None:
        query = query.filter(models.Expense.category_id == category_id)
    if amount_min is not None:
        query = query.filter(models.Expense.amount >= amount_min)
    if amount_max is not None:
        query = query.filter(models.Expense.amount <= amount_max)
    if date_from is not None:
        query = query.filter(models.Expense.date >= date_from)
    if date_to is not None:
        query = query.filter(models.Expense.date <= date_to)
    if q:
        like = f"%{q}%"
        query = query.filter(models.Expense.description.ilike(like))

    rows = query.order_by(models.Expense.date.desc(), models.Expense.id.desc()).all()
    return rows



