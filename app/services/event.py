import ast
import logging
from collections.abc import Callable

import httpx
from models import (
    Destination,
    EventLog,
    EventRequest,
    RoutingIntentRequest,
    RoutingResult,
    Strategy,
    StrategyEnum,
    TransportType,
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EventService:
    @classmethod
    async def process_event(cls, event: EventRequest) -> list[RoutingResult]:
        destinations = await Destination.find_all().to_list()
        results = []
        try:
            strategy_func = await cls.get_strategy_function(event.strategy)
        except ValueError as e:
            error = str(e)
            results.append(RoutingResult(destination_name='', routed=False, error=error))
        else:
            for intent in event.routing_intents:
                filtered_intent = strategy_func([dict(intent)])
                if not filtered_intent:
                    results.append(
                        RoutingResult(
                            destination_name=intent.destination_name, routed=False, error='Intent was filtered out'
                        )
                    )
                    continue
                destination = next((d for d in destinations if d.destination_name == intent.destination_name), None)
                if not destination:
                    results.append(
                        RoutingResult(
                            destination_name=intent.destination_name, routed=False, error='Destination not found'
                        )
                    )
                    continue
                routing_result = await cls.route_event(intent, event, destination)
                results.append(routing_result)
        await EventLog(request=event, response=results).insert()
        return results

    @staticmethod
    async def get_strategy_function(
        strategy: StrategyEnum | str | None,
    ) -> Callable[[list[RoutingIntentRequest]], list[RoutingIntentRequest]]:
        if strategy is None:
            strategy = await Strategy.find(Strategy.is_default == True).first_or_none()
            strategy = strategy.name if strategy else None
        if strategy == StrategyEnum.ALL:
            return lambda intents: intents
        elif strategy == StrategyEnum.IMPORTANT:
            return lambda intents: [intent for intent in intents if intent.get('important')]
        elif strategy == StrategyEnum.SMALL:
            return lambda intents: [intent for intent in intents if intent.get('bytes') and intent.get('bytes') < 1024]
        elif isinstance(strategy, str):
            try:
                tree = ast.parse(strategy, mode='eval')
                if isinstance(tree.body, ast.Lambda):
                    return eval(compile(tree, '<string>', 'eval'))
                else:
                    raise ValueError('Invalid strategy: must be a lambda function')
            except Exception as e:
                raise ValueError(f'Error parsing custom strategy: {str(e)}')
        else:
            raise ValueError('Invalid strategy type')

    @classmethod
    async def route_event(cls, intent: RoutingIntentRequest, event: EventRequest, destination: Destination):
        try:
            await cls._route_event(event.payload, destination)
        except Exception as e:
            return RoutingResult(destination_name=intent.destination_name, routed=False, error=str(e))
        else:
            return RoutingResult(destination_name=intent.destination_name, routed=True)

    @staticmethod
    async def _route_event(payload: dict, destination: Destination):
        if destination.transport in [TransportType.HTTP_POST, TransportType.HTTP_PUT, TransportType.HTTP_GET]:
            async with httpx.AsyncClient() as client:
                if destination.transport == TransportType.HTTP_POST:
                    await client.post(str(destination.url), json=payload)
                elif destination.transport == TransportType.HTTP_PUT:
                    await client.put(str(destination.url), json=payload)
                elif destination.transport == TransportType.HTTP_GET:
                    await client.get(str(destination.url), params=payload)
        elif destination.transport == TransportType.LOG_INFO:
            logger.info(f'Payload for {destination.destination_name}: {payload}')
        elif destination.transport == TransportType.LOG_WARN:
            logger.warning(f'Payload for {destination.destination_name}: {payload}')
