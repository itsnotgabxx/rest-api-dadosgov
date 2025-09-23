from pydantic import BaseModel

class BeneficiarioBase(BaseModel):
    nome: str
    cpf_anonimizado: str
    categoria_nivel: str

class BeneficiarioCreate(BeneficiarioBase):
    pass

class Beneficiario(BeneficiarioBase):
    id: int

    class Config:
        orm_mode = True