from fastapi import FastAPI
from routes import router
#tags
tags_metadata = [
    {
        "name": "clients",
        "description": "Operaciones para la gestión de clientes"},

    {   "name": "accounts",
        "description": "operaciones con cuentas"},

    {"name": "withdrawals",
    "description": "operaciones con retiros"},

    {"name": "transfers",
    "description": "poperaciones con tranferencias"},
    
    {"name": "employees",
    "description": "operaciones empleados"},

    {"name": "loans",
    "description": "operaciones con préstamos"}
]

app = FastAPI(
    title="API Financial",
    openapi_tags=tags_metadata
)

app.include_router(router)

if __name__ == "_main_":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
