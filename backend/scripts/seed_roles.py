from sqlalchemy.orm import Session
from app.enums.role_enum import RoleEnum
from app.models.role import Role


def seed_roles(db: Session):
    for role in RoleEnum:
        exists = db.query(Role).filter_by(name=role.value).first()
        if not exists:
            db.add(Role(name=role.value))
    db.commit()