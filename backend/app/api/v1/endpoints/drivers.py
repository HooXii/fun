from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import Driver, User
from app.schemas import DriverCreate, DriverRead, DriverUpdate


router = APIRouter()


@router.get("", response_model=list[DriverRead])
def list_drivers(
    search: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[Driver]:
    query = db.query(Driver)
    if search:
        like = f"%{search}%"
        query = query.filter(or_(Driver.full_name.ilike(like), Driver.license_number.ilike(like)))
    if status_filter:
        query = query.filter(Driver.status == status_filter)
    return query.order_by(Driver.id.desc()).all()


@router.post("", response_model=DriverRead, status_code=status.HTTP_201_CREATED)
def create_driver(payload: DriverCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> Driver:
    driver = Driver(**payload.model_dump())
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver


@router.get("/{driver_id}", response_model=DriverRead)
def get_driver(driver_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> Driver:
    driver = db.get(Driver, driver_id)
    if driver is None:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver


@router.put("/{driver_id}", response_model=DriverRead)
def update_driver(
    driver_id: int,
    payload: DriverUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Driver:
    driver = db.get(Driver, driver_id)
    if driver is None:
        raise HTTPException(status_code=404, detail="Driver not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(driver, key, value)
    db.commit()
    db.refresh(driver)
    return driver


@router.delete("/{driver_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_driver(driver_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> None:
    driver = db.get(Driver, driver_id)
    if driver is None:
        raise HTTPException(status_code=404, detail="Driver not found")
    db.delete(driver)
    db.commit()

