from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.drawing import Drawing
from app.models.project import Project
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    client: AsyncIOMotorClient = None

db = Database()

async def connect_db():
    db.client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
    await init_beanie(
        database=db.client[os.getenv("DATABASE_NAME")],
        document_models=[Drawing, Project]
    )

async def close_db():
    db.client.close()
