from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.db.models import DeploymentStatus

class DeploymentBase(BaseModel):
    name: str
    docker_image: str
    priority: int = 0
    required_cpu: float
    required_ram: float
    required_gpu: int

class DeploymentCreate(DeploymentBase):
    cluster_id: int

class DeploymentUpdate(DeploymentBase):
    status: Optional[DeploymentStatus] = None

class DeploymentInDBBase(DeploymentBase):
    id: int
    status: DeploymentStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cluster_id: int
    user_id: int

    class Config:
        from_attributes = True

class Deployment(DeploymentInDBBase):
    pass

class DeploymentInDB(DeploymentInDBBase):
    pass 