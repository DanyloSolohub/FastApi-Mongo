from httpx import AsyncClient
from models import Destination, TransportType, User
from services.auth import AuthService


async def create_user(username, password) -> User:
    return await User(username=username, hashed_password=AuthService.get_password_hash(password)).insert()


async def get_user_token_headers(client: AsyncClient, login_data) -> dict[str, str]:
    r = await client.post('api/v1/accounts/token', data=login_data)
    tokens = r.json()
    a_token = tokens['access_token']
    headers = {'Authorization': f'Bearer {a_token}'}
    return headers


async def create_destinations(data: list[dict]):
    destinations = []
    for entry in data:
        destination = Destination(
            destination_name=entry['destinationName'], transport=TransportType(entry['transport']), url=entry.get('url')
        )
        destinations.append(destination)

    await Destination.insert_many(destinations)
