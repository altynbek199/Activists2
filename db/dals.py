from sqlalchemy.ext.asyncio import AsyncSession
from db.models import UsersOrm, PortalRole
from sqlalchemy.dialects.postgresql import UUID
from typing import Optional
from sqlalchemy import select, update, delete

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










