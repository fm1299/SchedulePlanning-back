from sqlalchemy import Column, Integer, String
from core.database import Base

class Dias(Base):
    __tablename__ = "dias"

    id_dia = Column(Integer, primary_key=True, index=True)
    nombre_dia = Column(String, nullable=False)
    abreviatura = Column(String, nullable=False)
    orden = Column(Integer, nullable=False)
