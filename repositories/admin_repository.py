from typing import Optional
from sqlalchemy.orm import Session

# Backwards-compatible adapter: AdminRepository now wraps Usuario model
from models.usuario import Usuario as Admin
from repositories.base import BaseRepository


class AdminRepository(BaseRepository[Admin]):
    def __init__(self, db: Session):
        super().__init__(Admin, db)

    def get_by_username(self, username: str) -> Optional[Admin]:
        return self.db.query(Admin).filter(Admin.username == username).first()

    def get_by_email(self, email: str) -> Optional[Admin]:
        return self.db.query(Admin).filter(Admin.email == email).first()

    def count(self) -> int:
        return self.db.query(Admin).count()
