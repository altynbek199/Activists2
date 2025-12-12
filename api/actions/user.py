from api.schemas import UserShowDTO
from db.dals import UserDAL
from hashing import Hasher
from db.models.models import PortalRole, UsersOrm
from typing import Optional
from sqlalchemy.dialects.postgresql import UUID
import uuid

async def _create_new_user(cred, session) -> UserShowDTO:
    async with session.begin():
        user_dal = UserDAL(session)

        created_user_orm = await user_dal.create_user(
            name=cred.name,
            email=cred.email,
            hashed_password=Hasher.get_password_hash(cred.hashed_password),
            roles={PortalRole.ROLE_PORTAL_USER,}
        )

    user_show_dto = UserShowDTO.model_validate(created_user_orm, from_attributes=True)
    return user_show_dto



async def _delete_user(user_id, session) -> Optional[UUID]:
    async with session.begin():
        user_dal = UserDAL(session)

        deleted_user_id = await user_dal.delete_user(user_id=user_id)

        return deleted_user_id
    

async def _update_user(user_id, updated_user_params: dict, session) -> Optional[UUID]:
    async with session.begin():
        user_dal = UserDAL(session)

        updated_user_id = await user_dal.update_user(user_id=user_id, **updated_user_params)
        return updated_user_id
    
    
async def _get_user_by_id(user_id, session) -> UsersOrm:
    async with  session.begin():
        user_dal = UserDAL(session)
        return  await user_dal.get_user_by_id(user_id=user_id)

async def _get_user_by_email(email, session) -> UsersOrm:
    async with  session.begin():
        user_dal = UserDAL(session)
        return  await user_dal.get_user_by_email(email=email)
    

async def check_user_permission(target_user: UsersOrm, current_user: UsersOrm ) ->  bool:
    if PortalRole.ROLE_PORTAL_SUPERADMIN in target_user.roles:
        return False

    if target_user.user_id != current_user.user_id:
        #check admin role
        if not {
            PortalRole.ROLE_PORTAL_ADMIN,
            PortalRole.ROLE_PORTAL_SUPERADMIN
        }.intersection(set(current_user.roles)):
            return False

        #check admin deactivate superadmin attempt
        if (PortalRole.ROLE_PORTAL_ADMIN in current_user.roles 
            and PortalRole.ROLE_PORTAL_SUPERADMIN in target_user.roles):
            return False
        # check admin deactivate admin attempt
        if (PortalRole.ROLE_PORTAL_ADMIN in current_user.roles 
            and PortalRole.ROLE_PORTAL_ADMIN in target_user.roles):
            return False
    return True


async def _get_users(session) -> list[UsersOrm]:
    async with session.begin():
        users_dal = UserDAL(session)
        return await users_dal.get_users()



        






















