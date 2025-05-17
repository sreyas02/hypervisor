from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models import Cluster
from app.schemas.cluster import ClusterCreate, ClusterUpdate

class ClusterService:
    def get(self, db: Session, id: int) -> Optional[Cluster]:
        return db.query(Cluster).filter(Cluster.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Cluster]:
        return db.query(Cluster).offset(skip).limit(limit).all()

    def get_multi_by_organization(
        self, db: Session, *, organization_id: int, skip: int = 0, limit: int = 100
    ) -> List[Cluster]:
        return (
            db.query(Cluster)
            .filter(Cluster.organization_id == organization_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, db: Session, *, obj_in: ClusterCreate) -> Cluster:
        db_obj = Cluster(
            name=obj_in.name,
            total_cpu=obj_in.total_cpu,
            total_ram=obj_in.total_ram,
            total_gpu=obj_in.total_gpu,
            available_cpu=obj_in.total_cpu,
            available_ram=obj_in.total_ram,
            available_gpu=obj_in.total_gpu,
            organization_id=obj_in.organization_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: Cluster, obj_in: ClusterUpdate
    ) -> Cluster:
        update_data = obj_in.dict(exclude_unset=True)
        
        # Update available resources proportionally
        if "total_cpu" in update_data:
            ratio = update_data["total_cpu"] / db_obj.total_cpu
            db_obj.available_cpu = db_obj.available_cpu * ratio
        if "total_ram" in update_data:
            ratio = update_data["total_ram"] / db_obj.total_ram
            db_obj.available_ram = db_obj.available_ram * ratio
        if "total_gpu" in update_data:
            ratio = update_data["total_gpu"] / db_obj.total_gpu
            db_obj.available_gpu = int(db_obj.available_gpu * ratio)
        
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

cluster_service = ClusterService() 