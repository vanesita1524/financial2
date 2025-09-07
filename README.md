# financial2
#  Financial API

API developed with **FastAPI** and **Streamlit** for the management and query of financial information of a company.  
The application connects to a **MySQL** database that contains the main system tables and allows common queries (**GET** and **POST**), using different types of `JOIN`.

---
## Project Structure
---
financial2/
│── .env                  # Environment variables (sensitive connection data)
│── .gitignore            # Excludes sensitive files and virtualenv
│── db_schema.sql         # Database logical schema (DDL)
│── requirements.txt      # Project dependencies
│── conexion.py           # Connection to MySQL database
│── main.py               # API creation with FastAPI + tag definition
│── models.py             # Pydantic BaseModels definition (for each table)
│── routers/              # Organized API routes (GET and POST endpoints)
│── .env.example          # Example of environment variables configuration

---
Technologies Used
---
Python 3.10+

FastAPI (backend framework)

Streamlit (visual interface)

MySQL (relational database)

Uvicorn (ASGI server)

dotenv (environment variable management)

Pydantic (data validation)

---
Database
---
The API works on a financial schema in **MySQL** with the following tables:

- **accounts** → Accounts information.  
- **clients** → Client data.  
- **employees** → Employee data.  
- **loans** → Granted loans.  
- **transfers** → Performed transfers.  
- **withdrawals** → Money withdrawals.  

The file `db_schema.sql` contains the database schema definition.  

---

## Installation and Setup

1. Clone the repository:
```
git clone https://github.com/vanesita1524/financial2.git
cd financial2
```
2. Create and activate a virtual environment:
```
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```
3. Install dependencies:
```
pip install -r requirements.txt
```
---
4. Configure environment variables in the .env file (not included for security):
---
DB_HOST=localhost
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=financial_db

---
Run the Project
---

Start the API with FastAPI:

---

uvicorn main:app --reload

---

Interactive documentation will be available at:


Swagger UI → http://127.0.0.1:8000/docs

ReDoc → http://127.0.0.1:8000/redoc

---
Run the interface with Streamlit:

---

streamlit run app.py

---
How It Works
---

---
Database connection

conexion.py manages the MySQL connection using .env variables.

Credentials are protected with .gitignore.

Data models

models.py defines Pydantic BaseModel classes to validate each table’s data.

Routes and Endpoints

Routes are organized in the routers/ folder. Includes GET (queries, joins between tables) and POST (create records).
Endpoints are documented with tags in main.py for easy use in Swagger.
