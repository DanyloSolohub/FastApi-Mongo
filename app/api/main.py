from api.routes import accounts, destination, event, strategy
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(accounts.router, prefix='/accounts', tags=['accounts'])
api_router.include_router(destination.router, prefix='/destinations', tags=['destinations'])
api_router.include_router(event.router, prefix='/events', tags=['events'])
api_router.include_router(strategy.router, prefix='/strategy', tags=['strategy'])
