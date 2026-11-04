from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/applications", tags=["applications"])


def get_owned(db: Session, application_id: int, user: models.User) -> models.Application:
    row = db.get(models.Application, application_id)
    # Same 404 whether it doesn't exist or belongs to someone else
    if not row or row.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Application not found")
    return row


@router.post("", response_model=schemas.ApplicationOut, status_code=201)
def create_application(
    data: schemas.ApplicationCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    row = models.Application(**data.model_dump(exclude_none=True), owner_id=user.id)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("", response_model=list[schemas.ApplicationOut])
def list_applications(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    query = db.query(models.Application).filter(models.Application.owner_id == user.id)
    if status:
        query = query.filter(models.Application.status == status)
    return query.order_by(models.Application.id.desc()).all()


@router.get("/{application_id}", response_model=schemas.ApplicationOut)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    return get_owned(db, application_id, user)


@router.patch("/{application_id}", response_model=schemas.ApplicationOut)
def update_application(
    application_id: int,
    data: schemas.ApplicationUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    row = get_owned(db, application_id, user)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/{application_id}", status_code=204)
def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    row = get_owned(db, application_id, user)
    db.delete(row)
    db.commit()