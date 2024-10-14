from models import Destination


class DestinationService:
    @staticmethod
    async def get_all() -> list[Destination]:
        return await Destination.find_all().to_list()

    @staticmethod
    async def create(destination: Destination) -> Destination:
        return await destination.insert()

    @staticmethod
    async def get_by_name(name: str) -> Destination | None:
        return await Destination.find_one(Destination.destination_name == name)

    @staticmethod
    async def update(name: str, destination: Destination) -> Destination | None:
        db_destination = await DestinationService.get_by_name(name)
        if db_destination:
            await db_destination.set({Destination.transport: destination.transport, Destination.url: destination.url})
            return db_destination
        return None

    @staticmethod
    async def delete(name: str) -> bool:
        destination = await DestinationService.get_by_name(name)
        if destination:
            await destination.delete()
            return True
        return False
