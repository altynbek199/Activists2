from schemas import UserAddDTO, UserShowDTO, DeleteUserResponse, UpdatedUserResponse, UpdateUserRequest
from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from logging import getLogger
from actions.user import _create_new_user, _delete_user, _get_user_by_email, _get_user_by_id, _update_user, check_user_permission
from actions.auth import get_current_user_from_token
from sqlalchemy.dialects.postgresql import UUID 
from db.models import UsersOrm


logger = getLogger(__name__)

user_router = APIRouter()

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
       user_id: UUID,
       db: AsyncSession = Depends(get_db),
       current_user: UsersOrm = Depends(get_current_user_from_token)
) -> DeleteUserResponse:
       # check for deletion and existence
       user_for_deletion = _get_user_by_id(user_id=user_id)
       if user_for_deletion is None:
              raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found")

       if not await check_user_permission(
             target_user=user_for_deletion,
             current_user=current_user
       ):
              raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
       
       deleted_user_id = await _delete_user(user_id=user_id)
       if deleted_user_id is None:
              raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found ")
       return DeleteUserResponse(deleted_user_id)

@user_router.get("/", response_model=UUID)
async def get_user_by_uuid(
       user_id: UUID,
       db: AsyncSession = Depends(get_db),
       current_user: UsersOrm = Depends(get_current_user_from_token)
) -> UsersOrm:
       user = await _get_user_by_id(user_id=user_id, session=db)
       if user is None:
              raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found")
       return user

@user_router.patch("/", response_model=UpdatedUserResponse)
async def update_user(
       user_id: UUID,
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
       
       user = _get_user_by_id(user_id=user_id)
       if user is None:
              raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found")
       
       if not check_user_permission(
              target_user=user_id,
              current_user=current_user
       ):
              raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
       try:
              updated_user_id = _update_user(user_id=user_id, updated_user_params=update_user_params, session=db)
       except IntegrityError as err:
              logger.error(err)
              raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database error: {err}")
       return UpdatedUserResponse(updated_user_id=updated_user_id)


@user_router.patch("/admin_privilege_grant", response_model=UpdatedUserResponse)
async def grant_admin_privilege(
       user_id: UUID,
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
       return updated_user_id

       

@user_router.patch("/admin_privilege_revoke", response_model=UpdatedUserResponse)
async def revoke_admin_privilege(
       user_id: UUID,
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
       return updated_user_id
