from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models import Organization
from app.schemas.organization import OrganizationCreate, OrganizationUpdate

class OrganizationService:
    def get(self, db: Session, id: int) -> Optional[Organization]:
        return db.query(Organization).filter(Organization.id == id).first()

    def get_by_invite_code(self, db: Session, invite_code: str) -> Optional[Organization]:
        return db.query(Organization).filter(Organization.invite_code == invite_code).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Organization]:
        return db.query(Organization).offset(skip).limit(limit).all()

    def create(
        self, db: Session, *, obj_in: OrganizationCreate, invite_code: str
    ) -> Organization:
        db_obj = Organization(
            name=obj_in.name,
            invite_code=invite_code,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: Organization, obj_in: OrganizationUpdate
    ) -> Organization:
        update_data = obj_in.dict(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

organization_service = OrganizationService() 