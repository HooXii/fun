from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import Expense, Trip, User
from app.schemas import ExpenseCreate, ExpenseRead, ExpenseUpdate
from app.services.costs import recalculate_trip_by_id


router = APIRouter()


@router.get("", response_model=list[ExpenseRead])
def list_expenses(
    trip_id: int | None = None,
    expense_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[Expense]:
    query = db.query(Expense)
    if trip_id:
        query = query.filter(Expense.trip_id == trip_id)
    if expense_type:
        query = query.filter(Expense.expense_type == expense_type)
    return query.order_by(Expense.id.desc()).all()


@router.post("", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(payload: ExpenseCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> Expense:
    if db.get(Trip, payload.trip_id) is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    expense = Expense(**payload.model_dump())
    db.add(expense)
    db.flush()
    recalculate_trip_by_id(db, expense.trip_id)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("/{expense_id}", response_model=ExpenseRead)
def get_expense(expense_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> Expense:
    expense = db.get(Expense, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.put("/{expense_id}", response_model=ExpenseRead)
def update_expense(
    expense_id: int,
    payload: ExpenseUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Expense:
    expense = db.get(Expense, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")

    old_trip_id = expense.trip_id
    data = payload.model_dump(exclude_unset=True)
    if "trip_id" in data and db.get(Trip, data["trip_id"]) is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    for key, value in data.items():
        setattr(expense, key, value)

    db.flush()
    recalculate_trip_by_id(db, old_trip_id)
    recalculate_trip_by_id(db, expense.trip_id)
    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> None:
    expense = db.get(Expense, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    trip_id = expense.trip_id
    db.delete(expense)
    db.flush()
    recalculate_trip_by_id(db, trip_id)
    db.commit()

