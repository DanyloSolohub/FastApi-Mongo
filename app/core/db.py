from beanie import init_beanie
from core.config import settings
from models import models
from motor.motor_asyncio import AsyncIOMotorClient


async def initiate_database():
    client = AsyncIOMotorClient(settings.MONGO_URI)
    await init_beanie(
        database=client.get_default_database(),
        document_models=models,
    )
