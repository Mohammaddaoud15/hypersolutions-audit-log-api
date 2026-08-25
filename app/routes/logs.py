from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models import AuditLog, User
from app.schemas import AuditLogCreate, AuditLogResponse

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


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
