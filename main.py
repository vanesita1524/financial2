from fastapi import FastAPI
from routes import router

tags_metadata = [
    {
        "name": "clients",
        "description": "Operaciones para la gestión de clientes"},

    {   "name": "accounts",
        "description": "operaciones con cuentas"
    }
]

app = FastAPI(
    title="API Financial",
    openapi_tags=tags_metadata
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
