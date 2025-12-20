from db.database import Base
from typing import Annotated
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID 
from sqlalchemy import String, ARRAY, func, ForeignKey
from enum import  StrEnum
from datetime import datetime, timezone
from sqlalchemy import DateTime 

def _utc_now():
    return datetime.now(timezone.utc)


str_256 = Annotated[str, mapped_column(String(256))]
uidpk = Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]
created_at = Annotated[datetime, mapped_column(
    DateTime(timezone=True),
    server_default=func.now()
)]

updated_at = Annotated[datetime, mapped_column(
    DateTime(timezone=True),
    server_default=func.now(), 
    onupdate=_utc_now
)]
class PortalRole(StrEnum):
    ROLE_PORTAL_USER = "ROLE_PORTAL_USER"
    ROLE_PORTAL_ADMIN = "ROLE_PORTAL_ADMIN"
    ROLE_PORTAL_SUPERADMIN = "ROLE_PORTAL_SUPERADMIN"


class UsersOrm(Base):
    __tablename__ = "users"

    user_id: Mapped[uidpk]
    name: Mapped[str_256]
    email: Mapped[str_256] = mapped_column(unique=True, index=True)
    created_at: Mapped[created_at]

    hashed_password: Mapped[str_256] 
    roles: Mapped[set[str]] = mapped_column(ARRAY(String))

    events: Mapped[list["EventsOrm"]] = relationship("EventsOrm", back_populates="author")

    @property
    def is_superadmin(self) -> bool:
        return PortalRole.ROLE_PORTAL_SUPERADMIN in self.roles 

    @property
    def is_admin(self) -> bool:
        return PortalRole.ROLE_PORTAL_ADMIN in self.roles 
    
    def enrich_admin_roles_by_admin_role(self):
        if not self.is_admin:
            return {*self.roles, PortalRole.ROLE_PORTAL_ADMIN}
    
    def remove_admin_role_from_model(self):
        if self.is_admin:
            return {role for role in self.roles if role != PortalRole.ROLE_PORTAL_ADMIN}


class EventsOrm(Base):
    __tablename__ = "events"

    event_id: Mapped[uidpk]
    title: Mapped[str_256] 
    text: Mapped[str]
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"))
    photo: Mapped[str | None]
    likes: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    author:  Mapped["UsersOrm"] = relationship("UsersOrm", back_populates="events")

