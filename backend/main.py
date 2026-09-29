from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.delays import router as delays_router
from backend.routes.batteries import router as batteries_router
from backend.routes.analytics import router as analytics_router

# ==========================================
# CREATE FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title="Coke Oven Battery Delay Monitoring System",
    description="API for monitoring and analyzing coke oven battery delay records.",
    version="1.0.0"
)


# ==========================================
# CORS CONFIGURATION
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# REGISTER API ROUTES
# ==========================================

app.include_router(delays_router)
app.include_router(batteries_router)
app.include_router(analytics_router)

# ==========================================
# ROOT ENDPOINT
# ==========================================

@app.get("/")
def root():

    return {
        "message": "Coke Oven Battery Delay Monitoring API",
        "status": "running"
    }


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }