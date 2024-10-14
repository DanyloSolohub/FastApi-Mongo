from beanie import PydanticObjectId
from fastapi import APIRouter, Depends
from models import Strategy, User
from services.auth import AuthService
from services.strategy import StrategyService

router = APIRouter()


@router.get('/', response_model=list[Strategy])
async def get_all_strategies(_current_user: User = Depends(AuthService.get_current_active_user)):
    return await StrategyService.get_all_strategies()


@router.patch('/{strategy_id}/set-default', response_model=Strategy)
async def set_default_strategy(
    strategy_id: PydanticObjectId, _current_user: User = Depends(AuthService.get_current_active_user)
):
    strategy = await StrategyService.set_default_strategy(strategy_id)
    return strategy
