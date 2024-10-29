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
    client_full_name: str

class AccountResponse(BaseModel):
    account_id: int
    id_client: int
    account_number: str
    balance: float
    client_full_name: str  # Agregado para incluir el nombre completo del cliente