from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.graph.neo4j_client import neo4j_client
from app.api.v1.router import api_router
from app.db.session import engine, Base
import app.db.models  # Registers SQLAlchemy models

# Create SQLite tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    neo4j_client.connect()
    yield
    await neo4j_client.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Ezitech AI Learning Engine API is operational"}