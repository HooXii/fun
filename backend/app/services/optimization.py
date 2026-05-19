from statistics import mean

from sqlalchemy.orm import Session

from app.models import FuelLog, OptimizationResult, Route, Trip, Vehicle
from app.services.costs import get_actual_distance_km, recalculate_trip_cost, to_float


def detect_high_fuel_vehicles(db: Session) -> list[dict]:
    """Find vehicles whose factual fuel consumption is higher than the configured norm."""

    vehicles = db.query(Vehicle).all()
    results: list[dict] = []

    for vehicle in vehicles:
        liters = 0.0
        distance = 0.0
        logs = db.query(FuelLog).filter(FuelLog.vehicle_id == vehicle.id, FuelLog.trip_id.isnot(None)).all()
        for log in logs:
            if log.trip is None:
                continue
            liters += to_float(log.liters)
            distance += get_actual_distance_km(log.trip)

        factual_consumption = liters / distance * 100 if distance > 0 else 0.0
        norm = to_float(vehicle.fuel_consumption_norm)
        if norm > 0 and factual_consumption > norm * 1.15:
            results.append(
                {
                    "vehicle_id": vehicle.id,
                    "plate_number": vehicle.plate_number,
                    "norm_l_per_100km": round(norm, 2),
                    "actual_l_per_100km": round(factual_consumption, 2),
                    "overrun_percent": round((factual_consumption / norm - 1) * 100, 1),
                }
            )

    return results


def _route_costs(trips: list[Trip]) -> dict[int, float]:
    grouped: dict[int, list[float]] = {}
    for trip in trips:
        if to_float(trip.cost_per_km) <= 0:
            continue
        grouped.setdefault(trip.route_id, []).append(to_float(trip.cost_per_km))
    return {route_id: mean(values) for route_id, values in grouped.items()}


def _serialize_route(db: Session, route_id: int | None, avg_cost_per_km: float | None = None) -> dict | None:
    if route_id is None:
        return None
    route = db.get(Route, route_id)
    if route is None:
        return None
    return {
        "route_id": route.id,
        "name": route.name,
        "origin": route.origin,
        "destination": route.destination,
        "distance_km": to_float(route.distance_km),
        "average_cost_per_km": round(avg_cost_per_km or 0, 2),
    }


def run_optimization(db: Session) -> dict:
    trips = db.query(Trip).all()
    for trip in trips:
        recalculate_trip_cost(db, trip)
    db.flush()

    high_fuel_vehicles = detect_high_fuel_vehicles(db)
    high_fuel_vehicle_ids = {item["vehicle_id"] for item in high_fuel_vehicles}

    valid_costs = [to_float(trip.cost_per_km) for trip in trips if to_float(trip.cost_per_km) > 0]
    average_cost_per_km = mean(valid_costs) if valid_costs else 0.0

    costs_by_route = _route_costs(trips)
    cheapest_route_id = min(costs_by_route, key=costs_by_route.get) if costs_by_route else None
    cheapest_route = _serialize_route(
        db,
        cheapest_route_id,
        costs_by_route.get(cheapest_route_id, 0.0) if cheapest_route_id else None,
    )

    most_expensive_trip = max(trips, key=lambda trip: to_float(trip.total_cost), default=None)
    most_expensive_trip_payload = (
        {
            "trip_id": most_expensive_trip.id,
            "total_cost": to_float(most_expensive_trip.total_cost),
            "cost_per_km": to_float(most_expensive_trip.cost_per_km),
        }
        if most_expensive_trip
        else None
    )

    db.query(OptimizationResult).delete(synchronize_session=False)
    recommendations: list[dict] = []

    for trip in trips:
        route_distance = to_float(trip.route.distance_km) if trip.route else 0.0
        messages: list[str] = []

        if trip.vehicle_id in high_fuel_vehicle_ids:
            messages.append("Заменить автомобиль или проверить техническое состояние из-за перерасхода топлива")
        if average_cost_per_km and to_float(trip.cost_per_km) > average_cost_per_km * 1.2:
            messages.append("Выбрать другой маршрут или пересмотреть структуру расходов рейса")
        if route_distance > 0 and to_float(trip.empty_mileage_km) > route_distance * 0.15:
            messages.append("Снизить холостой пробег за счет лучшего планирования обратной загрузки")
        if to_float(trip.cargo_weight_tons) < 2:
            messages.append("Пересмотреть загрузку транспорта и объединить малые отправки")
        if to_float(trip.maintenance_cost) > 0 and to_float(trip.maintenance_cost) > to_float(trip.total_cost) * 0.2:
            messages.append("Проверить техническое состояние автомобиля перед следующими рейсами")

        if not messages:
            messages.append("Рейс находится в допустимых пределах по стоимости и эффективности")

        recommendation_text = "; ".join(messages)
        result = OptimizationResult(
            trip_id=trip.id,
            total_cost=trip.total_cost,
            cost_per_km=trip.cost_per_km,
            efficiency_score=trip.efficiency_score,
            recommendation=recommendation_text,
        )
        db.add(result)
        recommendations.append(
            {
                "trip_id": trip.id,
                "total_cost": to_float(trip.total_cost),
                "cost_per_km": to_float(trip.cost_per_km),
                "efficiency_score": to_float(trip.efficiency_score),
                "recommendation": recommendation_text,
            }
        )

    db.commit()
    return {
        "processed_trips": len(trips),
        "cheapest_route": cheapest_route,
        "most_expensive_trip": most_expensive_trip_payload,
        "high_fuel_vehicles": high_fuel_vehicles,
        "recommendations": recommendations,
    }

