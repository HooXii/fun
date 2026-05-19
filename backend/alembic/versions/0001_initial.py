"""Initial schema.

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-19
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "vehicles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("plate_number", sa.String(length=32), nullable=False),
        sa.Column("brand", sa.String(length=100), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("fuel_type", sa.String(length=50), nullable=False),
        sa.Column("fuel_consumption_norm", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("mileage", sa.Numeric(12, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_vehicles_id"), "vehicles", ["id"], unique=False)
    op.create_index(op.f("ix_vehicles_plate_number"), "vehicles", ["plate_number"], unique=True)

    op.create_table(
        "drivers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("license_number", sa.String(length=100), nullable=False),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("salary_per_trip", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_drivers_id"), "drivers", ["id"], unique=False)
    op.create_index(op.f("ix_drivers_license_number"), "drivers", ["license_number"], unique=True)

    op.create_table(
        "routes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("origin", sa.String(length=255), nullable=False),
        sa.Column("destination", sa.String(length=255), nullable=False),
        sa.Column("distance_km", sa.Numeric(10, 2), nullable=False),
        sa.Column("planned_duration_hours", sa.Numeric(10, 2), nullable=False),
        sa.Column("tolls_estimate", sa.Numeric(12, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_routes_id"), "routes", ["id"], unique=False)

    op.create_table(
        "trips",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vehicle_id", sa.Integer(), nullable=False),
        sa.Column("driver_id", sa.Integer(), nullable=False),
        sa.Column("route_id", sa.Integer(), nullable=False),
        sa.Column("trip_date", sa.Date(), nullable=False),
        sa.Column("cargo_weight_tons", sa.Numeric(10, 2), nullable=False),
        sa.Column("empty_mileage_km", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("driver_salary", sa.Numeric(12, 2), nullable=False),
        sa.Column("fuel_cost", sa.Numeric(12, 2), nullable=False),
        sa.Column("maintenance_cost", sa.Numeric(12, 2), nullable=False),
        sa.Column("tolls", sa.Numeric(12, 2), nullable=False),
        sa.Column("depreciation", sa.Numeric(12, 2), nullable=False),
        sa.Column("other_costs", sa.Numeric(12, 2), nullable=False),
        sa.Column("total_cost", sa.Numeric(12, 2), nullable=False),
        sa.Column("cost_per_km", sa.Numeric(12, 2), nullable=False),
        sa.Column("efficiency_score", sa.Numeric(12, 6), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["driver_id"], ["drivers.id"]),
        sa.ForeignKeyConstraint(["route_id"], ["routes.id"]),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_trips_id"), "trips", ["id"], unique=False)

    op.create_table(
        "expenses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("trip_id", sa.Integer(), nullable=False),
        sa.Column("expense_type", sa.String(length=50), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_expenses_id"), "expenses", ["id"], unique=False)

    op.create_table(
        "fuel_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("trip_id", sa.Integer(), nullable=True),
        sa.Column("vehicle_id", sa.Integer(), nullable=False),
        sa.Column("log_date", sa.Date(), nullable=False),
        sa.Column("liters", sa.Numeric(10, 2), nullable=False),
        sa.Column("price_per_liter", sa.Numeric(10, 2), nullable=False),
        sa.Column("total_cost", sa.Numeric(12, 2), nullable=False),
        sa.Column("odometer_km", sa.Numeric(12, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"]),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_fuel_logs_id"), "fuel_logs", ["id"], unique=False)

    op.create_table(
        "maintenance",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("trip_id", sa.Integer(), nullable=True),
        sa.Column("vehicle_id", sa.Integer(), nullable=False),
        sa.Column("service_date", sa.Date(), nullable=False),
        sa.Column("maintenance_type", sa.String(length=100), nullable=False),
        sa.Column("cost", sa.Numeric(12, 2), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"]),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_maintenance_id"), "maintenance", ["id"], unique=False)

    op.create_table(
        "optimization_results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("trip_id", sa.Integer(), nullable=False),
        sa.Column("total_cost", sa.Numeric(12, 2), nullable=False),
        sa.Column("cost_per_km", sa.Numeric(12, 2), nullable=False),
        sa.Column("efficiency_score", sa.Numeric(12, 6), nullable=False),
        sa.Column("recommendation", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_optimization_results_id"), "optimization_results", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_optimization_results_id"), table_name="optimization_results")
    op.drop_table("optimization_results")
    op.drop_index(op.f("ix_maintenance_id"), table_name="maintenance")
    op.drop_table("maintenance")
    op.drop_index(op.f("ix_fuel_logs_id"), table_name="fuel_logs")
    op.drop_table("fuel_logs")
    op.drop_index(op.f("ix_expenses_id"), table_name="expenses")
    op.drop_table("expenses")
    op.drop_index(op.f("ix_trips_id"), table_name="trips")
    op.drop_table("trips")
    op.drop_index(op.f("ix_routes_id"), table_name="routes")
    op.drop_table("routes")
    op.drop_index(op.f("ix_drivers_license_number"), table_name="drivers")
    op.drop_index(op.f("ix_drivers_id"), table_name="drivers")
    op.drop_table("drivers")
    op.drop_index(op.f("ix_vehicles_plate_number"), table_name="vehicles")
    op.drop_index(op.f("ix_vehicles_id"), table_name="vehicles")
    op.drop_table("vehicles")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

