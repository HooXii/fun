from collections import defaultdict

from sqlalchemy.orm import Session

from app.models import Expense, FuelLog, Maintenance, Route, Trip


def to_float(value: object) -> float:
    """Convert Decimal/None values from SQLAlchemy into regular floats for calculations."""

    if value is None:
        return 0.0
    return float(value)


def get_actual_distance_km(trip: Trip) -> float:
    route_distance = to_float(trip.route.distance_km) if trip.route else 0.0
    return route_distance + to_float(trip.empty_mileage_km)


def recalculate_trip_cost(db: Session, trip: Trip) -> Trip:
    """Recalculate stored financial indicators for a trip.

    The base cost columns can be filled directly in the trip form. Detailed records
    from expenses, fuel logs and maintenance are added on top of those base values.
    """

    if trip.route is None:
        trip.route = db.get(Route, trip.route_id)

    expense_totals: dict[str, float] = defaultdict(float)
    for expense in db.query(Expense).filter(Expense.trip_id == trip.id).all():
        expense_totals[expense.expense_type.strip().lower()] += to_float(expense.amount)

    fuel_logs_total = sum(
        to_float(row.total_cost) for row in db.query(FuelLog).filter(FuelLog.trip_id == trip.id).all()
    )
    maintenance_total = sum(
        to_float(row.cost) for row in db.query(Maintenance).filter(Maintenance.trip_id == trip.id).all()
    )

    fuel_cost = to_float(trip.fuel_cost) + fuel_logs_total + expense_totals["fuel"]
    driver_salary = to_float(trip.driver_salary) + expense_totals["driver_salary"]
    maintenance_cost = to_float(trip.maintenance_cost) + maintenance_total + expense_totals["maintenance"]
    tolls = to_float(trip.tolls) + expense_totals["tolls"]
    depreciation = to_float(trip.depreciation) + expense_totals["depreciation"]

    known_types = {"fuel", "driver_salary", "maintenance", "tolls", "depreciation"}
    detailed_other = sum(value for key, value in expense_totals.items() if key not in known_types)
    other_costs = to_float(trip.other_costs) + detailed_other

    total_cost = fuel_cost + driver_salary + maintenance_cost + tolls + depreciation + other_costs
    distance_km = get_actual_distance_km(trip)
    cost_per_km = total_cost / distance_km if distance_km > 0 else 0.0
    efficiency_score = distance_km / total_cost if total_cost > 0 else 0.0

    trip.total_cost = round(total_cost, 2)
    trip.cost_per_km = round(cost_per_km, 2)
    trip.efficiency_score = round(efficiency_score, 6)
    db.add(trip)
    return trip


def recalculate_trip_by_id(db: Session, trip_id: int | None) -> Trip | None:
    if trip_id is None:
        return None
    trip = db.get(Trip, trip_id)
    if trip is None:
        return None
    return recalculate_trip_cost(db, trip)

