from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import Driver, Route, Trip, User, Vehicle
from app.schemas import TripCreate, TripRead, TripUpdate
from app.services.costs import recalculate_trip_cost


router = APIRouter()


def _validate_trip_refs(db: Session, vehicle_id: int, driver_id: int, route_id: int) -> None:
    if db.get(Vehicle, vehicle_id) is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if db.get(Driver, driver_id) is None:
        raise HTTPException(status_code=404, detail="Driver not found")
    if db.get(Route, route_id) is None:
        raise HTTPException(status_code=404, detail="Route not found")


@router.get("", response_model=list[TripRead])
def list_trips(
    status_filter: str | None = Query(default=None, alias="status"),
    vehicle_id: int | None = None,
    driver_id: int | None = None,
    route_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[Trip]:
    query = db.query(Trip)
    if status_filter:
        query = query.filter(Trip.status == status_filter)
    if vehicle_id:
        query = query.filter(Trip.vehicle_id == vehicle_id)
    if driver_id:
        query = query.filter(Trip.driver_id == driver_id)
    if route_id:
        query = query.filter(Trip.route_id == route_id)
    if date_from:
        query = query.filter(Trip.trip_date >= date_from)
    if date_to:
        query = query.filter(Trip.trip_date <= date_to)
    return query.order_by(Trip.trip_date.desc(), Trip.id.desc()).all()


@router.post("", response_model=TripRead, status_code=status.HTTP_201_CREATED)
def create_trip(payload: TripCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> Trip:
    _validate_trip_refs(db, payload.vehicle_id, payload.driver_id, payload.route_id)
    trip = Trip(**payload.model_dump())
    db.add(trip)
    db.flush()
    recalculate_trip_cost(db, trip)
    db.commit()
    db.refresh(trip)
    return trip


@router.get("/{trip_id}", response_model=TripRead)
def get_trip(trip_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> Trip:
    trip = db.get(Trip, trip_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


@router.put("/{trip_id}", response_model=TripRead)
def update_trip(
    trip_id: int,
    payload: TripUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Trip:
    trip = db.get(Trip, trip_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")

    data = payload.model_dump(exclude_unset=True)
    vehicle_id = data.get("vehicle_id", trip.vehicle_id)
    driver_id = data.get("driver_id", trip.driver_id)
    route_id = data.get("route_id", trip.route_id)
    _validate_trip_refs(db, vehicle_id, driver_id, route_id)

    for key, value in data.items():
        setattr(trip, key, value)
    recalculate_trip_cost(db, trip)
    db.commit()
    db.refresh(trip)
    return trip


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(trip_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> None:
    trip = db.get(Trip, trip_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    db.delete(trip)
    db.commit()

