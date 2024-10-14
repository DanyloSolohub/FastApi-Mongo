from fastapi import APIRouter, Depends
from models import EventRequest, RoutingResult, User
from services.auth import AuthService
from services.event import EventService

router = APIRouter()


@router.post('/', response_model=list[RoutingResult])
async def process_event(event: EventRequest, _current_user: User = Depends(AuthService.get_current_active_user)):
    return await EventService.process_event(event)
