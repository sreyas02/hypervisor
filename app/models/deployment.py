from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum

class DeploymentStatus(enum.Enum):
    PENDING = "PENDING"
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    QUEUED = "QUEUED"

class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(DeploymentStatus), nullable=True)
    docker_image = Column(String, nullable=True)
    priority = Column(Integer, nullable=True)
    required_cpu = Column(Float, nullable=True)
    required_ram = Column(Float, nullable=True)
    required_gpu = Column(Integer, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    cluster_id = Column(Integer, ForeignKey("clusters.id"), nullable=True)

    user = relationship("User", back_populates="deployments")
    cluster = relationship("Cluster", back_populates="deployments") 