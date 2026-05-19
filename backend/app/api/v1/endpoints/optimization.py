from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import OptimizationResult, User
from app.schemas import OptimizationResultRead, OptimizationRunResponse
from app.services.optimization import detect_high_fuel_vehicles, run_optimization


router = APIRouter()


@router.post("/run", response_model=OptimizationRunResponse)
def run(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> dict:
    return run_optimization(db)


@router.get("/results", response_model=list[OptimizationResultRead])
def results(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[OptimizationResult]:
    return db.query(OptimizationResult).order_by(OptimizationResult.created_at.desc()).all()


@router.get("/recommendations")
def recommendations(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> dict:
    results = db.query(OptimizationResult).order_by(OptimizationResult.created_at.desc()).all()
    return {
        "high_fuel_vehicles": detect_high_fuel_vehicles(db),
        "recommendations": [
            {
                "trip_id": result.trip_id,
                "cost_per_km": float(result.cost_per_km),
                "recommendation": result.recommendation,
            }
            for result in results
        ],
    }

