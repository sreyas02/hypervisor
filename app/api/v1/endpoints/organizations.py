from typing import Any, List
import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas.organization import Organization, OrganizationCreate, OrganizationUpdate
from app.services.organization import organization_service
from app.core.auth import get_current_user
from app.db.models import User

router = APIRouter()

@router.post("/", response_model=Organization)
def create_organization(
    *,
    db: Session = Depends(get_db),
    organization_in: OrganizationCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create new organization.
    """
    # Generate a unique invite code
    invite_code = secrets.token_urlsafe(8)
    organization = organization_service.create(
        db, obj_in=organization_in, invite_code=invite_code
    )
    return organization

@router.get("/", response_model=List[Organization])
def read_organizations(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve organizations.
    """
    organizations = organization_service.get_multi(db, skip=skip, limit=limit)
    return organizations

@router.get("/{organization_id}", response_model=Organization)
def read_organization(
    *,
    db: Session = Depends(get_db),
    organization_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get organization by ID.
    """
    organization = organization_service.get(db, id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    return organization

@router.put("/{organization_id}", response_model=Organization)
def update_organization(
    *,
    db: Session = Depends(get_db),
    organization_id: int,
    organization_in: OrganizationUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update organization.
    """
    organization = organization_service.get(db, id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    organization = organization_service.update(db, db_obj=organization, obj_in=organization_in)
    return organization

@router.post("/join/{invite_code}", response_model=Organization)
def join_organization(
    *,
    db: Session = Depends(get_db),
    invite_code: str,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Join organization using invite code.
    """
    organization = organization_service.get_by_invite_code(db, invite_code=invite_code)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid invite code",
        )
    
    # Add user to organization
    current_user.organization_id = organization.id
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return organization 