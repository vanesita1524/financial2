from fastapi import APIRouter, HTTPException
from typing import List
from conexion import get_db_connection
from models import ClientCreate, ClientResponse, AccountCreate, AccountResponse, WithdrawalCreate, WithdrawalResponse, TransferCreate, TransferResponse,EmployeeCreate, EmployeeResponse, LoanCreate, LoanResponse
from mysql.connector import Error
from decimal import Decimal
from datetime import date

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
        raise HTTPException(status_code=500, detail="Database connection failed")
    
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
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
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
        
        last_id = cursor.lastrowid
        
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
        raise HTTPException(status_code=500, detail="Database connection failed")
    
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
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
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
            cursor.execute("SELECT id_client FROM clients WHERE CONCAT(name, ' ', last_name) = %s", (account.client_full_name,))
            client = cursor.fetchone()
            
            if not client:
                raise HTTPException(status_code=404, detail=f"Client '{account.client_full_name}' not found")
            
            id_client = client["id_client"]
            account_data.append((id_client, account.account_number, account.balance))
        cursor.executemany(insert_query, account_data)
        connection.commit()
        
        last_id = cursor.lastrowid
        return [AccountResponse(account_id=last_id + i, id_client=id_client, **account.dict())
            for i, account in enumerate(accounts)]
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
                "client_full_name": f"{account['name']} {account['last_name']}"
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

        for withdrawal in withdrawals:
            cursor.execute("SELECT account_id, balance FROM accounts WHERE account_number = %s", (withdrawal.account_number,))
            account = cursor.fetchone()
            
            if not account:
                raise HTTPException(status_code=404, detail=f"Account '{withdrawal.account_number}' not found")
            
            account_balance = Decimal(account["balance"])
            withdrawal_amount = Decimal(withdrawal.amount)
            
            if account_balance < withdrawal_amount:
                raise HTTPException(status_code=400, detail="Insufficient balance")
            
            withdrawal_data.append((account["account_id"], withdrawal_amount, withdrawal.withdrawal_date, withdrawal.withdrawal_method))
            account_ids[account["account_id"]] = account_balance - withdrawal_amount

        for account_id, new_balance in account_ids.items():
            cursor.execute("UPDATE accounts SET balance = %s WHERE account_id = %s", (new_balance, account_id))

        insert_query = """
        INSERT INTO withdrawals (account_id, amount, withdrawal_date, withdrawal_method)
        VALUES (%s, %s, %s, %s)
        """
        cursor.executemany(insert_query, withdrawal_data)
        connection.commit()
        
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

        for transfer in transfers:
            cursor.execute("SELECT account_id, balance FROM accounts WHERE account_number = %s", (transfer.from_account_number,))
            from_account = cursor.fetchone()
            
            if not from_account:
                raise HTTPException(status_code=404, detail=f"From account '{transfer.from_account_number}' not found")
            
            cursor.execute("SELECT account_id FROM accounts WHERE account_number = %s", (transfer.to_account_number,))
            to_account = cursor.fetchone()
            
            if not to_account:
                raise HTTPException(status_code=404, detail=f"To account '{transfer.to_account_number}' not found")
            
            if from_account["balance"] < transfer.amount:
                raise HTTPException(status_code=400, detail="Insufficient balance in the from account")
            
            transfer_data.append((from_account["account_id"], to_account["account_id"], transfer.amount, transfer.transfer_date, transfer.transfer_method, transfer.status))
            account_balances[from_account["account_id"]] = from_account["balance"] - transfer.amount  
            account_balances[to_account["account_id"]] = account_balances.get(to_account["account_id"], 0) + transfer.amount  

        for account_id, new_balance in account_balances.items():
            cursor.execute("UPDATE accounts SET balance = %s WHERE account_id = %s", (new_balance, account_id))
        
        insert_query = """
        INSERT INTO transfers (from_account_id, to_account_id, amount, transfer_date, transfer_method, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(insert_query, transfer_data)
        connection.commit()
        
        transfer_ids = []
        for i in range(len(transfer_data)):
            transfer_ids.append(cursor.lastrowid - len(transfer_data) + 1 + i)

        return [
            TransferResponse(
                transfer_id=transfer_id,
                from_account_number=transfers[i].from_account_number,
                to_account_number=transfers[i].to_account_number,
                amount=transfer_data[i][2], 
                transfer_date=transfer_data[i][3],  
                transfer_method=transfer_data[i][4],  
                status=transfer_data[i][5]  
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

        for loan in loans:
            cursor.execute("SELECT id_client FROM clients WHERE CONCAT(name, ' ', last_name) = %s", (loan.client_full_name,))
            client = cursor.fetchone()
            
            if not client:
                raise HTTPException(status_code=404, detail=f"Client '{loan.client_full_name}' not found")
            client_ids[loan.client_full_name] = client["id_client"]

            cursor.execute("SELECT employee_id FROM employees WHERE name = %s", (loan.employee_full_name,))
            employee = cursor.fetchone()
            
            if not employee:
                raise HTTPException(status_code=404, detail=f"Employee '{loan.employee_full_name}' not found")
            employee_ids[loan.employee_full_name] = employee["employee_id"]

            loan_data.append((client_ids[loan.client_full_name], employee_ids[loan.employee_full_name], loan.amount, loan.interest_rate, loan.disbursement_date, loan.due_date, loan.balance, loan.status))

        insert_query = """
        INSERT INTO loans (ID_client, employee_id, amount, interest_rate, disbursement_date, due_date, balance, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(insert_query, loan_data)
        connection.commit()
        
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


@router.get("/loans/summary_by_client_amount_count_loans", response_model=dict, tags=["loans"])
async def get_loans_summary_by_client(client_full_name: str):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    try:
        select_query = """
        SELECT c.id_client, c.name, c.last_name, 
            COUNT(l.loan_id) AS total_loans, 
            SUM(l.amount) AS total_amount
        FROM clients c
        LEFT JOIN loans l ON c.id_client = l.ID_client
        WHERE CONCAT(c.name, ' ', c.last_name) = %s
        GROUP BY c.id_client
        """
        cursor.execute(select_query, (client_full_name,))
        summary = cursor.fetchone()
        
        if not summary:
            raise HTTPException(status_code=404, detail="Client not found or has no loans")
        
        return {
            "client_id": summary["id_client"],
            "client_full_name": f"{summary['name']} {summary['last_name']}",
            "total_loans": summary["total_loans"],
            "total_amount": summary["total_amount"] if summary["total_amount"] is not None else 0.0
        }
    except Error as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        cursor.close()
        connection.close()

@router.get("/loans/summary_by_employee_amount_count_loans", response_model=dict, tags=["loans"])
async def get_loans_summary_by_employee(employee_full_name: str):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    try:
        select_query = """
        SELECT e.employee_id, e.name, 
            COUNT(l.loan_id) AS total_loans, 
            SUM(l.amount) AS total_amount
        FROM employees e
        LEFT JOIN loans l ON e.employee_id = l.employee_id
        WHERE e.name = %s
        GROUP BY e.employee_id
        """
        cursor.execute(select_query, (employee_full_name,))
        summary = cursor.fetchone()
        
        if not summary:
            raise HTTPException(status_code=404, detail="Employee not found or has no loans")
        
        return {
            "employee_id": summary["employee_id"],
            "employee_full_name": f"{summary['name']}",
            "total_loans": summary["total_loans"] if summary["total_loans"] is not None else 0,
            "total_amount": summary["total_amount"] if summary["total_amount"] is not None else 0.0
        }
    except Error as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        cursor.close()
        connection.close()

@router.get("/withdrawals/withdrawals_average_by_client", response_model=dict, tags=["withdrawals"])
async def get_average_withdrawals_by_client(client_full_name: str):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    try:
        select_query = """
        SELECT c.id_client, c.name, c.last_name, 
            AVG(w.amount) AS average_withdrawal
        FROM clients c
        INNER JOIN accounts a ON c.id_client = a.id_client
        INNER JOIN withdrawals w ON a.account_id = w.account_id
        WHERE CONCAT(c.name, ' ', c.last_name) = %s
        GROUP BY c.id_client
        """
        cursor.execute(select_query, (client_full_name,))
        average = cursor.fetchone()
        
        if not average:
            raise HTTPException(status_code=404, detail="Client not found or has no withdrawals")
        
        return {
            "client_id": average["id_client"],
            "client_full_name": f"{average['name']} {average['last_name']}",
            "average_withdrawal": average["average_withdrawal"] if average["average_withdrawal"] is not None else 0.0
        }
    except Error as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        cursor.close()
        connection.close()


@router.get("/withdrawals/count_and_amounts_by_client_and_date", response_model=dict, tags=["withdrawals"])
async def get_count_and_amounts_withdrawals_by_client_and_date(client_full_name: str, withdrawal_date: date):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    try:
        select_query = """
        SELECT c.id_client, c.name, c.last_name, 
            COUNT(w.withdrawal_id) AS withdrawal_count,
            GROUP_CONCAT(w.amount) AS withdrawal_amounts
        FROM clients c
        INNER JOIN accounts a ON c.id_client = a.id_client
        INNER JOIN withdrawals w ON a.account_id = w.account_id
        WHERE CONCAT(c.name, ' ', c.last_name) = %s
        AND w.withdrawal_date = %s
        GROUP BY c.id_client
        """
        cursor.execute(select_query, (client_full_name, withdrawal_date))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Client not found or has no withdrawals on this date")
        
        return {
            "client_id": result["id_client"],
            "client_full_name": f"{result['name']} {result['last_name']}",
            "withdrawal_count": result["withdrawal_count"] if result["withdrawal_count"] is not None else 0,
            "withdrawal_amounts": result["withdrawal_amounts"].split(',') if result["withdrawal_amounts"] else []
        }
    except Error as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        cursor.close()
        connection.close()

@router.get("/clients_by_employee", response_model=List[dict], tags=["clients"])
async def get_clients_with_employees(employee_name: str = None):  
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    try:
        select_query = """
        SELECT e.employee_id, e.name AS employee_name, e.position, 
            c.id_client, c.name AS client_name, c.last_name AS client_last_name
        FROM employees e
        RIGHT JOIN loans l ON e.employee_id = l.employee_id
        RIGHT JOIN accounts a ON l.ID_client = a.id_client
        RIGHT JOIN clients c ON a.id_client = c.id_client
        """
        
        if employee_name is not None:  
            select_query += " WHERE e.name = %s"
            cursor.execute(select_query, (employee_name,))
        else:
            cursor.execute(select_query)
        
        results = cursor.fetchall()
        
        return [
            {
                "employee_id": result["employee_id"],
                "employee_name": result["employee_name"] if result["employee_name"] else "No assigned employee",
                "position": result["position"] if result["position"] else "No position",
                "client_id": result["id_client"],
                "client_full_name": f"{result['client_name']} {result['client_last_name']}" if result["client_name"] else "No client name"
            }
            for result in results
        ]
    except Error as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        cursor.close()
        connection.close()

@router.get("/loans_status_by_client", response_model=List[dict], tags=["clients"])
async def get_clients_loan_status(client_full_name: str):  
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    try:
        select_query = """
        SELECT c.id_client, c.name AS client_name, c.last_name AS client_last_name,
            a.account_id, a.account_number, a.balance,
            l.loan_id, l.amount AS loan_amount, l.status AS loan_status
        FROM clients c
        LEFT JOIN accounts a ON c.id_client = a.id_client
        LEFT JOIN loans l ON a.id_client = l.ID_client
        WHERE CONCAT(c.name, ' ', c.last_name) = %s
        """
        cursor.execute(select_query, (client_full_name,))
        results = cursor.fetchall()
        
        if not results:
            raise HTTPException(status_code=404, detail="Client not found")
        
        return [
            {
                "client_id": result["id_client"],
                "client_full_name": f"{result['client_name']} {result['client_last_name']}",
                "account_id": result["account_id"],
                "account_number": result["account_number"],
                "balance": result["balance"],
                "loan_id": result["loan_id"],
                "loan_amount": result["loan_amount"] if result["loan_amount"] is not None else 0.0,
                "loan_status": result["loan_status"] if result["loan_status"] else "No loan"
            }
            for result in results
        ]
    except Error as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        cursor.close()
        connection.close()

@router.get("/accounts_above_min_balance", response_model=List[dict], tags=["accounts"])
async def get_accounts_above_balance(min_balance: float):  
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    try:
        select_query = """
        SELECT a.account_id, a.account_number, a.balance,
            c.id_client, c.name AS client_name, c.last_name AS client_last_name
        FROM accounts a
        LEFT JOIN clients c ON a.id_client = c.id_client
        WHERE a.balance > %s
        """
        cursor.execute(select_query, (min_balance,))
        results = cursor.fetchall()
        
        return [
            {
                "account_id": result["account_id"],
                "account_number": result["account_number"],
                "balance": result["balance"],
                "client_id": result["id_client"],
                "client_full_name": f"{result['client_name']} {result['client_last_name']}" if result["client_name"] else "No client"
            }
            for result in results
        ]
    except Error as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        cursor.close()
        connection.close()

@router.get("/count_accounts_above_min_balance", response_model=dict, tags=["accounts"])
async def count_accounts_above_balance(min_balance: float):  # Parámetro para el saldo mínimo
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    try:
        select_query = """
        SELECT COUNT(*) AS account_count
        FROM accounts
        WHERE balance > %s
        """
        cursor.execute(select_query, (min_balance,))
        result = cursor.fetchone()
        return {
            "min_balance": min_balance,
            "account_count": result["account_count"]
        }
    except Error as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        cursor.close()
        connection.close()

@router.get("/transfers_by_account_and_date_range", response_model=List[dict], tags=["transfers"])
async def transfers_by_account_and_date_range(start_date: date, end_date: date, from_account_number: str):  
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    try:
        select_query = """
        SELECT t.transfer_id, t.amount, t.transfer_date, t.transfer_method, t.status,
            ta.account_number AS to_account_number
        FROM transfers t
        JOIN accounts fa ON t.from_account_id = fa.account_id
        JOIN accounts ta ON t.to_account_id = ta.account_id
        WHERE fa.account_number = %s AND t.transfer_date BETWEEN %s AND %s
        """
        cursor.execute(select_query, (from_account_number, start_date, end_date))
        results = cursor.fetchall()
        
        if not results:
            raise HTTPException(status_code=404, detail="No transfers found for the specified account and date range.")
        
        return [
            {
                "transfer_id": result["transfer_id"],
                "amount": result["amount"],
                "transfer_date": result["transfer_date"],
                "transfer_method": result["transfer_method"],
                "status": result["status"],
                "to_account_number": result["to_account_number"]
            }
            for result in results
        ]
    except Error as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        cursor.close()
        connection.close()

@router.get("/transfers_count_total_amount_by_toaccount_and_date_range", response_model=dict, tags=["transfers"])
async def transfers_summary_to_specific_account(to_account_number: str, start_date: date, end_date: date):  
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    try:
        select_query = """
        SELECT COUNT(*) AS transfer_count, SUM(t.amount) AS total_amount
        FROM transfers t
        JOIN accounts ta ON t.to_account_id = ta.account_id
        WHERE ta.account_number = %s AND t.transfer_date BETWEEN %s AND %s
        """
        cursor.execute(select_query, (to_account_number, start_date, end_date))
        result = cursor.fetchone()
        
        return {
            "to_account_number": to_account_number,
            "start_date": start_date,
            "end_date": end_date,
            "transfer_count": result["transfer_count"],
            "total_amount": result["total_amount"] if result["total_amount"] is not None else 0.0
        }
    except Error as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        cursor.close()
        connection.close()

@router.get("/employee_details_by_name", response_model=dict, tags=["employees"])
async def get_employee_details_by_name(employee_name: str): 
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    try:
        select_query = """
        SELECT employee_id, name, position, hire_date
        FROM employees
        WHERE name = %s
        """
        cursor.execute(select_query, (employee_name,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        return {
            "employee_id": result["employee_id"],
            "name": result["name"],
            "position": result["position"],
            "hire_date": result["hire_date"]
        }
    except Error as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        cursor.close()
        connection.close()

@router.get("/loans_summary_by_name_employee", response_model=dict, tags=["employees"])
async def get_employees_loans_summary_by_name(employee_name: str):  
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    try:
        select_query = """
        SELECT e.employee_id, e.name, e.position, COUNT(l.loan_id) AS total_loans, SUM(l.amount) AS total_amount
        FROM employees e
        LEFT JOIN loans l ON e.employee_id = l.employee_id
        WHERE e.name = %s
        GROUP BY e.employee_id
        """
        cursor.execute(select_query, (employee_name,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Employee not found or has no loans")
        
        return {
            "employee_id": result["employee_id"],
            "name": result["name"],
            "position": result["position"],
            "total_loans": result["total_loans"],
            "total_amount": result["total_amount"] if result["total_amount"] is not None else 0.0
        }
    except Error as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        cursor.close()
        connection.close()

@router.get("/loans_above_min_amount", response_model=List[dict], tags=["loans"])
async def get_loans_above_amount(min_amount: float): 
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    try:
        select_query = """
        SELECT l.loan_id, l.ID_client, l.employee_id, 
            l.amount, l.interest_rate, l.disbursement_date, l.due_date, l.balance, l.status,
            c.name AS client_name, c.last_name AS client_last_name,
            e.name AS employee_name
        FROM loans l
        JOIN clients c ON l.ID_client = c.id_client
        JOIN employees e ON l.employee_id = e.employee_id
        WHERE l.amount >= %s
        """
        cursor.execute(select_query, (min_amount,))
        results = cursor.fetchall()
        return [
            {
                "loan_id": result["loan_id"],
                "client_full_name": f"{result['client_name']} {result['client_last_name']}",
                "employee_name": result["employee_name"],
                "amount": result["amount"],
                "interest_rate": result["interest_rate"],
                "disbursement_date": result["disbursement_date"],
                "due_date": result["due_date"],
                "balance": result["balance"],
                "status": result["status"]
            }
            for result in results
        ]
    except Error as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        cursor.close()
        connection.close()

@router.get("/withdrawals_sum_count_by_date_range_and_client", response_model=dict, tags=["withdrawals"])
async def withdrawals_summary_by_client(client_full_name: str, start_date: date, end_date: date):  
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    try:
        select_query = """
        SELECT COUNT(w.withdrawal_id) AS total_withdrawals, SUM(w.amount) AS total_amount
        FROM withdrawals w
        JOIN accounts a ON w.account_id = a.account_id
        JOIN clients c ON a.id_client = c.id_client
        WHERE CONCAT(c.name, ' ', c.last_name) = %s AND w.withdrawal_date BETWEEN %s AND %s
        """
        cursor.execute(select_query, (client_full_name, start_date, end_date))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="No withdrawals found for the specified client in the given date range.")
        
        return {
            "client_full_name": client_full_name,
            "start_date": start_date,
            "end_date": end_date,
            "total_withdrawals": result["total_withdrawals"],
            "total_amount": result["total_amount"] if result["total_amount"] is not None else 0.0
        }
    except Error as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        cursor.close()
        connection.close()

@router.get("/count_accounts_by_client", response_model=dict, tags=["clients"])
async def get_client_accounts_summary(client_full_name: str): 
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    try:
        select_query = """
        SELECT c.id_client, c.name, c.last_name, 
            COUNT(a.account_id) AS account_count,
            GROUP_CONCAT(a.account_number) AS account_numbers
        FROM clients c
        LEFT JOIN accounts a ON c.id_client = a.id_client
        WHERE CONCAT(c.name, ' ', c.last_name) = %s
        GROUP BY c.id_client
        """
        cursor.execute(select_query, (client_full_name,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Client not found or has no accounts")
        
        return {
            "client_id": result["id_client"],
            "client_full_name": f"{result['name']} {result['last_name']}",
            "account_count": result["account_count"],
            "accounts": result["account_numbers"].split(',') if result["account_numbers"] else []
        }
    except Error as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        cursor.close()
        connection.close()