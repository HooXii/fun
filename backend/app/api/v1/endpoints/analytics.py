from collections import defaultdict
from statistics import mean

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import Driver, Expense, FuelLog, Maintenance, Route, Trip, User, Vehicle
from app.schemas import AnalyticsExpenseItem, AnalyticsMonthItem, AnalyticsSummary
from app.services.costs import to_float


router = APIRouter()


@router.get("/summary", response_model=AnalyticsSummary)
def summary(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> AnalyticsSummary:
    trips = db.query(Trip).all()
    total_cost = sum(to_float(trip.total_cost) for trip in trips)
    cost_per_km_values = [to_float(trip.cost_per_km) for trip in trips if to_float(trip.cost_per_km) > 0]
    most_expensive = max(trips, key=lambda trip: to_float(trip.total_cost), default=None)

    costs_by_route: dict[int, list[float]] = defaultdict(list)
    for trip in trips:
        if to_float(trip.cost_per_km) > 0:
            costs_by_route[trip.route_id].append(to_float(trip.cost_per_km))
    cheapest_route_id = None
    if costs_by_route:
        cheapest_route_id = min(costs_by_route, key=lambda route_id: mean(costs_by_route[route_id]))

    return AnalyticsSummary(
        vehicles_count=db.query(Vehicle).count(),
        drivers_count=db.query(Driver).count(),
        routes_count=db.query(Route).count(),
        trips_count=len(trips),
        total_cost=round(total_cost, 2),
        average_cost_per_km=round(mean(cost_per_km_values), 2) if cost_per_km_values else 0,
        most_expensive_trip_id=most_expensive.id if most_expensive else None,
        cheapest_route_id=cheapest_route_id,
    )


@router.get("/expenses-by-type", response_model=list[AnalyticsExpenseItem])
def expenses_by_type(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[AnalyticsExpenseItem]:
    totals: dict[str, float] = defaultdict(float)

    for trip in db.query(Trip).all():
        totals["Оплата водителя"] += to_float(trip.driver_salary)
        totals["Топливо"] += to_float(trip.fuel_cost)
        totals["Обслуживание"] += to_float(trip.maintenance_cost)
        totals["Платные дороги"] += to_float(trip.tolls)
        totals["Амортизация"] += to_float(trip.depreciation)
        totals["Прочее"] += to_float(trip.other_costs)

    for expense in db.query(Expense).all():
        name = {
            "fuel": "Топливо",
            "driver_salary": "Оплата водителя",
            "maintenance": "Обслуживание",
            "tolls": "Платные дороги",
            "depreciation": "Амортизация",
        }.get(expense.expense_type.strip().lower(), "Прочее")
        totals[name] += to_float(expense.amount)

    totals["Топливо"] += sum(to_float(log.total_cost) for log in db.query(FuelLog).all())
    totals["Обслуживание"] += sum(to_float(item.cost) for item in db.query(Maintenance).all())

    return [AnalyticsExpenseItem(name=name, value=round(value, 2)) for name, value in totals.items() if value > 0]


@router.get("/costs-by-month", response_model=list[AnalyticsMonthItem])
def costs_by_month(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[AnalyticsMonthItem]:
    totals: dict[str, float] = defaultdict(float)
    for trip in db.query(Trip).all():
        month = trip.trip_date.strftime("%Y-%m")
        totals[month] += to_float(trip.total_cost)
    return [AnalyticsMonthItem(month=month, total_cost=round(value, 2)) for month, value in sorted(totals.items())]

