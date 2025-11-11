from sqlalchemy.orm import Session
from app.models.User import User
from app.models.device_session import DeviceSession
from datetime import datetime, timedelta
import secrets

def get_user_by_mobile(db: Session, mobile: str):
    return db.query(User).filter(User.mobile == mobile).first()

def create_user(db: Session, mobile: str, name: str = None, email: str = None):
    user = User(mobile=mobile, name=name, email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_device_session(db: Session, user_id: int, device_id: str = None, device_platform: str = None,
                          device_details: str = None, ip: str = None, user_agent: str = None, expires_in_seconds: int = None):
    session_key = secrets.token_urlsafe(32)
    expires_at = None
    if expires_in_seconds:
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in_seconds)

    ds = DeviceSession(
        user_id=user_id,
        session_key=session_key,
        device_id=device_id,
        device_platform=device_platform,
        device_details=device_details,
        ip_address=ip,
        user_agent=user_agent,
        expires_at=expires_at,
        is_active=True
    )
    db.add(ds)
    db.commit()
    db.refresh(ds)
    return ds
