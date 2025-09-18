from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from fastapi import HTTPException, status

from ..db import get_db
from .. import models, schemas
from ..auth.security import get_current_user
from typing import List

router = APIRouter(prefix="/categories", tags=["categories"])

@router.post("", response_model=schemas.CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    data: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # preventing duplicate names
    exists = (
        db.query(models.Category)
        .filter(models.Category.user_id == current_user.id, models.Category.name == data.name)
        .first()
    )
    if exists:
        raise HTTPException(status_code=400, detail="Category with this name already exists")

    cat = models.Category(name=data.name, user_id=current_user.id)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat

@router.get("", response_model=List[schemas.CategoryRead])
def list_categories(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    rows = (
        db.query(models.Category)
        .filter(models.Category.user_id == current_user.id)
        .order_by(models.Category.id.asc())
        .all()
    )
    return rows
