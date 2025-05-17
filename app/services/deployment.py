from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models import Deployment
from app.schemas.deployment import DeploymentCreate, DeploymentUpdate

class DeploymentService:
    def get(self, db: Session, id: int) -> Optional[Deployment]:
        return db.query(Deployment).filter(Deployment.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Deployment]:
        return db.query(Deployment).offset(skip).limit(limit).all()

    def get_multi_by_organization(
        self, db: Session, *, organization_id: int, skip: int = 0, limit: int = 100
    ) -> List[Deployment]:
        return (
            db.query(Deployment)
            .join(Deployment.cluster)
            .filter(Deployment.cluster.has(organization_id=organization_id))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(
        self, db: Session, *, obj_in: DeploymentCreate, user_id: int
    ) -> Deployment:
        db_obj = Deployment(
            name=obj_in.name,
            docker_image=obj_in.docker_image,
            priority=obj_in.priority,
            required_cpu=obj_in.required_cpu,
            required_ram=obj_in.required_ram,
            required_gpu=obj_in.required_gpu,
            cluster_id=obj_in.cluster_id,
            user_id=user_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: Deployment, obj_in: DeploymentUpdate
    ) -> Deployment:
        update_data = obj_in.dict(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> Optional[Deployment]:
        """Delete a deployment."""
        deployment = self.get(db, id=id)
        if deployment:
            db.delete(deployment)
            db.commit()
        return deployment

deployment_service = DeploymentService() 