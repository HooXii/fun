from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import FuelLog, Trip, User, Vehicle
from app.schemas import FuelLogCreate, FuelLogRead, FuelLogUpdate
from app.services.costs import recalculate_trip_by_id


router = APIRouter()


def _validate_fuel_refs(db: Session, vehicle_id: int, trip_id: int | None) -> None:
    if db.get(Vehicle, vehicle_id) is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if trip_id is not None:
        trip = db.get(Trip, trip_id)
        if trip is None:
            raise HTTPException(status_code=404, detail="Trip not found")
        if trip.vehicle_id != vehicle_id:
            raise HTTPException(status_code=400, detail="Fuel log vehicle must match trip vehicle")


@router.get("", response_model=list[FuelLogRead])
def list_fuel_logs(
    trip_id: int | None = None,
    vehicle_id: int | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[FuelLog]:
    query = db.query(FuelLog)
    if trip_id:
        query = query.filter(FuelLog.trip_id == trip_id)
    if vehicle_id:
        query = query.filter(FuelLog.vehicle_id == vehicle_id)
    return query.order_by(FuelLog.log_date.desc(), FuelLog.id.desc()).all()


@router.post("", response_model=FuelLogRead, status_code=status.HTTP_201_CREATED)
def create_fuel_log(payload: FuelLogCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> FuelLog:
    _validate_fuel_refs(db, payload.vehicle_id, payload.trip_id)
    data = payload.model_dump()
    data["total_cost"] = round(payload.liters * payload.price_per_liter, 2)
    fuel_log = FuelLog(**data)
    db.add(fuel_log)
    db.flush()
    recalculate_trip_by_id(db, fuel_log.trip_id)
    db.commit()
    db.refresh(fuel_log)
    return fuel_log


@router.get("/{fuel_log_id}", response_model=FuelLogRead)
def get_fuel_log(fuel_log_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> FuelLog:
    fuel_log = db.get(FuelLog, fuel_log_id)
    if fuel_log is None:
        raise HTTPException(status_code=404, detail="Fuel log not found")
    return fuel_log


@router.put("/{fuel_log_id}", response_model=FuelLogRead)
def update_fuel_log(
    fuel_log_id: int,
    payload: FuelLogUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> FuelLog:
    fuel_log = db.get(FuelLog, fuel_log_id)
    if fuel_log is None:
        raise HTTPException(status_code=404, detail="Fuel log not found")

    old_trip_id = fuel_log.trip_id
    data = payload.model_dump(exclude_unset=True)
    vehicle_id = data.get("vehicle_id", fuel_log.vehicle_id)
    trip_id = data.get("trip_id", fuel_log.trip_id)
    _validate_fuel_refs(db, vehicle_id, trip_id)
    for key, value in data.items():
        setattr(fuel_log, key, value)
    fuel_log.total_cost = round(float(fuel_log.liters) * float(fuel_log.price_per_liter), 2)

    db.flush()
    recalculate_trip_by_id(db, old_trip_id)
    recalculate_trip_by_id(db, fuel_log.trip_id)
    db.commit()
    db.refresh(fuel_log)
    return fuel_log


@router.delete("/{fuel_log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fuel_log(fuel_log_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> None:
    fuel_log = db.get(FuelLog, fuel_log_id)
    if fuel_log is None:
        raise HTTPException(status_code=404, detail="Fuel log not found")
    trip_id = fuel_log.trip_id
    db.delete(fuel_log)
    db.flush()
    recalculate_trip_by_id(db, trip_id)
    db.commit()

