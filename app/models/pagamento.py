from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Pagamento(Base):
    __tablename__ = "pagamento"

    id = Column(Integer, primary_key=True, index=True)
    ano_referencia = Column(Integer)
    processo = Column(String)
    modalidade = Column(String)
    linha_fomento = Column(String)
    valor_pago = Column(Float)
    data_inicio = Column(Date)
    data_fim = Column(Date)
    titulo_projeto = Column(String)
    
    # Foreign Keys
    fk_beneficiario = Column(Integer, ForeignKey("beneficiario.id"))
    fk_instituicao = Column(Integer, ForeignKey("instituicao.id"))
    fk_programa = Column(Integer, ForeignKey("programa.id"))
    
    # Relationships
    beneficiario = relationship("Beneficiario", back_populates="pagamentos")
    instituicao = relationship("Instituicao", back_populates="pagamentos")
    programa = relationship("Programa", back_populates="pagamentos")