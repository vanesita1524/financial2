from fastapi import APIRouter, HTTPException
from typing import List
from conexion import get_db_connection
from models import ClientCreate, ClientResponse
from mysql.connector import Error

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
