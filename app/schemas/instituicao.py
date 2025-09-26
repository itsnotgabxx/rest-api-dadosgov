from pydantic import BaseModel

class InstituicaoBase(BaseModel):
    nome: str
    sigla: str | None = None
    cidade: str | None = None
    uf: str | None = None
    pais: str | None = None

class InstituicaoCreate(InstituicaoBase):
    pass

class Instituicao(InstituicaoBase):
    id: int

    class Config:
        from_attributes = True