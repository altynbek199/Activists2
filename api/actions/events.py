from db.dals import EventsDAL
from db.models import EventsOrm
from sqlalchemy.dialects.postgresql import UUID
from api.schemas import EventAddDTO, EventShowDTO
from typing import Optional



async def _create_new_event(cred, session) -> EventShowDTO:
    async with session.begin():
        event_dal = EventsDAL(session)

        created_event_orm = await event_dal.create_event(
            title=cred.title,
            text=cred.text,
            author_id=cred.author_id,
            photo=cred.photo
        )

    event_show_dto = EventShowDTO.model_validate(created_event_orm, from_attributes=True)
    return event_show_dto



async def _delete_event(event_id, session) -> Optional[UUID]:
    async with session.begin():
        event_dal = EventsDAL(session)

        deleted_user_id = await event_dal.delete_event(event_id=event_id)

        return deleted_user_id



async def _get_events(session) -> list[EventsOrm]:
    events_dal = EventsDAL(session)
    return await events_dal.get_events()

async def _get_event_by_id(event_id, session) -> EventsOrm:
    event_dal = EventsDAL(session)
    return await event_dal.get_event_by_id(event_id=event_id)

