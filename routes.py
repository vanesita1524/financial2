from fastapi import APIRouter, HTTPException
from typing import List
from conexion import get_db_connection
from models import ClientCreate, ClientResponse, AccountCreate, AccountResponse
from mysql.connector import Error
#rutas
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

@router.post("/accounts", response_model=AccountResponse, tags=["accounts"])
async def create_account(account: AccountCreate, client_full_name: str):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    try:
        # Obtener el ID del cliente a partir del nombre completo
        cursor.execute("SELECT id_client FROM clients WHERE CONCAT(name, ' ', last_name) = %s", (client_full_name,))
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
        SELECT account_id, id_client, account_number, balance
        FROM accounts
        """
        cursor.execute(select_query)
        accounts = cursor.fetchall()
        
        return [AccountResponse(**account) for account in accounts]
    
    except Error as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        cursor.close()
        connection.close()
