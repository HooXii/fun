from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import Expense, Trip, User
from app.services.costs import to_float


router = APIRouter()


@router.get("/trips")
def trips_report(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[dict]:
    trips = db.query(Trip).order_by(Trip.trip_date.desc()).all()
    return [
        {
            "trip_id": trip.id,
            "date": trip.trip_date.isoformat(),
            "vehicle": trip.vehicle.plate_number if trip.vehicle else None,
            "driver": trip.driver.full_name if trip.driver else None,
            "route": trip.route.name if trip.route else None,
            "distance_km": to_float(trip.route.distance_km) if trip.route else 0,
            "total_cost": to_float(trip.total_cost),
            "cost_per_km": to_float(trip.cost_per_km),
            "efficiency_score": to_float(trip.efficiency_score),
            "status": trip.status,
        }
        for trip in trips
    ]


@router.get("/expenses")
def expenses_report(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[dict]:
    expenses = db.query(Expense).order_by(Expense.created_at.desc()).all()
    return [
        {
            "expense_id": expense.id,
            "trip_id": expense.trip_id,
            "route": expense.trip.route.name if expense.trip and expense.trip.route else None,
            "type": expense.expense_type,
            "amount": to_float(expense.amount),
            "description": expense.description,
            "created_at": expense.created_at.isoformat(),
        }
        for expense in expenses
    ]

