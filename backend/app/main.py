from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import sessions
from app.core.config import settings

app = FastAPI(
    title="RP Realtime API",
    description="Role-play conversation practice with real-time feedback",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sessions.router)


@app.get("/")
async def root():
    return {
        "message": "RP Realtime API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
