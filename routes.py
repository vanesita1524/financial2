from fastapi import APIRouter, HTTPException
from typing import List
from conexion import get_db_connection
from models import ClientCreate, ClientResponse, AccountCreate, AccountResponse, WithdrawalCreate, WithdrawalResponse, TransferCreate, TransferResponse,EmployeeCreate, EmployeeResponse, LoanCreate, LoanResponse
from mysql.connector import Error
from decimal import Decimal

router = APIRouter()

@router.post("/clients", response_model=List[ClientResponse], tags=["clients"])
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
        
        # Obtener el último ID insertado
        last_id = cursor.lastrowid  # Asegúrate de que esto sea un entero
        
        return [
            EmployeeResponse(employee_id=last_id + i, **employee.dict()) for i, employee in enumerate(employees)
        ]
    
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

@router.post("/accounts/bulk", response_model=List[AccountResponse], tags=["accounts"])
async def create_accounts_bulk(accounts: List[AccountCreate]):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)

    try:
        insert_query = """
        INSERT INTO accounts (id_client, account_number, balance)
        VALUES (%s, %s, %s)
        """
        
        account_data = []
        for account in accounts:
            # Obtener el ID del cliente a partir del nombre completo
            cursor.execute("SELECT id_client FROM clients WHERE CONCAT(name, ' ', last_name) = %s", (account.client_full_name,))
            client = cursor.fetchone()
            
            if not client:
                raise HTTPException(status_code=404, detail=f"Client '{account.client_full_name}' not found")
            
            id_client = client["id_client"]
            account_data.append((id_client, account.account_number, account.balance))
        
        cursor.executemany(insert_query, account_data)
        connection.commit()
        
        # Obtener el último ID insertado
        last_id = cursor.lastrowid
        
        return [
            AccountResponse(account_id=last_id + i, id_client=id_client, **account.dict())
            for i, account in enumerate(accounts)
        ]
    
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

@router.post("/withdrawals/bulk", response_model=List[WithdrawalResponse], tags=["withdrawals"])
async def create_withdrawals_bulk(withdrawals: List[WithdrawalCreate]):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    try:
        withdrawal_data = []
        account_ids = {}

        # Obtener los IDs de las cuentas y verificar saldos
        for withdrawal in withdrawals:
            cursor.execute("SELECT account_id, balance FROM accounts WHERE account_number = %s", (withdrawal.account_number,))
            account = cursor.fetchone()
            
            if not account:
                raise HTTPException(status_code=404, detail=f"Account '{withdrawal.account_number}' not found")
            
            account_balance = Decimal(account["balance"])
            withdrawal_amount = Decimal(withdrawal.amount)
            
            if account_balance < withdrawal_amount:
                raise HTTPException(status_code=400, detail="Insufficient balance")
            
            # Agregar datos para la inserción
            withdrawal_data.append((account["account_id"], withdrawal_amount, withdrawal.withdrawal_date, withdrawal.withdrawal_method))
            account_ids[account["account_id"]] = account_balance - withdrawal_amount  # Actualizar saldo

        # Actualizar saldos de cuentas
        for account_id, new_balance in account_ids.items():
            cursor.execute("UPDATE accounts SET balance = %s WHERE account_id = %s", (new_balance, account_id))
        
        # Insertar los retiros en la tabla de retiros
        insert_query = """
        INSERT INTO withdrawals (account_id, amount, withdrawal_date, withdrawal_method)
        VALUES (%s, %s, %s, %s)
        """
        cursor.executemany(insert_query, withdrawal_data)
        connection.commit()
        
        # Obtener los IDs de los retiros insertados
        withdrawal_ids = []
        for i in range(len(withdrawal_data)):
            withdrawal_ids.append(cursor.lastrowid - len(withdrawal_data) + 1 + i)

        return [
            WithdrawalResponse(
                withdrawal_id=withdrawal_id,
                account_id=data[0],
                account_number=withdrawals[i].account_number,
                amount=float(data[1]),
                withdrawal_date=data[2],
                withdrawal_method=data[3]
            )
            for i, (data, withdrawal_id) in enumerate(zip(withdrawal_data, withdrawal_ids))
        ]
    
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

