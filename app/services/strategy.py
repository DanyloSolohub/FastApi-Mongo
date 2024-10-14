from beanie import PydanticObjectId
from fastapi import HTTPException
from models import Strategy


class StrategyService:
    @staticmethod
    async def get_all_strategies() -> list:
        return await Strategy.find(Strategy.is_client_strategy == False).sort('-is_default').to_list()

    @staticmethod
    async def set_default_strategy(strategy_id: PydanticObjectId):
        strategy = await Strategy.get(strategy_id)
        if not strategy:
            raise HTTPException(status_code=404, detail='Strategy not found')
        if strategy.is_client_strategy:
            raise HTTPException(status_code=400, detail='Cannot set a client strategy as default')
        await Strategy.find({'is_default': True}).update({'$set': {'is_default': False}})
        strategy.is_default = True
        await strategy.save()
        return strategy
