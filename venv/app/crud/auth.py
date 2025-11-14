from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
from typing import Optional
from app.models.User import User
from app.models.device_session import DeviceSession


def get_user_by_mobile(db: Session, mobile: str) -> Optional[User]:
    """
    Retrieve user by mobile number.
    """
    return db.query(User).filter(User.mobile == mobile).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Retrieve user by ID.
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Retrieve user by email.
    """
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, mobile: str, name: Optional[str] = None, email: Optional[str] = None) -> User:
    """
    Create a new user with mobile number.
    """
    user = User(mobile=mobile, name=name, email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_profile(
    db: Session,
    user_id: int,
    name: Optional[str] = None,
    email: Optional[str] = None,
    mobile: Optional[str] = None
) -> Optional[User]:
    """
    Update user profile information.
    Only updates fields that are provided (not None).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    # Update only provided fields
    if name is not None:
        user.name = name
    if email is not None:
        user.email = email
    if mobile is not None:
        user.mobile = mobile

    try:
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        raise e


def create_device_session(
    db: Session,
    user_id: int,
    device_id: Optional[str] = None,
    device_platform: Optional[str] = None,
    device_details: Optional[str] = None,
    ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    expires_in_seconds: Optional[int] = None
) -> DeviceSession:
    """
    Create a new device session for a user.
    """
    session_key = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in_seconds) if expires_in_seconds else None

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


def get_device_session(db: Session, session_id: int) -> Optional[DeviceSession]:
    """
    Retrieve device session by ID.
    """
    return db.query(DeviceSession).filter(DeviceSession.id == session_id).first()


def deactivate_session(db: Session, session_id: int) -> bool:
    """
    Deactivate a device session.
    """
    session = db.query(DeviceSession).filter(DeviceSession.id == session_id).first()
    if session:
        session.is_active = False
        db.commit()
        return True
    return False