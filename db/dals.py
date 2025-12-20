from sqlalchemy.ext.asyncio import AsyncSession
from db.models.models import UsersOrm, PortalRole, EventsOrm
from sqlalchemy.dialects.postgresql import UUID
from typing import Optional
from sqlalchemy import select, update, delete




#########
# User
#########

class UserDAL:
    """ Data Access Layer fro operating user info """
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(self, name: str, email: str, hashed_password: str, roles: list[PortalRole]) -> UsersOrm:
        new_user = UsersOrm(
            name=name,
            email=email,
            hashed_password=hashed_password,
            roles=roles,
        )

        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user
    
    async def delete_user(self, user_id: UUID) -> Optional[UUID]:
        query = (delete(UsersOrm)
                 .where(UsersOrm.user_id==user_id)
                 .returning(UsersOrm.user_id)
                 )
        res = await self.db_session.execute(query)
        deleted_user_id = res.scalars().one_or_none()
        return deleted_user_id
    
    async def update_user(self, user_id: UUID, **kwargs) -> Optional[UUID]:
        query = (
            update(UsersOrm)
            .where(UsersOrm.user_id==user_id)
            .values(kwargs)
            .returning(UsersOrm.user_id)
        )

        res = await self.db_session.execute(query)
        updated_user_id = res.scalars().one_or_none()
        return updated_user_id
    
    async def get_user_by_id(self, user_id: UUID) -> UsersOrm:
        query = (
            select(UsersOrm)
            .where(UsersOrm.user_id==user_id)
        )

        res = await self.db_session.execute(query)
        user_orm = res.scalars().one_or_none()
        return user_orm
    
    async def get_user_by_email(self, email: str) -> UsersOrm:
        query = (
            select(UsersOrm)
            .where(UsersOrm.email==email)
        )

        res = await self.db_session.execute(query)
        user_orm = res.scalars().one_or_none()
        return user_orm
    
    async def get_users(self) -> list[UsersOrm]:
        query = (
            select(UsersOrm)
        )

        res = await self.db_session.execute(query)
        users_orm = res.scalars().all()
        return users_orm


#########
# Event
#########

class EventsDAL:
    ''' DAL for operating events info'''

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_event(self, title: str, text: str, author_id: UUID, photo: Optional[str] = None) -> EventsOrm:
        new_event = EventsOrm(
            title=title,
            text=text,
            author_id=author_id,
            photo=photo
        )

        self.db_session.add(new_event)
        await self.db_session.flush()
        return new_event
    
    async def delete_event(self, event_id: UUID) -> Optional[UUID]:
        query = (delete(EventsOrm)
                 .where(EventsOrm.event_id==event_id)
                 .returning(EventsOrm.event_id)
                 )
        res = await self.db_session.execute(query)
        deleted_event_id = res.scalars().one_or_none()
        return deleted_event_id
    


    async def get_events_limit_10(self, offset) -> list[EventsOrm]:
        query = (
            select(EventsOrm)
            .order_by(EventsOrm.created_at.desc())
            .offset(offset)
            .limit(10)
        )
        res = await self.db_session.execute(query)
        events_orm = res.scalars().all()
        return events_orm
    
    async def get_event_by_id(self, event_id) -> EventsOrm:
        query = (
            select(EventsOrm)
            .where(EventsOrm.event_id==event_id)
        )
        res = await self.db_session.execute(query)
        events_orm = res.scalars().one_or_none()
        return events_orm
    
    async def update_photo(self, event_id, photo) -> Optional[UUID]:
        query = (
            update(EventsOrm)
            .where(EventsOrm.event_id==event_id)
            .values(photo=photo)
            .returning(EventsOrm.event_id)
        )

        res = await self.db_session.execute(query)
        response = res.scalars().one_or_none()
        return response








