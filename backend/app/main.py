from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import init_db
from app.routes import auth, assets, portfolio, risk, advisor, export

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Secure Portfolio Management API",
    description="India-first multi-asset portfolio management with hybrid AI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      
        "http://localhost:5173",
        "http://localhost:8080",      
        "http://127.0.0.1:8080", 
        "http://172.17.66.10:8080", 
        "http://172.17.70.179:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(assets.router)
app.include_router(portfolio.router)
app.include_router(risk.router)
app.include_router(advisor.router)
app.include_router(export.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("Database initialized")


@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Portfolio Management API",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "environment": settings.ENVIRONMENT
    }
