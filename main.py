from fastapi import FastAPI
from app.api import health

app = FastAPI(Title="BSC Conversational Product Assistant")

app.include_router(health.router)