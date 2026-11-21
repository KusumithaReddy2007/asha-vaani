import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.seed import seed_database
from app.api import auth, beneficiaries, visits, danger_signs, followups, analytics, voice_ws

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("asha_vaani_main")

# Initialize database tables and benchmark synthetic data
seed_database()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("ASHA-VAANI Core System startup complete.")
    yield
    logger.info("Shutting down ASHA-VAANI...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="ASHA-VAANI: AI-Powered Healthcare Voice Assistant for Maternal and Child Healthcare visits (Build Bengaluru 2.0 PS1)",
    lifespan=lifespan
)

# CORS setup for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(beneficiaries.router)
app.include_router(visits.router)
app.include_router(danger_signs.router)
app.include_router(followups.router)
app.include_router(analytics.router)
app.include_router(voice_ws.router)

@app.get("/")
def read_root():
    return {
        "project": "ASHA-VAANI",
        "tagline": "Your Voice. Every Visit. Better Healthcare.",
        "event": "Build Bengaluru 2.0 Innovation Challenge, PS1 – Healthcare",
        "status": "ONLINE",
        "version": settings.APP_VERSION,
        "docs_url": "/docs",
        "endpoints": {
            "auth": "/api/auth",
            "beneficiaries": "/api/beneficiaries",
            "visits": "/api/visits",
            "danger_signs": "/api/danger-signs",
            "followups": "/api/followups",
            "analytics": "/api/analytics",
            "websocket_voice": "/ws/voice"
        }
    }
