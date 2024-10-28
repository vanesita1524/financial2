from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
import uvicorn
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

load_dotenv()

tags_metadata = [
    {
        "name": "clients",
        "description": "Operaciones con clientes"
    }
]

app = FastAPI(
    title="API Financial",
    openapi_tags=tags_metadata
)

# Configuración de la base de datos MySQL
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None

# Modelos Pydantic para la validación de datos
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

# Métodos bulk
@app.post("/clients/bulk", response_model=List[ClientResponse], tags=["clients"])
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
        
        # Obtener los IDs de los clientes insertados
        cursor.execute("SELECT LAST_INSERT_ID()")
        last_id = cursor.fetchone()[0]
        
        return [ClientResponse(id_client=last_id+i, **client.dict()) for i, client in enumerate(clients)]
    
    except Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        cursor.close()
        connection.close()

# Otros endpoints...

class ClientList(BaseModel):
    clients: List[ClientResponse]

@app.get("/clients", response_model=List[ClientResponse], tags=["clients"])
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)