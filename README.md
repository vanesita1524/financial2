# financial2
#  Financial API

API developed with **FastAPI** and **Streamlit** for the management and query of financial information of a company.  
The application connects to a **MySQL** database that contains the main system tables and allows common queries (**GET** and **POST**), using different types of `JOIN`.

---
## Project Structure
---

- .env                  # Environment variables (sensitive connection data)
- .gitignore            # Excludes sensitive files and virtualenv
- db_schema.sql         # Database logical schema (DDL)
- requirements.txt      # Project dependencies
- conexion.py           # Connection to MySQL database
- main.py               # API creation with FastAPI + tag definition
- models.py             # Pydantic BaseModels definition (for each table)
- routers/              # Organized API routes (GET and POST endpoints)
- .env.example          # Example of environment variables configuration

---
Technologies Used
---
- Python 3.10+

- FastAPI (backend framework)

- Streamlit (visual interface)

- MySQL (relational database)

- Uvicorn (ASGI server)

- dotenv (environment variable management)

- Pydantic (data validation)

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

1. Start the API with FastAPI:

---

uvicorn main:app --reload

---

Interactive documentation will be available at:


Swagger UI → http://127.0.0.1:8000/docs

ReDoc → http://127.0.0.1:8000/redoc

---
2. Run the interface with Streamlit:

---

streamlit run app.py

---
How It Works
---

---
Database connection

- conexion.py manages the MySQL connection using .env variables.

Credentials are protected with .gitignore.

- Data models

models.py defines Pydantic BaseModel classes to validate each table’s data.

- Routes and Endpoints

Routes are organized in the routers/ folder. Includes GET (queries, joins between tables) and POST (create records).
Endpoints are documented with tags in main.py for easy use in Swagger.

Imanges
<img width="1323" height="623" alt="image" src="https://github.com/user-attachments/assets/a09e6a26-28e8-46c7-940a-e4e7dd4592bf" />
<img width="1357" height="608" alt="image" src="https://github.com/user-attachments/assets/c451aef0-a961-41a8-b1bd-0d1a2f288c9f" />
<img width="1326" height="552" alt="image" src="https://github.com/user-attachments/assets/1e88b096-c36f-4713-93bd-36d97b8e4dee" />



