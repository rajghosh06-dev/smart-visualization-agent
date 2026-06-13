from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.routes import router
from core.parser import init_llm
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("smart_vis_agent")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the local LLM in a background thread
    logger.info("Starting up Smart Visualization Agent...")
    init_llm()
    yield
    # Shutdown: Clean up resources if needed
    logger.info("Shutting down Smart Visualization Agent...")

app = FastAPI(
    title="Smart Visualization Agent",
    description="An offline-first AI-powered dashboard for CSV/Excel data visualization.",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include the main router
app.include_router(router)
