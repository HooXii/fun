from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import Maintenance, Trip, User, Vehicle
from app.schemas import MaintenanceCreate, MaintenanceRead, MaintenanceUpdate
from app.services.costs import recalculate_trip_by_id


router = APIRouter()


def _validate_maintenance_refs(db: Session, vehicle_id: int, trip_id: int | None) -> None:
    if db.get(Vehicle, vehicle_id) is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if trip_id is not None:
        trip = db.get(Trip, trip_id)
        if trip is None:
            raise HTTPException(status_code=404, detail="Trip not found")
        if trip.vehicle_id != vehicle_id:
            raise HTTPException(status_code=400, detail="Maintenance vehicle must match trip vehicle")


@router.get("", response_model=list[MaintenanceRead])
def list_maintenance(
    trip_id: int | None = None,
    vehicle_id: int | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[Maintenance]:
    query = db.query(Maintenance)
    if trip_id:
        query = query.filter(Maintenance.trip_id == trip_id)
    if vehicle_id:
        query = query.filter(Maintenance.vehicle_id == vehicle_id)
    return query.order_by(Maintenance.service_date.desc(), Maintenance.id.desc()).all()


@router.post("", response_model=MaintenanceRead, status_code=status.HTTP_201_CREATED)
def create_maintenance(
    payload: MaintenanceCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Maintenance:
    _validate_maintenance_refs(db, payload.vehicle_id, payload.trip_id)
    record = Maintenance(**payload.model_dump())
    db.add(record)
    db.flush()
    recalculate_trip_by_id(db, record.trip_id)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{maintenance_id}", response_model=MaintenanceRead)
def get_maintenance(
    maintenance_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Maintenance:
    record = db.get(Maintenance, maintenance_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    return record


@router.put("/{maintenance_id}", response_model=MaintenanceRead)
def update_maintenance(
    maintenance_id: int,
    payload: MaintenanceUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Maintenance:
    record = db.get(Maintenance, maintenance_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Maintenance record not found")

    old_trip_id = record.trip_id
    data = payload.model_dump(exclude_unset=True)
    vehicle_id = data.get("vehicle_id", record.vehicle_id)
    trip_id = data.get("trip_id", record.trip_id)
    _validate_maintenance_refs(db, vehicle_id, trip_id)
    for key, value in data.items():
        setattr(record, key, value)

    db.flush()
    recalculate_trip_by_id(db, old_trip_id)
    recalculate_trip_by_id(db, record.trip_id)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{maintenance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_maintenance(
    maintenance_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> None:
    record = db.get(Maintenance, maintenance_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    trip_id = record.trip_id
    db.delete(record)
    db.flush()
    recalculate_trip_by_id(db, trip_id)
    db.commit()

