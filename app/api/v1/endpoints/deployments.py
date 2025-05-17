from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas.deployment import Deployment, DeploymentCreate, DeploymentUpdate
from app.services.deployment import deployment_service
from app.services.scheduler import SchedulerService
from app.core.auth import get_current_user
from app.db.models import User, Cluster, DeploymentStatus

router = APIRouter()

@router.post("/", response_model=Deployment)
def create_deployment(
    *,
    db: Session = Depends(get_db),
    deployment_in: DeploymentCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create new deployment.
    """
    # Verify cluster belongs to user's organization
    cluster = db.query(Cluster).filter(Cluster.id == deployment_in.cluster_id).first()
    if not cluster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster not found",
        )
    if cluster.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to deploy to this cluster",
        )
    
    # Create deployment
    deployment = deployment_service.create(
        db, obj_in=deployment_in, user_id=current_user.id
    )
    
    # Try to schedule the deployment
    scheduler = SchedulerService(db)
    if not scheduler.schedule_deployment(deployment):
        # If scheduling fails, try preemption
        if deployment.priority > 0:
            scheduler.preempt_deployments(deployment)
    
    return deployment

@router.get("/", response_model=List[Deployment])
def read_deployments(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve deployments for the user's organization.
    """
    deployments = deployment_service.get_multi_by_organization(
        db, organization_id=current_user.organization_id, skip=skip, limit=limit
    )
    return deployments

@router.get("/{deployment_id}", response_model=Deployment)
def read_deployment(
    *,
    db: Session = Depends(get_db),
    deployment_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get deployment by ID.
    """
    deployment = deployment_service.get(db, id=deployment_id)
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found",
        )
    if deployment.cluster.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this deployment",
        )
    return deployment

@router.put("/{deployment_id}", response_model=Deployment)
def update_deployment(
    *,
    db: Session = Depends(get_db),
    deployment_id: int,
    deployment_in: DeploymentUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update deployment.
    """
    deployment = deployment_service.get(db, id=deployment_id)
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found",
        )
    if deployment.cluster.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this deployment",
        )
    
    # If priority is being updated, we need to reschedule
    if deployment_in.priority != deployment.priority:
        scheduler = SchedulerService(db)
        scheduler.process_queue(deployment.cluster_id)
    
    deployment = deployment_service.update(db, db_obj=deployment, obj_in=deployment_in)
    return deployment

@router.delete("/{deployment_id}", response_model=Deployment)
def delete_deployment(
    *,
    db: Session = Depends(get_db),
    deployment_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Delete a deployment.
    """
    deployment = deployment_service.get(db, id=deployment_id)
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found",
        )
    if deployment.cluster.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this deployment",
        )
    
    # If deployment is running, release its resources
    if deployment.status == DeploymentStatus.RUNNING:
        scheduler = SchedulerService(db)
        scheduler.release_resources(deployment.cluster, deployment)
    
    deployment = deployment_service.delete(db, id=deployment_id)
    return deployment 