from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.resource import Resource
from app.models.user import User
from app.schemas.resource import ResourceCreate, ResourceOut
from app.core.security import require_admin, get_current_user
from typing import List, Optional
import uuid
from app.schemas.resource import ResourceUpdate

router = APIRouter(prefix="/resources", tags=["resources"])

@router.post("", response_model=ResourceOut)
def create_resource(
    resource_in: ResourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    new_resource = Resource(
        name=resource_in.name,
        type=resource_in.type,
        location=resource_in.location,
        capacity=resource_in.capacity,
        created_by=current_user.id,
    )
    db.add(new_resource)
    db.commit()
    db.refresh(new_resource)
    return new_resource


@router.get("", response_model=List[ResourceOut])
def list_resources(
    type: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Resource).filter(Resource.is_active == True)
    if type:
        query = query.filter(Resource.type == type)
    return query.offset(skip).limit(limit).all()


@router.get("/{resource_id}", response_model=ResourceOut)
def get_resource(
    resource_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource

@router.put("/{resource_id}", response_model=ResourceOut)
def update_resource(
    resource_id: uuid.UUID,
    resource_in: ResourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    update_data = resource_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resource, field, value)

    db.commit()
    db.refresh(resource)
    return resource


@router.delete("/{resource_id}")
def delete_resource(
    resource_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    resource.is_active = False
    db.commit()
    return {"detail": "Resource deactivated successfully"}
