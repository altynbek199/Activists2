from api.schemas import UserAddDTO, UserShowDTO, DeleteUserResponse, UpdatedUserResponse, UpdateUserRequest, EventAddDTO, EventShowDTO, DeleteEventResponse
from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from logging import getLogger
from api.actions.user import (_create_new_user, _delete_user, _get_user_by_email,
_get_user_by_id, _update_user, check_user_permission, _get_users) 
from api.actions.auth import get_current_user_from_token
from sqlalchemy.dialects.postgresql import UUID 
from db.models.models import UsersOrm, EventsOrm
import uuid
from api.actions.events import _create_new_event, _delete_event, _get_events_limit_10_by_page, _get_event_by_id

logger = getLogger(__name__)

user_router = APIRouter()

#######################
# User
#######################



@user_router.post("/", response_model=UserShowDTO)
async def create_user(
        cred: UserAddDTO,
        db: AsyncSession = Depends(get_db)
) -> UserShowDTO:
        try:
              return await _create_new_user(cred, db)
        except IntegrityError as err:
              logger.error(err)
              raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f'Database erroe: {err}')
        
@user_router.delete("/", response_model=DeleteUserResponse)
async def delete_user(
       user_id: uuid.UUID,
       db: AsyncSession = Depends(get_db),
       current_user: UsersOrm = Depends(get_current_user_from_token)
) -> DeleteUserResponse:
       # check for deletion and existence
       user_for_deletion = await _get_user_by_id(user_id=user_id, session=db)
       if user_for_deletion is None:
              raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found")

       if not await check_user_permission(
             target_user=user_for_deletion,
             current_user=current_user
       ):
              raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
       
       deleted_user_id = await _delete_user(user_id=user_id, session=db)
       if deleted_user_id is None:
              raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User    with id {user_id} not found ")
       return DeleteUserResponse(deleted_user_id=deleted_user_id)

@user_router.get("/", response_model=UserShowDTO)
async def get_user_by_uuid(
       user_id: uuid.UUID,
       db: AsyncSession = Depends(get_db),
       current_user: UsersOrm = Depends(get_current_user_from_token)
) -> UserShowDTO:
       user = await _get_user_by_id(user_id=user_id, session=db)
       if user is None:
              raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found")
       return user

@user_router.patch("/", response_model=UpdatedUserResponse)
async def update_user(
       user_id: uuid.UUID,
       body: UpdateUserRequest,
       db: AsyncSession = Depends(get_db),
       current_user: UsersOrm = Depends(get_current_user_from_token)
) -> UpdatedUserResponse:
       
       # check if there is params in body
       update_user_params = body.model_dump(exclude_none=True)
       if update_user_params == {}:
              raise HTTPException(
                     status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                     detail="At least one parameter for user update info should be provided"
              )
       
       user_for_update = await _get_user_by_id(user_id=user_id, session=db)
       if user_for_update is None:
              raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found")
       
       if not await check_user_permission(
              target_user=user_for_update,
              current_user=current_user
       ):
              raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
       try:
              updated_user_id = await _update_user(user_id=user_id, updated_user_params=update_user_params, session=db)
       except IntegrityError as err:
              logger.error(err)
              raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database error: {err}")
       return UpdatedUserResponse(updated_user_id=updated_user_id)


@user_router.get("/users", response_model=list[UserShowDTO])
async def get_users(
       db: AsyncSession = Depends(get_db),
       current_user: UsersOrm = Depends(get_current_user_from_token)
) -> list[UserShowDTO]:
       if not(current_user.is_admin, current_user.is_superadmin):
              raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
       users = await _get_users(session=db)
       if users is None:
              raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Users not found")
       return users

@user_router.patch("/admin_privilege_grant", response_model=UpdatedUserResponse)
async def grant_admin_privilege(
       user_id: uuid.UUID,
       db: AsyncSession = Depends(get_db),
       current_user: UsersOrm = Depends(get_current_user_from_token)
) -> UpdatedUserResponse:
       if not current_user.is_superadmin:
              raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
       if current_user.user_id == user_id:
              raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot manage privileges of itself")
       
       user_for_promotion = await _get_user_by_id(user_id=user_id, session=db)
       if user_for_promotion is None:
              raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found")
       if user_for_promotion.is_admin or user_for_promotion.is_superadmin:
              raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"User with id {user_id} already promoted to admin/superadmin")
       updated_user_params = {
              "roles": user_for_promotion.enrich_admin_roles_by_admin_role()
       }
       try:
              updated_user_id = await _update_user(
                     user_id=user_id,
                     updated_user_params=updated_user_params,
                     session=db
              ) 
       except IntegrityError as err:
              logger.error(err)
              raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database error: {err}")
       return UpdatedUserResponse(updated_user_id=updated_user_id)

       

@user_router.patch("/admin_privilege_revoke", response_model=UpdatedUserResponse)
async def revoke_admin_privilege(
       user_id: uuid.UUID,
       db: AsyncSession = Depends(get_db),
       current_user: UsersOrm = Depends(get_current_user_from_token)
) -> UpdatedUserResponse:
       if not current_user.is_superadmin:
              raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
       if current_user.user_id == user_id:
              raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot manage privileges of itself")
       
       user_for_promotion = await _get_user_by_id(user_id=user_id, session=db)
       if user_for_promotion is None:
              raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found")
       if not (user_for_promotion.is_admin or user_for_promotion.is_superadmin):
              raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"User with id {user_id} is not admin")
       updated_user_params = {
              "roles": user_for_promotion.remove_admin_role_from_model()
       }
       try:
              updated_user_id = await _update_user(
                     user_id=user_id,
                     updated_user_params=updated_user_params,
                     session=db
              ) 
       except IntegrityError as err:
              logger.error(err)
              raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database error: {err}")
       return UpdatedUserResponse(updated_user_id=updated_user_id)


####################
# Events
####################

event_router = APIRouter()


@event_router.post("/add", response_model=EventShowDTO)
async def create_events(
        cred: EventAddDTO,
        db: AsyncSession = Depends(get_db),
        current_user: UsersOrm = Depends(get_current_user_from_token)
) -> EventShowDTO:
        
       if not (current_user.is_admin or current_user.is_superadmin):
              raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
       author = await _get_user_by_id(user_id=cred.author_id, session=db)
       if author is None:
              raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {cred.author_id} not found" )
       if not (author.is_admin or author.is_superadmin):
              raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Author must be admin/superadmin")

       try:
              return await _create_new_event(cred, db)
       except IntegrityError as err:
              logger.error(err)
              raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f'Database erroe: {err}')
        
@event_router.delete("/delete", response_model=DeleteEventResponse)
async def delete_event(
       event_id: uuid.UUID,
       db: AsyncSession = Depends(get_db),
       current_user: UsersOrm = Depends(get_current_user_from_token)
) -> DeleteEventResponse:
       # check for deletion and existence

       if not (current_user.is_admin or current_user.is_superadmin):
              raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
       
       event_for_deletion = await _get_event_by_id(event_id=event_id, session=db)
       if event_for_deletion is None:
              raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event with id {event_id} not found")

       
       
       deleted_event_id = await _delete_event(event_id=event_id, session=db)
       if deleted_event_id is None:
              raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event    with id {event_id} not found ")
       return DeleteEventResponse(deleted_event_id=deleted_event_id)

@event_router.get("/get", response_model=list[EventShowDTO])
async def get_events_limit_10_by_page(
       page: int,
       db: AsyncSession = Depends(get_db)
) -> list[EventShowDTO]:
       events = await _get_events_limit_10_by_page(page=page, session=db)
       if events is None:
              raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Events not found")

       return events