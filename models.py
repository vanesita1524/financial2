from pydantic import BaseModel
from datetime import date
from decimal import Decimal



# Modelo para crear clientes 1
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

class EmployeeCreate(BaseModel):
    name: str
    position: str
    hire_date:date

# Modelo para respuesta de cliente
class EmployeeResponse(EmployeeCreate):
    employee_id: int
    
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
    client_full_name: str

class WithdrawalCreate(BaseModel):
    account_number: str  
    amount: float       
    withdrawal_date: date  
    withdrawal_method: str  

class WithdrawalResponse(WithdrawalCreate):
    withdrawal_id: int
    account_id: int
    account_number: str

class TransferCreate(BaseModel):
    from_account_number: str  # Número de cuenta de origen
    to_account_number: str    # Número de cuenta de destino
    amount: Decimal            # Monto de la transferencia
    transfer_date: date   # Fecha de la transferencia
    transfer_method: str       # Método de transferencia    # Banco de destino
    status: str = "pending"    # Estado de la transferencia (por defecto "pending")

class TransferResponse(TransferCreate):
    transfer_id: int           # ID de la transferencia

# Modelo para crear préstamos
class LoanCreate(BaseModel):
    client_full_name: str  # Nombre completo del cliente
    employee_full_name: str  # Nombre completo del empleado
    amount: Decimal
    interest_rate: Decimal
    disbursement_date: date # Inicialmente vacío
    due_date: date  # Inicialmente vacío
    balance: Decimal
    status: str = "active"  # Estado por defecto

# Modelo para respuesta de préstamo
class LoanResponse(LoanCreate):
    loan_id: int