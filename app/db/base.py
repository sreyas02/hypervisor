from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.core.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Import all models here for Alembic to detect them
from app.db.models import User, Organization, Cluster, Deployment, UserRole, DeploymentStatus

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 