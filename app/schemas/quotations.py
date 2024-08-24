from pydantic import BaseModel



class QuotationSchema(BaseModel):
    id:int

class QuotationTestParameterSchema(BaseModel):
    id:int

class QuotationCreate(BaseModel):
    pass

class QuotationUpdate(BaseModel):
    pass

