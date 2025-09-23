import datetime
from pydantic import BaseModel

class PagamentoBase(BaseModel):
    ano_referencia: int
    processo: str | None = None
    modalidade: str | None = None
    linha_fomento: str | None = None
    valor_pago: float | None = None
    data_inicio: datetime.date | None = None
    data_fim: datetime.date | None = None
    titulo_projeto: str | None = None
    fk_beneficiario: int
    fk_instituicao: int
    fk_programa: int

class PagamentoCreate(PagamentoBase):
    pass

class Pagamento(PagamentoBase):
    id: int

    class Config:
        orm_mode = True