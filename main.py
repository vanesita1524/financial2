from fastapi import FastAPI
from routes import router

tags_metadata = [
    {
        "name": "clients",
        "description": "Operations with Clients"},

    {   "name": "accounts",
        "description": "Operations with accounts"},

    {"name": "withdrawals",
    "description": "Operations with withdrawals"},

    {"name": "transfers",
    "description": "Operations with transfers"},
    
    {"name": "employees",
    "description": "Operations with employees"},

    {"name": "loans",
    "description": "Operations with loans"}
]

app = FastAPI(
    title="API Financial",
    openapi_tags=tags_metadata
)

app.include_router(router)

if __name__ == "_main_":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)