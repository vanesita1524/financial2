from pydantic import BaseModel
from typing import List

# Modelo para crear clientes 1
class ClientCreate(BaseModel):
    name: str
    last_name: str
    address: str
    phone_number: str
    email: str
    identification_type: str
    identification_number: str

# Modelo para respuesta de cliente
class ClientResponse(ClientCreate):
    id_client: int

#modelo para cuentas
class AccountCreate(BaseModel):
    account_number: str
    balance: float

class AccountResponse(AccountCreate):
    account_id: int