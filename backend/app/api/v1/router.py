from fastapi import APIRouter

from app.api.v1.endpoints import (
    analytics,
    auth,
    drivers,
    expenses,
    fuel_logs,
    maintenance,
    optimization,
    reports,
    routes,
    trips,
    vehicles,
)


api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["vehicles"])
api_router.include_router(drivers.router, prefix="/drivers", tags=["drivers"])
api_router.include_router(routes.router, prefix="/routes", tags=["routes"])
api_router.include_router(trips.router, prefix="/trips", tags=["trips"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["expenses"])
api_router.include_router(fuel_logs.router, prefix="/fuel-logs", tags=["fuel_logs"])
api_router.include_router(maintenance.router, prefix="/maintenance", tags=["maintenance"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(optimization.router, prefix="/optimization", tags=["optimization"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])

