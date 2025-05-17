from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"

class DeploymentStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    QUEUED = "queued"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(UserRole), default=UserRole.DEVELOPER)
    
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    organization = relationship("Organization", back_populates="users")

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    invite_code = Column(String, unique=True, index=True)
    
    users = relationship("User", back_populates="organization")
    clusters = relationship("Cluster", back_populates="organization")

class Cluster(Base):
    __tablename__ = "clusters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    total_cpu = Column(Float)
    total_ram = Column(Float)
    total_gpu = Column(Integer)
    available_cpu = Column(Float)
    available_ram = Column(Float)
    available_gpu = Column(Integer)
    
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    organization = relationship("Organization", back_populates="clusters")
    deployments = relationship("Deployment", back_populates="cluster")

class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    docker_image = Column(String)
    status = Column(Enum(DeploymentStatus), default=DeploymentStatus.PENDING)
    priority = Column(Integer, default=0)
    required_cpu = Column(Float)
    required_ram = Column(Float)
    required_gpu = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    cluster_id = Column(Integer, ForeignKey("clusters.id"))
    cluster = relationship("Cluster", back_populates="deployments")
    
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User") 