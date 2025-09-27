from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class Programa(Base):
    __tablename__ = "programa"

    id = Column(Integer, primary_key=True, index=True)
    nome_chamada = Column(String)
    programa_cnpq = Column(String)
    grande_area = Column(String)
    area = Column(String)
    subarea = Column(String)
    pagamentos = relationship("Pagamento", back_populates="programa")