from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="manager", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    plate_number: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fuel_type: Mapped[str] = mapped_column(String(50), default="diesel", nullable=False)
    fuel_consumption_norm: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    mileage: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    trips: Mapped[list["Trip"]] = relationship(back_populates="vehicle")
    fuel_logs: Mapped[list["FuelLog"]] = relationship(back_populates="vehicle")
    maintenance_records: Mapped[list["Maintenance"]] = relationship(back_populates="vehicle")


class Driver(Base):
    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    license_number: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    salary_per_trip: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    trips: Mapped[list["Trip"]] = relationship(back_populates="driver")


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    origin: Mapped[str] = mapped_column(String(255), nullable=False)
    destination: Mapped[str] = mapped_column(String(255), nullable=False)
    distance_km: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    planned_duration_hours: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    tolls_estimate: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    trips: Mapped[list["Trip"]] = relationship(back_populates="route")


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), nullable=False)
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), nullable=False)
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"), nullable=False)
    trip_date: Mapped[date] = mapped_column(Date, nullable=False)
    cargo_weight_tons: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    empty_mileage_km: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="planned", nullable=False)
    driver_salary: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    fuel_cost: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    maintenance_cost: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    tolls: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    depreciation: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    other_costs: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    total_cost: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    cost_per_km: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    efficiency_score: Mapped[float] = mapped_column(Numeric(12, 6), default=0, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    vehicle: Mapped[Vehicle] = relationship(back_populates="trips")
    driver: Mapped[Driver] = relationship(back_populates="trips")
    route: Mapped[Route] = relationship(back_populates="trips")
    expenses: Mapped[list["Expense"]] = relationship(back_populates="trip", cascade="all, delete-orphan")
    fuel_logs: Mapped[list["FuelLog"]] = relationship(back_populates="trip")
    maintenance_records: Mapped[list["Maintenance"]] = relationship(back_populates="trip")
    optimization_results: Mapped[list["OptimizationResult"]] = relationship(
        back_populates="trip", cascade="all, delete-orphan"
    )


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id"), nullable=False)
    expense_type: Mapped[str] = mapped_column(String(50), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    trip: Mapped[Trip] = relationship(back_populates="expenses")


class FuelLog(Base):
    __tablename__ = "fuel_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    trip_id: Mapped[int | None] = mapped_column(ForeignKey("trips.id"), nullable=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), nullable=False)
    log_date: Mapped[date] = mapped_column(Date, nullable=False)
    liters: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    price_per_liter: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    total_cost: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    odometer_km: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    trip: Mapped[Trip | None] = relationship(back_populates="fuel_logs")
    vehicle: Mapped[Vehicle] = relationship(back_populates="fuel_logs")


class Maintenance(Base):
    __tablename__ = "maintenance"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    trip_id: Mapped[int | None] = mapped_column(ForeignKey("trips.id"), nullable=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), nullable=False)
    service_date: Mapped[date] = mapped_column(Date, nullable=False)
    maintenance_type: Mapped[str] = mapped_column(String(100), nullable=False)
    cost: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    trip: Mapped[Trip | None] = relationship(back_populates="maintenance_records")
    vehicle: Mapped[Vehicle] = relationship(back_populates="maintenance_records")


class OptimizationResult(Base):
    __tablename__ = "optimization_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id"), nullable=False)
    total_cost: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    cost_per_km: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    efficiency_score: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    trip: Mapped[Trip] = relationship(back_populates="optimization_results")

