from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class AccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=6, max_length=128)
    role: str = "manager"


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VehicleBase(BaseModel):
    plate_number: str = Field(min_length=2, max_length=32)
    brand: str = Field(min_length=2, max_length=100)
    model: str = Field(min_length=1, max_length=100)
    year: int | None = None
    fuel_type: str = "diesel"
    fuel_consumption_norm: float = 0
    status: str = "active"
    mileage: float = 0


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    plate_number: str | None = None
    brand: str | None = None
    model: str | None = None
    year: int | None = None
    fuel_type: str | None = None
    fuel_consumption_norm: float | None = None
    status: str | None = None
    mileage: float | None = None


class VehicleRead(VehicleBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DriverBase(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    license_number: str = Field(min_length=2, max_length=100)
    phone: str | None = None
    salary_per_trip: float = 0
    status: str = "active"


class DriverCreate(DriverBase):
    pass


class DriverUpdate(BaseModel):
    full_name: str | None = None
    license_number: str | None = None
    phone: str | None = None
    salary_per_trip: float | None = None
    status: str | None = None


class DriverRead(DriverBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RouteBase(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    origin: str = Field(min_length=2, max_length=255)
    destination: str = Field(min_length=2, max_length=255)
    distance_km: float = Field(gt=0)
    planned_duration_hours: float = 0
    tolls_estimate: float = 0


class RouteCreate(RouteBase):
    pass


class RouteUpdate(BaseModel):
    name: str | None = None
    origin: str | None = None
    destination: str | None = None
    distance_km: float | None = None
    planned_duration_hours: float | None = None
    tolls_estimate: float | None = None


class RouteRead(RouteBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TripBase(BaseModel):
    vehicle_id: int
    driver_id: int
    route_id: int
    trip_date: date
    cargo_weight_tons: float = 0
    empty_mileage_km: float = 0
    status: str = "planned"
    driver_salary: float = 0
    fuel_cost: float = 0
    maintenance_cost: float = 0
    tolls: float = 0
    depreciation: float = 0
    other_costs: float = 0
    notes: str | None = None


class TripCreate(TripBase):
    pass


class TripUpdate(BaseModel):
    vehicle_id: int | None = None
    driver_id: int | None = None
    route_id: int | None = None
    trip_date: date | None = None
    cargo_weight_tons: float | None = None
    empty_mileage_km: float | None = None
    status: str | None = None
    driver_salary: float | None = None
    fuel_cost: float | None = None
    maintenance_cost: float | None = None
    tolls: float | None = None
    depreciation: float | None = None
    other_costs: float | None = None
    notes: str | None = None


class TripRead(TripBase):
    id: int
    total_cost: float
    cost_per_km: float
    efficiency_score: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExpenseBase(BaseModel):
    trip_id: int
    expense_type: str = Field(min_length=2, max_length=50)
    amount: float = Field(ge=0)
    description: str | None = None


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    trip_id: int | None = None
    expense_type: str | None = None
    amount: float | None = None
    description: str | None = None


class ExpenseRead(ExpenseBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FuelLogBase(BaseModel):
    trip_id: int | None = None
    vehicle_id: int
    log_date: date
    liters: float = Field(ge=0)
    price_per_liter: float = Field(ge=0)
    odometer_km: float | None = None


class FuelLogCreate(FuelLogBase):
    pass


class FuelLogUpdate(BaseModel):
    trip_id: int | None = None
    vehicle_id: int | None = None
    log_date: date | None = None
    liters: float | None = None
    price_per_liter: float | None = None
    odometer_km: float | None = None


class FuelLogRead(FuelLogBase):
    id: int
    total_cost: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MaintenanceBase(BaseModel):
    trip_id: int | None = None
    vehicle_id: int
    service_date: date
    maintenance_type: str = Field(min_length=2, max_length=100)
    cost: float = Field(ge=0)
    description: str | None = None


class MaintenanceCreate(MaintenanceBase):
    pass


class MaintenanceUpdate(BaseModel):
    trip_id: int | None = None
    vehicle_id: int | None = None
    service_date: date | None = None
    maintenance_type: str | None = None
    cost: float | None = None
    description: str | None = None


class MaintenanceRead(MaintenanceBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OptimizationResultRead(BaseModel):
    id: int
    trip_id: int
    total_cost: float
    cost_per_km: float
    efficiency_score: float
    recommendation: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnalyticsSummary(BaseModel):
    vehicles_count: int
    drivers_count: int
    routes_count: int
    trips_count: int
    total_cost: float
    average_cost_per_km: float
    most_expensive_trip_id: int | None
    cheapest_route_id: int | None


class AnalyticsExpenseItem(BaseModel):
    name: str
    value: float


class AnalyticsMonthItem(BaseModel):
    month: str
    total_cost: float


class OptimizationRunResponse(BaseModel):
    processed_trips: int
    cheapest_route: dict | None
    most_expensive_trip: dict | None
    high_fuel_vehicles: list[dict]
    recommendations: list[dict]

