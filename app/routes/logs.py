from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.exceptions import PermissionDeniedException, ResourceNotFoundException
from app.database import get_db
from app.models import AuditLog, User
from app.schemas import AuditLogCreate, AuditLogResponse

router = APIRouter(prefix="/logs", tags=["Audit Logs"])


@router.post("/", response_model=AuditLogResponse, status_code=status.HTTP_201_CREATED)
def create_audit_log(
    log_in: AuditLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_log = AuditLog(
        action=log_in.action,
        resource_type=log_in.resource_type,
        resource_id=log_in.resource_id,
        status=log_in.status,
        details=log_in.details,
        user_id=current_user.id,
    )

    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    return new_log


@router.get("/", response_model=list[AuditLogResponse])
def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(AuditLog)

    if current_user.role.value not in ["Admin", "Auditor", "System"]:
        query = query.filter(AuditLog.user_id == current_user.id)

    return query.offset(skip).limit(limit).all()


@router.get("/search", response_model=list[AuditLogResponse])
def search_audit_logs(
    action: str | None = None,
    target_user_id: UUID | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(AuditLog)

    if current_user.role.value not in ["Admin", "Auditor", "System"]:
        query = query.filter(AuditLog.user_id == current_user.id)
    else:
        if target_user_id:
            query = query.filter(AuditLog.user_id == target_user_id)

    if action:
        query = query.filter(AuditLog.action == action)
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)

    return query.offset(skip).limit(limit).all()


@router.get("/{log_id}", response_model=AuditLogResponse)
def get_audit_log(
    log_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()

    if not log:
        raise ResourceNotFoundException(
            resource_name="Audit log", resource_id=str(log_id)
        )

    if (
        current_user.role.value not in ["Admin", "Auditor", "System"]
        and log.user_id != current_user.id
    ):
        raise PermissionDeniedException(detail="Not authorized to view this log")

    return log
