from pydantic import BaseModel
from datetime import date
from decimal import Decimal


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

class AccountResponse(AccountCreate):
    account_id: int
    id_client: int

class WithdrawalCreate(BaseModel):
    account_number: str  # Número de cuenta
    amount: float        # Monto del retiro
    withdrawal_date: date  # Fecha del retiro
    withdrawal_method: str  # Método del retiro

class WithdrawalResponse(WithdrawalCreate):
    withdrawal_id: int
    account_id: int
    account_number: str