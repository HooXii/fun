from datetime import date

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models import Driver, Expense, FuelLog, Maintenance, Route, Trip, User, Vehicle
from app.services.costs import recalculate_trip_cost
from app.services.optimization import run_optimization


def seed() -> None:
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.email == "admin@example.com").first():
            db.add(
                User(
                    email="admin@example.com",
                    full_name="Администратор",
                    hashed_password=get_password_hash("admin123"),
                    role="admin",
                )
            )

        if db.query(Vehicle).count() == 0:
            vehicles = [
                Vehicle(
                    plate_number="A101AA77",
                    brand="KamAZ",
                    model="5490",
                    year=2021,
                    fuel_type="diesel",
                    fuel_consumption_norm=29,
                    mileage=142000,
                ),
                Vehicle(
                    plate_number="B202BB77",
                    brand="Volvo",
                    model="FH",
                    year=2020,
                    fuel_type="diesel",
                    fuel_consumption_norm=25,
                    mileage=188500,
                ),
                Vehicle(
                    plate_number="C303CC77",
                    brand="GAZ",
                    model="Next",
                    year=2022,
                    fuel_type="diesel",
                    fuel_consumption_norm=16,
                    mileage=62000,
                ),
            ]
            drivers = [
                Driver(full_name="Иванов Сергей Петрович", license_number="77AA123456", phone="+7 900 111-22-33", salary_per_trip=9000),
                Driver(full_name="Павлов Андрей Викторович", license_number="77BB654321", phone="+7 900 222-33-44", salary_per_trip=8500),
                Driver(full_name="Орлова Марина Игоревна", license_number="77CC111222", phone="+7 900 333-44-55", salary_per_trip=7000),
            ]
            routes = [
                Route(name="Москва - Тверь", origin="Москва", destination="Тверь", distance_km=180, planned_duration_hours=3.5, tolls_estimate=900),
                Route(name="Москва - Ярославль", origin="Москва", destination="Ярославль", distance_km=265, planned_duration_hours=4.5, tolls_estimate=1200),
                Route(name="Москва - Нижний Новгород", origin="Москва", destination="Нижний Новгород", distance_km=420, planned_duration_hours=7, tolls_estimate=2800),
            ]
            db.add_all(vehicles + drivers + routes)
            db.flush()

            trips = [
                Trip(
                    vehicle_id=vehicles[0].id,
                    driver_id=drivers[0].id,
                    route_id=routes[2].id,
                    trip_date=date(2026, 5, 10),
                    cargo_weight_tons=15,
                    empty_mileage_km=80,
                    status="completed",
                    driver_salary=12000,
                    tolls=2800,
                    depreciation=6500,
                    other_costs=1500,
                    notes="Доставка производственного оборудования",
                ),
                Trip(
                    vehicle_id=vehicles[1].id,
                    driver_id=drivers[1].id,
                    route_id=routes[1].id,
                    trip_date=date(2026, 5, 12),
                    cargo_weight_tons=12,
                    empty_mileage_km=25,
                    status="completed",
                    driver_salary=9500,
                    tolls=1200,
                    depreciation=4800,
                    other_costs=900,
                    notes="Плановая поставка на склад",
                ),
                Trip(
                    vehicle_id=vehicles[2].id,
                    driver_id=drivers[2].id,
                    route_id=routes[0].id,
                    trip_date=date(2026, 5, 14),
                    cargo_weight_tons=1.2,
                    empty_mileage_km=55,
                    status="completed",
                    driver_salary=7000,
                    tolls=900,
                    depreciation=2100,
                    other_costs=600,
                    notes="Малая партия груза",
                ),
            ]
            db.add_all(trips)
            db.flush()

            db.add_all(
                [
                    FuelLog(trip_id=trips[0].id, vehicle_id=vehicles[0].id, log_date=date(2026, 5, 10), liters=165, price_per_liter=64, total_cost=10560),
                    FuelLog(trip_id=trips[1].id, vehicle_id=vehicles[1].id, log_date=date(2026, 5, 12), liters=73, price_per_liter=64, total_cost=4672),
                    FuelLog(trip_id=trips[2].id, vehicle_id=vehicles[2].id, log_date=date(2026, 5, 14), liters=48, price_per_liter=64, total_cost=3072),
                    Maintenance(trip_id=trips[0].id, vehicle_id=vehicles[0].id, service_date=date(2026, 5, 9), maintenance_type="Плановое ТО", cost=18000),
                    Maintenance(trip_id=trips[2].id, vehicle_id=vehicles[2].id, service_date=date(2026, 5, 13), maintenance_type="Диагностика", cost=3500),
                    Expense(trip_id=trips[0].id, expense_type="other", amount=1200, description="Парковка и оформление документов"),
                    Expense(trip_id=trips[1].id, expense_type="other", amount=800, description="Погрузочные работы"),
                ]
            )
            db.flush()

            for trip in trips:
                recalculate_trip_cost(db, trip)

        db.commit()
        run_optimization(db)
    finally:
        db.close()


if __name__ == "__main__":
    seed()

