import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.endpoints import spotify, translation

logger = structlog.get_logger(__name__)

app = FastAPI(
    title="Spotify Translation Service",
    description="External service for Spotify metadata and translation operations",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(spotify.router, prefix="/spotify", tags=["spotify"])
app.include_router(translation.router, prefix="/translation", tags=["translation"])

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Spotify Translation Service")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Spotify Translation Service")
