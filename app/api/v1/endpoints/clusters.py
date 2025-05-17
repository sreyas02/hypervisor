from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas.cluster import Cluster, ClusterCreate, ClusterUpdate
from app.services.cluster import cluster_service
from app.core.auth import get_current_user
from app.db.models import User

router = APIRouter()

@router.post("/", response_model=Cluster)
def create_cluster(
    *,
    db: Session = Depends(get_db),
    cluster_in: ClusterCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create new cluster.
    """
    # Verify user belongs to the organization
    if current_user.organization_id != cluster_in.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create cluster for this organization",
        )
    
    cluster = cluster_service.create(db, obj_in=cluster_in)
    return cluster

@router.get("/", response_model=List[Cluster])
def read_clusters(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve clusters for the user's organization.
    """
    clusters = cluster_service.get_multi_by_organization(
        db, organization_id=current_user.organization_id, skip=skip, limit=limit
    )
    return clusters

@router.get("/{cluster_id}", response_model=Cluster)
def read_cluster(
    *,
    db: Session = Depends(get_db),
    cluster_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get cluster by ID.
    """
    cluster = cluster_service.get(db, id=cluster_id)
    if not cluster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster not found",
        )
    if cluster.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this cluster",
        )
    return cluster

@router.put("/{cluster_id}", response_model=Cluster)
def update_cluster(
    *,
    db: Session = Depends(get_db),
    cluster_id: int,
    cluster_in: ClusterUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update cluster.
    """
    cluster = cluster_service.get(db, id=cluster_id)
    if not cluster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster not found",
        )
    if cluster.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this cluster",
        )
    cluster = cluster_service.update(db, db_obj=cluster, obj_in=cluster_in)
    return cluster 