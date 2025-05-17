from pydantic import BaseModel
from typing import Optional

class ClusterBase(BaseModel):
    name: str
    total_cpu: float
    total_ram: float
    total_gpu: int

class ClusterCreate(ClusterBase):
    organization_id: int

class ClusterUpdate(ClusterBase):
    pass

class ClusterInDBBase(ClusterBase):
    id: int
    available_cpu: float
    available_ram: float
    available_gpu: int
    organization_id: int

    class Config:
        from_attributes = True

class Cluster(ClusterInDBBase):
    pass

class ClusterInDB(ClusterInDBBase):
    pass 