from fastapi import APIRouter, HTTPException
from typing import List
from conexion import get_db_connection
from models import ClientCreate, ClientResponse, AccountCreate, AccountResponse, WithdrawalCreate, WithdrawalResponse, TransferCreate, TransferResponse,EmployeeCreate, EmployeeResponse
from mysql.connector import Error
from decimal import Decimal
#aaa
router = APIRouter()

@router.post("/clients/bulk", response_model=List[ClientResponse], tags=["clients"])
async def create_clients_bulk(clients: List[ClientCreate]):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor()
    try:
        insert_query = """
        INSERT INTO clients (name, last_name, address, phone_number, email, identification_type, identification_number)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        client_data = [(client.name, client.last_name, client.address, client.phone_number, 
                        client.email, client.identification_type, client.identification_number) 
                    for client in clients]
        
        cursor.executemany(insert_query, client_data)
        connection.commit()
        
        cursor.execute("SELECT LAST_INSERT_ID()")
        last_id = cursor.fetchone()[0]
        
        return [ClientResponse(id_client=last_id+i, **client.dict()) for i, client in enumerate(clients)]
    
    except Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        cursor.close()
        connection.close()

@router.get("/clients", response_model=List[ClientResponse], tags=["clients"])
async def list_clients():
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
    
    cursor = connection.cursor(dictionary=True)
    try:
        select_query = """
        SELECT id_client, name, last_name, address, phone_number, 
            email, identification_type, identification_number 
        FROM clients
        """
        cursor.execute(select_query)
        clients = cursor.fetchall()
        
        return [ClientResponse(**client) for client in clients]
    
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error: {str(e)}")
    finally:
        cursor.close()
        connection.close()
# Ruta para obtener nombres y IDs de clientes
@router.get("/clients/names", tags=["clients"])
async def get_client_names():
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
    
    cursor = connection.cursor(dictionary=True)
    try:
        # Cambia 'first_name' y 'last_name' por los nombres de tus columnas reales
        query = "SELECT id_client, CONCAT(name, ' ', last_name) AS full_name FROM clients"
        cursor.execute(query)
        clients = cursor.fetchall()
        return clients
    
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error: {str(e)}")
    finally:
        cursor.close()
        connection.close()

@router.post("/employees", response_model=List[EmployeeResponse], tags=["employees"])
async def create_employees_bulk(employees: List[EmployeeCreate]):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor()
    try:
        insert_query = """
        INSERT INTO employees (name, position, hire_date)
        VALUES (%s, %s, %s)
        """
        employee_data = [(employee.name, employee.position, employee.hire_date) for employee in employees]
        
        cursor.executemany(insert_query, employee_data)
        connection.commit()
        
        cursor.execute("SELECT LAST_INSERT_ID()")
        last_id = cursor.fetchone()[0]
        
        return [EmployeeResponse(employee_id=last_id+i, **employee.dict()) for i, employee in enumerate(employees)]
    
    except Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        cursor.close()
        connection.close()

@router.get("/employees", response_model=List[EmployeeResponse], tags=["employees"])
async def list_employees():
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
    
    cursor = connection.cursor(dictionary=True)
    try:
        select_query = """
        SELECT employee_id, name, position, hire_date 
        FROM employees
        """
        cursor.execute(select_query)
        employees = cursor.fetchall()
        
        return [EmployeeResponse(**employee) for employee in employees]
    
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error: {str(e)}")
    finally:
        cursor.close()
        connection.close()

@router.post("/accounts", response_model=AccountResponse, tags=["accounts"])
async def create_account(account: AccountCreate):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    cursor = connection.cursor(dictionary=True)
    try:
        # Obtener el ID del cliente a partir del nombre completo
        cursor.execute("SELECT id_client FROM clients WHERE CONCAT(name, ' ', last_name) = %s", (account.client_full_name,))
        client = cursor.fetchone()
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        id_client = client["id_client"]
        
        # Insertar la cuenta con el ID del cliente
        # Obtener el ID del cliente a partir del nombre completo
        cursor.execute("SELECT id_client FROM clients WHERE CONCAT(name, ' ', last_name) = %s", (account.client_full_name,))
        client = cursor.fetchone()
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        id_client = client["id_client"]
        
        # Insertar la cuenta con el ID del cliente
        insert_query = """
        INSERT INTO accounts (id_client, account_number, balance)
        VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (id_client, account.account_number, account.balance))
        connection.commit()
        
        account_id = cursor.lastrowid
        return AccountResponse(account_id=account_id, id_client=id_client, **account.dict())
    
    except Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        cursor.close()
        connection.close()

