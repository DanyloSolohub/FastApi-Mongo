import json

from core.db import initiate_database
from models import Destination, Strategy, StrategyEnum, TransportType


def load_data_from_json(file_path: str) -> dict[str, list[dict]]:
    with open(file_path) as file:
        return json.load(file)


async def create_destinations(data: list[dict]):
    destinations = []
    for entry in data:
        destination = Destination(
            destination_name=entry['destinationName'], transport=TransportType(entry['transport']), url=entry.get('url')
        )
        destinations.append(destination)

    await Destination.insert_many(destinations)


async def create_strategies(data: list[dict]):
    strategies = []
    for entry in data:
        strategy = Strategy(
            name=StrategyEnum[entry['name']],
            is_default=entry['is_default'],
        )
        strategies.append(strategy)

    await Strategy.insert_many(strategies)


async def main():
    await initiate_database()
    data = load_data_from_json('initial_data.json')
    await create_destinations(data.get('destination'))
    await create_strategies(data.get('strategy'))


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
