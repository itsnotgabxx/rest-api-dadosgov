from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class Beneficiario(Base):
    __tablename__ = "beneficiario"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    cpf_anonimizado = Column(String)
    categoria_nivel = Column(String)
    pagamentos = relationship("Pagamento", back_populates="beneficiario")