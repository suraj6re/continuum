from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import connect_db, close_db
from app.routes import upload, analysis
import os

app = FastAPI(title="StructIQ API", version="1.0.0")

# CORS middleware - MUST be before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Startup event
@app.on_event("startup")
async def startup_event():
    await connect_db()
    # Ensure uploads directory exists
    upload_dir = os.getenv("UPLOAD_DIR", "../uploads")
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    await close_db()

# Include routers
app.include_router(upload.router)
app.include_router(analysis.router)

# Mount uploads directory as static files - AFTER routes
upload_dir = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(upload_dir, exist_ok=True)  # Ensure directory exists
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

@app.get("/")
async def root():
    return {"message": "StructIQ API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
