from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Cluster(Base):
    __tablename__ = "clusters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    total_cpu = Column(Float, nullable=True)
    total_ram = Column(Float, nullable=True)
    total_gpu = Column(Integer, nullable=True)
    available_cpu = Column(Float, nullable=True)
    available_ram = Column(Float, nullable=True)
    available_gpu = Column(Integer, nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)

    organization = relationship("Organization", back_populates="clusters")
    deployments = relationship("Deployment", back_populates="cluster") 