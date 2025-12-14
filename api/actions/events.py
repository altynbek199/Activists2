from db.dals import EventsDAL
from db.models.models import EventsOrm
from sqlalchemy.dialects.postgresql import UUID
from api.schemas import EventAddDTO, EventShowDTO
from typing import Optional
import uuid
import datetime
from sqlalchemy.inspection import inspect
import redis.asyncio as redis_async
import asyncio
import json
from pydantic import TypeAdapter
from settings import settings


redis_client = redis_async.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT,password=settings.REDIS_PASS , decode_responses=True)

async def redis_available():
    try:
        return await redis_client.ping()
    except:
        return False

def orm_to_dict(obj: EventsOrm):
    dict1 = {}
    for c in inspect(obj).mapper.column_attrs:
        value = getattr(obj, c.key)
            
        dict1[c.key] = str(value)


    return dict1


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
    if await redis_available():
        keys = await redis_client.keys("events:page:*")
        if keys:
            await redis_client.delete(*keys)
    return event_show_dto



async def _delete_event(event_id, session) -> Optional[UUID]:
    async with session.begin():
        event_dal = EventsDAL(session)
        deleted_event_id = await event_dal.delete_event(event_id=event_id)
    return deleted_event_id

hit = 0
miss = 0

adapter = TypeAdapter(list[EventShowDTO])

async def _get_events_limit_10_by_page(page: int, session) -> list[EventsOrm]:
    global hit, miss
    cache_key = f"events:page:{page}"

    try:
        if await redis_available():

            cached_data = await redis_client.get(cache_key)
            
            if cached_data:
                hit += 1
                events_dto = adapter.validate_json(cached_data)
                return [EventsOrm(**dto.model_dump()) for dto in events_dto]
                
    except Exception as e:
        print(f"Redis error (read): {e}")
    miss += 1
    start = 10 * (page - 1)
    events_dal = EventsDAL(session)
    events_orm_list = await events_dal.get_events_limit_10(offset=start)
    
    if not events_orm_list:
        return []
    if await redis_available():
        asyncio.create_task(cache_page_data(cache_key, events_orm_list))

    return events_orm_list

async def cache_page_data(key: str, events_orm: list[EventsOrm]):
    try:
        events_dto = [EventShowDTO.model_validate(e, from_attributes=True) for e in events_orm]
        
        json_data = adapter.dump_json(events_dto).decode('utf-8')
        
        await redis_client.set(key, json_data, ex=600)
        
    except Exception as e:
        print(f"Redis error (write): {e}")

async def _get_event_by_id(event_id, session) -> EventsOrm:
    async with session.begin():
        event_dal = EventsDAL(session)
        return await event_dal.get_event_by_id(event_id=event_id)

