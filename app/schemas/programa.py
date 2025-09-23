from pydantic import BaseModel

class ProgramaBase(BaseModel):
    nome_chamada: str | None = None
    programa_cnpq: str | None = None
    grande_area: str | None = None
    area: str | None = None
    subarea: str | None = None

class ProgramaCreate(ProgramaBase):
    pass

class Programa(ProgramaBase):
    id: int

    class Config:
        orm_mode = True