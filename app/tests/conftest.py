import pytest
from asgi_lifespan import LifespanManager
from core.config import settings
from httpx import ASGITransport, AsyncClient
from main import app
from motor.motor_asyncio import AsyncIOMotorClient

settings.MONGO_URI = settings.TEST_MONGO_URI


@pytest.fixture(scope='function', autouse=True)
async def clear_test_db():
    yield
    client = AsyncIOMotorClient(settings.TEST_MONGO_URI)
    db = client.get_default_database()
    collections = await db.list_collection_names()
    for collection in collections:
        await db[collection].delete_many({})


@pytest.fixture
async def client():
    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test', follow_redirects=True) as ac:
            yield ac
