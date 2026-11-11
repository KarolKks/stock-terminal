from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.database import init_db
from app.routers import auth
import app.models.user  

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title="Stock Terminal API",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(auth.router)

@app.get("/")
async def root():
    return {"message": "Stock Terminal works"}