from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import Route, User
from app.schemas import RouteCreate, RouteRead, RouteUpdate


router = APIRouter()


@router.get("", response_model=list[RouteRead])
def list_routes(
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[Route]:
    query = db.query(Route)
    if search:
        like = f"%{search}%"
        query = query.filter(or_(Route.name.ilike(like), Route.origin.ilike(like), Route.destination.ilike(like)))
    return query.order_by(Route.id.desc()).all()


@router.post("", response_model=RouteRead, status_code=status.HTTP_201_CREATED)
def create_route(payload: RouteCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> Route:
    route = Route(**payload.model_dump())
    db.add(route)
    db.commit()
    db.refresh(route)
    return route


@router.get("/{route_id}", response_model=RouteRead)
def get_route(route_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> Route:
    route = db.get(Route, route_id)
    if route is None:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


@router.put("/{route_id}", response_model=RouteRead)
def update_route(
    route_id: int,
    payload: RouteUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Route:
    route = db.get(Route, route_id)
    if route is None:
        raise HTTPException(status_code=404, detail="Route not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(route, key, value)
    db.commit()
    db.refresh(route)
    return route


@router.delete("/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_route(route_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> None:
    route = db.get(Route, route_id)
    if route is None:
        raise HTTPException(status_code=404, detail="Route not found")
    db.delete(route)
    db.commit()

