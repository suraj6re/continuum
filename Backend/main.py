from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import connect_db, close_db
from app.routes import upload, analysis

app = FastAPI(title="StructIQ API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event
@app.on_event("startup")
async def startup_event():
    await connect_db()

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    await close_db()

# Include routers
app.include_router(upload.router)
app.include_router(analysis.router)

@app.get("/")
async def root():
    return {"message": "StructIQ API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
