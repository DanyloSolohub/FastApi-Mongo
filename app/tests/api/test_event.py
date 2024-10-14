from unittest.mock import AsyncMock

import models
import pytest
from httpx import AsyncClient
from tests.utils.utils import create_destinations, create_user, get_user_token_headers


@pytest.mark.asyncio
async def test_event_all_strategy(mocker, client: AsyncClient):
    mocker.patch('services.event.EventService._route_event', new_callable=AsyncMock)
    await create_user('test', 'test')
    await models.Strategy(name=models.StrategyEnum.ALL, is_default=True).save()
    destinations = [
        {'destinationName': 'destination1', 'url': 'http://example.com/endpoint', 'transport': 'http.post'},
        {'destinationName': 'destination2', 'url': 'http://example2.com/endpoint', 'transport': 'http.get'},
        {'destinationName': 'destination3', 'transport': 'log.info'},
    ]
    await create_destinations(destinations)
    data = {
        'payload': {'a': 1},
        'routing_intents': [
            {'destination_name': 'destination1'},
            {'destination_name': 'destination2'},
            {'destination_name': 'destination3'},
            {'destination_name': 'destination4'},
            {'destination_name': 'destination5'},
        ],
    }
    response = await client.post(
        'api/v1/events/',
        headers=await get_user_token_headers(client, {'username': 'test', 'password': 'test'}),
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content == [
        {'destination_name': 'destination1', 'routed': True, 'error': None},
        {'destination_name': 'destination2', 'routed': True, 'error': None},
        {'destination_name': 'destination3', 'routed': True, 'error': None},
        {'destination_name': 'destination4', 'routed': False, 'error': 'Destination not found'},
        {'destination_name': 'destination5', 'routed': False, 'error': 'Destination not found'},
    ]


@pytest.mark.asyncio
async def test_event_important_strategy(mocker, client: AsyncClient):
    mocker.patch('services.event.EventService._route_event', new_callable=AsyncMock)
    await create_user('test', 'test')
    await models.Strategy(name=models.StrategyEnum.IMPORTANT, is_default=True).save()
    destinations = [
        {'destinationName': 'destination1', 'url': 'http://example.com/endpoint', 'transport': 'http.post'},
        {'destinationName': 'destination2', 'url': 'http://example2.com/endpoint', 'transport': 'http.get'},
        {'destinationName': 'destination3', 'transport': 'log.info'},
    ]
    await create_destinations(destinations)
    data = {
        'payload': {'a': 2},
        'routing_intents': [
            {'destination_name': 'destination1', 'important': True},
            {'destination_name': 'destination2', 'important': False},
            {'destination_name': 'destination3', 'important': True},
            {'destination_name': 'destination4', 'important': False},
            {'destination_name': 'destination5', 'important': True},
        ],
    }
    response = await client.post(
        'api/v1/events/',
        headers=await get_user_token_headers(client, {'username': 'test', 'password': 'test'}),
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content == [
        {'destination_name': 'destination1', 'routed': True, 'error': None},
        {'destination_name': 'destination2', 'routed': False, 'error': 'Intent was filtered out'},
        {'destination_name': 'destination3', 'routed': True, 'error': None},
        {'destination_name': 'destination4', 'routed': False, 'error': 'Intent was filtered out'},
        {'destination_name': 'destination5', 'routed': False, 'error': 'Destination not found'},
    ]


@pytest.mark.asyncio
async def test_event_user_strategy(mocker, client: AsyncClient):
    mocker.patch('services.event.EventService._route_event', new_callable=AsyncMock)
    await create_user('test', 'test')
    await models.Strategy(name=models.StrategyEnum.ALL, is_default=True).save()
    destinations = [
        {'destinationName': 'destination1', 'url': 'http://example.com/endpoint', 'transport': 'http.post'},
        {'destinationName': 'destination2', 'url': 'http://example2.com/endpoint', 'transport': 'http.get'},
        {'destinationName': 'destination3', 'transport': 'log.info'},
    ]
    await create_destinations(destinations)
    data = {
        'payload': {'a': 1},
        'strategy': "lambda routing_intents: [intent for intent in routing_intents if intent.get('score', 0) < 0]",
        'routing_intents': [
            {'destination_name': 'destination1', 'score': 1},
            {'destination_name': 'destination2', 'score': -1},
            {'destination_name': 'destination3', 'score': 0},
            {'destination_name': 'destination4', 'score': -1},
            {'destination_name': 'destination5', 'score': 1},
        ],
    }
    response = await client.post(
        'api/v1/events/',
        headers=await get_user_token_headers(client, {'username': 'test', 'password': 'test'}),
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content == [
        {'destination_name': 'destination1', 'routed': False, 'error': 'Intent was filtered out'},
        {'destination_name': 'destination2', 'routed': True, 'error': None},
        {'destination_name': 'destination3', 'routed': False, 'error': 'Intent was filtered out'},
        {'destination_name': 'destination4', 'routed': False, 'error': 'Destination not found'},
        {'destination_name': 'destination5', 'routed': False, 'error': 'Intent was filtered out'},
    ]
