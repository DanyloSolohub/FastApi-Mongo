from fastapi import APIRouter, Depends, HTTPException
from models import Destination, User
from services.auth import AuthService
from services.destination import DestinationService

router = APIRouter()


@router.get('/', response_model=list[Destination])
async def get_destinations(_current_user: User = Depends(AuthService.get_current_active_user)):
    return await DestinationService.get_all()


@router.post('/', response_model=Destination)
async def create_destination(
    destination: Destination, _current_user: User = Depends(AuthService.get_current_active_user)
):
    return await DestinationService.create(destination)


@router.get('/{name}', response_model=Destination)
async def get_destination(name: str, _current_user: User = Depends(AuthService.get_current_active_user)):
    destination = await DestinationService.get_by_name(name)
    if destination is None:
        raise HTTPException(status_code=404, detail='Destination not found')
    return destination


@router.patch('/{name}', response_model=Destination)
async def update_destination(
    name: str, destination: Destination, _current_user: User = Depends(AuthService.get_current_active_user)
):
    updated_destination = await DestinationService.update(name, destination)
    if updated_destination is None:
        raise HTTPException(status_code=404, detail='Destination not found')
    return updated_destination


@router.delete('/{name}', response_model=bool)
async def delete_destination(name: str, _current_user: User = Depends(AuthService.get_current_active_user)):
    deleted = await DestinationService.delete(name)
    if not deleted:
        raise HTTPException(status_code=404, detail='Destination not found')
    return True
