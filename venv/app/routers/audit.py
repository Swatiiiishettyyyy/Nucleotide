from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.deps import get_db
from app.middleware.auth import get_current_user
from app.models.User import User
from app.crud.audit import get_audit_logs_by_user, get_audit_logs_by_cart

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/my-activity")
def get_my_audit_logs(
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get audit logs for current user"""
    
    logs = get_audit_logs_by_user(db, current_user.id, limit)
    
    return {
        "status": "success",
        "message": "Audit logs fetched successfully.",
        "data": {
            "user_id": current_user.id,
            "username": current_user.name or current_user.mobile,
            "total_logs": len(logs),
            "logs": [
                {
                    "id": log.id,
                    "action": log.action,
                    "entity_type": log.entity_type,
                    "entity_id": log.entity_id,
                    "cart_id": log.cart_id,
                    "details": log.details,
                    "created_at": log.created_at.isoformat() if log.created_at else None
                }
                for log in logs
            ]
        }
    }