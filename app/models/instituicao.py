from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class Instituicao(Base):
    __tablename__ = "instituicao"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    sigla = Column(String)
    cidade = Column(String)
    uf = Column(String)
    pais = Column(String)
    pagamentos = relationship("Pagamento", back_populates="instituicao")