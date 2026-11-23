from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.database import init_db
from app.routers import auth, fundamentals, market, watchlist

import app.models.user
import app.models.watchlist
import app.models.refresh_token 




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
app.include_router(watchlist.router)
app.include_router(market.router)
app.include_router(fundamentals.router)

@app.get("/")
async def root():
    return {"message": "Stock Terminal works"}