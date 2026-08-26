import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "Admin"
    AUDITOR = "Auditor"
    SYSTEM = "System"
    USER = "User"


class ActionType(str, enum.Enum):
    READ = "READ"
    WRITE = "WRITE"
    DELETE = "DELETE"
    EXPORT = "EXPORT"


class StatusType(str, enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)
    logs: Mapped[list["AuditLog"]] = relationship("AuditLog", back_populates="user")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    action: Mapped[ActionType] = mapped_column()
    resource_type: Mapped[str] = mapped_column(index=True, nullable=False)
    resource_id: Mapped[str] = mapped_column(index=True, nullable=False)
    status: Mapped[StatusType] = mapped_column(nullable=False)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    user = relationship("User", back_populates="logs")