@router.post("/transfers/bulk", response_model=List[TransferResponse], tags=["transfers"])
async def create_transfers_bulk(transfers: List[TransferCreate]):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    try:
        transfer_data = []
        account_balances = {}

        # Verificar saldos y preparar datos para inserción
        for transfer in transfers:
            # Obtener el saldo de la cuenta de origen
            cursor.execute("SELECT account_id, balance FROM accounts WHERE account_number = %s", (transfer.from_account_number,))
            from_account = cursor.fetchone()
            
            if not from_account:
                raise HTTPException(status_code=404, detail=f"From account '{transfer.from_account_number}' not found")
            
            # Obtener el saldo de la cuenta de destino
            cursor.execute("SELECT account_id FROM accounts WHERE account_number = %s", (transfer.to_account_number,))
            to_account = cursor.fetchone()
            
            if not to_account:
                raise HTTPException(status_code=404, detail=f"To account '{transfer.to_account_number}' not found")
            
            # Verificar que haya suficiente saldo en la cuenta de origen
            if from_account["balance"] < transfer.amount:
                raise HTTPException(status_code=400, detail="Insufficient balance in the from account")
            
            # Preparar datos para la inserción
            transfer_data.append((from_account["account_id"], to_account["account_id"], transfer.amount, transfer.transfer_date, transfer.transfer_method, transfer.status))
            account_balances[from_account["account_id"]] = from_account["balance"] - transfer.amount  # Actualizar saldo de la cuenta de origen
            account_balances[to_account["account_id"]] = account_balances.get(to_account["account_id"], 0) + transfer.amount  # Actualizar saldo de la cuenta de destino

        # Actualizar saldos de cuentas
        for account_id, new_balance in account_balances.items():
            cursor.execute("UPDATE accounts SET balance = %s WHERE account_id = %s", (new_balance, account_id))
        
        # Insertar las transferencias en la tabla de transferencias
        insert_query = """
        INSERT INTO transfers (from_account_id, to_account_id, amount, transfer_date, transfer_method, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(insert_query, transfer_data)
        connection.commit()
        
        # Obtener los IDs de las transferencias insertadas
        transfer_ids = []
        for i in range(len(transfer_data)):
            transfer_ids.append(cursor.lastrowid - len(transfer_data) + 1 + i)

        return [
            TransferResponse(
                transfer_id=transfer_id,
                from_account_number=transfers[i].from_account_number,
                to_account_number=transfers[i].to_account_number,
                amount=transfer_data[i][2],  # Monto
                transfer_date=transfer_data[i][3],  # Fecha
                transfer_method=transfer_data[i][4],  # Método
                status=transfer_data[i][5]  # Estado
            )
            for i, transfer_id in enumerate(transfer_ids)
        ]
    
    except Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
    finally:
        cursor.close()
        connection.close()

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

@router.post("/loans/bulk", response_model=List[LoanResponse], tags=["loans"])
async def create_loans_bulk(loans: List[LoanCreate]):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    try:
        loan_data = []
        client_ids = {}
        employee_ids = {}

        # Obtener los IDs de los clientes y empleados
        for loan in loans:
            # Obtener el ID del cliente
            cursor.execute("SELECT id_client FROM clients WHERE CONCAT(name, ' ', last_name) = %s", (loan.client_full_name,))
            client = cursor.fetchone()
            
            if not client:
                raise HTTPException(status_code=404, detail=f"Client '{loan.client_full_name}' not found")
            client_ids[loan.client_full_name] = client["id_client"]

            # Obtener el ID del empleado
            cursor.execute("SELECT employee_id FROM employees WHERE name = %s", (loan.employee_full_name,))
            employee = cursor.fetchone()
            
            if not employee:
                raise HTTPException(status_code=404, detail=f"Employee '{loan.employee_full_name}' not found")
            employee_ids[loan.employee_full_name] = employee["employee_id"]

            # Preparar datos para la inserción
            loan_data.append((client_ids[loan.client_full_name], employee_ids[loan.employee_full_name], loan.amount, loan.interest_rate, loan.disbursement_date, loan.due_date, loan.balance, loan.status))

        # Insertar los préstamos en la tabla de préstamos
        insert_query = """
        INSERT INTO loans (ID_client, employee_id, amount, interest_rate, disbursement_date, due_date, balance, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(insert_query, loan_data)
        connection.commit()
        
        # Obtener los IDs de los préstamos insertados
        loan_ids = []
        for i in range(len(loan_data)):
            loan_ids.append(cursor.lastrowid - len(loan_data) + 1 + i)

        return [
            LoanResponse(loan_id=loan_id, **loan.dict())
            for i, loan_id in enumerate(loan_ids)
        ]
    
    except Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
    finally:
        cursor.close()
        connection.close()

@router.get("/loans", response_model=List[LoanResponse], tags=["loans"])
async def list_loans():
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    try:
        select_query = """
        SELECT l.loan_id, l.ID_client, l.employee_id, 
            c.name AS client_name, c.last_name AS client_last_name, 
            e.name AS employee_name, 
            l.amount, l.interest_rate, l.disbursement_date, l.due_date, l.balance, l.status
        FROM loans l
        JOIN clients c ON l.ID_client = c.id_client
        JOIN employees e ON l.employee_id = e.employee_id
        """
        cursor.execute(select_query)
        loans = cursor.fetchall()
        
        return [
            {
                "loan_id": loan["loan_id"],
                "client_full_name": f"{loan['client_name']} {loan['client_last_name']}",
                "employee_full_name": f"{loan['employee_name']}",
                "amount": loan["amount"],
                "interest_rate": loan["interest_rate"],
                "disbursement_date": loan["disbursement_date"],
                "due_date": loan["due_date"],
                "balance": loan["balance"],
                "status": loan["status"]
            }
            for loan in loans
        ]
    
    except Error as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        cursor.close()
        connection.close()