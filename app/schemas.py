from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models import ActionType, StatusType, UserRole


class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: UUID
    username: str
    role: UserRole
    model_config = ConfigDict(from_attributes=True)


class AuditLogCreate(BaseModel):
    action: ActionType
    resource_type: str
    resource_id: str
    status: StatusType
    details: dict[str, Any] | None = None


class AuditLogResponse(BaseModel):
    id: UUID
    timestamp: datetime
    user_id: UUID
    model_config = ConfigDict(from_attributes=True)
    action: ActionType
    resource_type: str
    resource_id: str
    status: StatusType
    details: dict[str, Any] | None = None


class Token(BaseModel):
    access_token: str
    token_type: str