@router.get("/accounts", response_model=List[AccountResponse], tags=["accounts"])
async def list_accounts():
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    try:
        select_query = """
        SELECT a.account_id, a.id_client, a.account_number, a.balance, c.name, c.last_name
        FROM accounts a
        JOIN clients c ON a.id_client = c.id_client
        """
        cursor.execute(select_query)
        accounts = cursor.fetchall()
        
        return [
            {
                "account_id": account["account_id"],
                "id_client": account["id_client"],
                "account_number": account["account_number"],
                "balance": account["balance"],
                "client_full_name": f"{account['name']} {account['last_name']}"  # Concatenar nombre y apellido
            }
            for account in accounts
        ]
    
    except Error as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        cursor.close()
        connection.close()

@router.post("/withdrawals", response_model=WithdrawalResponse, tags=["withdrawals"])
async def create_withdrawal(withdrawal: WithdrawalCreate):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    try:
        # Obtener el ID de la cuenta usando el número de cuenta
        cursor.execute("SELECT account_id, balance FROM accounts WHERE account_number = %s", (withdrawal.account_number,))
        account = cursor.fetchone()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Convertir el saldo y el monto a Decimal
        account_balance = Decimal(account["balance"])
        withdrawal_amount = Decimal(withdrawal.amount)
        
        # Verificar que haya suficiente saldo
        if account_balance < withdrawal_amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        
        # Actualizar el saldo después del retiro
        new_balance = account_balance - withdrawal_amount
        cursor.execute("UPDATE accounts SET balance = %s WHERE account_id = %s", (new_balance, account["account_id"]))
        
        # Insertar el retiro en la tabla de retiros
        insert_query = """
        INSERT INTO withdrawals (account_id, amount, withdrawal_date, withdrawal_method)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (account["account_id"], withdrawal_amount, withdrawal.withdrawal_date, withdrawal.withdrawal_method))
        connection.commit()
        
        withdrawal_id = cursor.lastrowid
        return WithdrawalResponse(
            withdrawal_id=withdrawal_id,
            account_id=account["account_id"],
            account_number=withdrawal.account_number,
            amount=float(withdrawal_amount),  # Convertir a float para la respuesta
            withdrawal_date=withdrawal.withdrawal_date,
            withdrawal_method=withdrawal.withdrawal_method
        )
    
    except Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        cursor.close()
        connection.close()

# Listar retiros
@router.get("/withdrawals", response_model=List[WithdrawalResponse], tags=["withdrawals"])
async def list_withdrawals():
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    try:
        select_query = """
        SELECT w.withdrawal_id, w.account_id, w.amount, w.withdrawal_date, w.withdrawal_method,
            a.account_number, c.name, c.last_name
        FROM withdrawals w
        JOIN accounts a ON w.account_id = a.account_id
        JOIN clients c ON a.id_client = c.id_client
        """
        cursor.execute(select_query)
        withdrawals = cursor.fetchall()
        
        # Modificar la respuesta para incluir el nombre completo del cliente y el número de cuenta
        return [
            {
                "withdrawal_id": withdrawal["withdrawal_id"],
                "account_id": withdrawal["account_id"],
                "amount": withdrawal["amount"],
                "withdrawal_date": withdrawal["withdrawal_date"],
                "withdrawal_method": withdrawal["withdrawal_method"],
                "account_number": withdrawal["account_number"],
                "client_full_name": f"{withdrawal['name']} {withdrawal['last_name']}"
            }
            for withdrawal in withdrawals
        ]
    
    except Error as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        cursor.close()
        connection.close()

@router.post("/transfers", response_model=TransferResponse, tags=["transfers"])
async def create_transfer(transfer: TransferCreate):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    try:
        # Obtener el ID de la cuenta de origen usando el número de cuenta
        cursor.execute("SELECT account_id, balance FROM accounts WHERE account_number = %s", (transfer.from_account_number,))
        from_account = cursor.fetchone()
        
        if not from_account:
            raise HTTPException(status_code=404, detail="From account not found")
        
        # Obtener el ID de la cuenta de destino usando el número de cuenta
        cursor.execute("SELECT account_id FROM accounts WHERE account_number = %s", (transfer.to_account_number,))
        to_account = cursor.fetchone()
        
        if not to_account:
            raise HTTPException(status_code=404, detail="To account not found")
        
        # Si el estado es "completed", verificar que haya suficiente saldo
        if transfer.status.lower() == "completed":
            if from_account["balance"] < transfer.amount:
                raise HTTPException(status_code=400, detail="Insufficient balance in the from account")
            
            # Actualizar el saldo de la cuenta de origen
            new_from_balance = from_account["balance"] - transfer.amount
            cursor.execute("UPDATE accounts SET balance = %s WHERE account_id = %s", (new_from_balance, from_account["account_id"]))
            
            # Actualizar el saldo de la cuenta de destino
            cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (to_account["account_id"],))
            to_account_balance = cursor.fetchone()["balance"]
            new_to_balance = to_account_balance + transfer.amount
            cursor.execute("UPDATE accounts SET balance = %s WHERE account_id = %s", (new_to_balance, to_account["account_id"]))
        
        # Insertar la transferencia en la tabla de transfers
        insert_query = """
        INSERT INTO transfers (from_account_id, to_account_id, amount, transfer_date, transfer_method, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (from_account["account_id"], to_account["account_id"], transfer.amount, transfer.transfer_date, transfer.transfer_method, transfer.status))
        connection.commit()
        
        transfer_id = cursor.lastrowid
        return TransferResponse(
            transfer_id=transfer_id,
            from_account_number=transfer.from_account_number,
            to_account_number=transfer.to_account_number,
            amount=transfer.amount,
            transfer_date=transfer.transfer_date,
            transfer_method=transfer.transfer_method,
            status=transfer.status
        )
    
    except Error as e:
        connection.rollback()  # Deshacer cambios en caso de error
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
    finally:
        cursor.close()  # Cerrar el cursor
        connection.close()  # Cerrar la conexión

@router.get("/transfers", response_model=List[TransferResponse], tags=["transfers"])
async def list_transfers():
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    try:
        select_query = """
        SELECT t.transfer_id, t.amount, t.transfer_date, t.transfer_method,  t.status,
            fa.account_number AS from_account_number, ta.account_number AS to_account_number
        FROM transfers t
        JOIN accounts fa ON t.from_account_id = fa.account_id
        JOIN accounts ta ON t.to_account_id = ta.account_id
        """
        cursor.execute(select_query)
        transfers = cursor.fetchall()
        
        return [
            {
                "transfer_id": transfer["transfer_id"],
                "from_account_number": transfer["from_account_number"],
                "to_account_number": transfer["to_account_number"],
                "amount": transfer["amount"],
                "transfer_date": transfer["transfer_date"],
                "transfer_method": transfer["transfer_method"],
                "status": transfer["status"]
            }
            for transfer in transfers
        ]
    
    except Error as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        cursor.close()
        connection.close()