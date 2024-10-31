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

class ClientResponse(ClientCreate):
    id_client: int

class EmployeeCreate(BaseModel):
    name: str
    position: str
    hire_date:date

class EmployeeResponse(EmployeeCreate):
    employee_id: int

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
    from_account_number: str 
    to_account_number: str   
    amount: Decimal        
    transfer_date: date   
    transfer_method: str       
    status: str = "pending"    

class TransferResponse(TransferCreate):
    transfer_id: int          

class LoanCreate(BaseModel):
    client_full_name: str 
    employee_full_name: str
    amount: Decimal
    interest_rate: Decimal
    disbursement_date: date 
    due_date: date 
    balance: Decimal
    status: str = "active" 

class LoanResponse(LoanCreate):
    loan_id: int
    