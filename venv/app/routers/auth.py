from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.schemas.auth import (
    SendOTPRequest,
    SendOTPResponse,
    OTPData,
    VerifyOTPRequest,
    VerifyOTPResponse,
    VerifiedData
)
from app.deps import get_db
from app.utils import otp_manager, security
from app.crud.auth import get_user_by_mobile, create_user, create_device_session

from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Read OTP and token expiry directly from .env
OTP_EXPIRY_SECONDS = int(os.getenv("OTP_EXPIRY_SECONDS", 300))
ACCESS_TOKEN_EXPIRE_SECONDS = int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", 86400))

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/send-otp", response_model=SendOTPResponse)
def send_otp(request: SendOTPRequest, db: Session = Depends(get_db)):
    # Rate limit
    if not otp_manager.can_request_otp(request.country_code, request.mobile):
        remaining = otp_manager.get_remaining_requests(request.country_code, request.mobile)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"OTP request limit reached. Remaining: {remaining}"
        )

    # Generate OTP
    otp = otp_manager.generate_otp()
    otp_manager.store_otp(request.country_code, request.mobile, otp, expires_in=OTP_EXPIRY_SECONDS)

    # TODO: integrate Twilio or other SMS service here
    message = f"OTP sent successfully to {request.mobile}."

    data = OTPData(
        mobile=request.mobile,
        otp=otp,  # In production, avoid returning OTP in response
        expires_in=OTP_EXPIRY_SECONDS,
        purpose=request.purpose
    )
    return SendOTPResponse(status="success", message=message, data=data)


@router.post("/verify-otp", response_model=VerifyOTPResponse)
def verify_otp(req: VerifyOTPRequest, request: Request, db: Session = Depends(get_db)):
    # Check OTP
    stored = otp_manager.get_otp(req.country_code, req.mobile)
    if not stored:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP expired or not found")
    if stored != req.otp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")

    # OTP correct, delete it
    otp_manager.delete_otp(req.country_code, req.mobile)

    # Get or create user
    user = get_user_by_mobile(db, req.mobile)
    if not user:
        user = create_user(db, mobile=req.mobile)

    # Create device session
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    ds = create_device_session(
        db=db,
        user_id=user.id,
        device_id=req.device_id,
        device_platform=req.device_platform or "unknown",
        device_details=req.device_details,
        ip=ip,
        user_agent=user_agent,
        expires_in_seconds=ACCESS_TOKEN_EXPIRE_SECONDS
    )

    # Create access token with session id and user id
    payload = {
        "sub": str(user.id),
        "session_id": str(ds.id),
        "device_platform": ds.device_platform
    }
    token = security.create_access_token(payload, expires_delta=ACCESS_TOKEN_EXPIRE_SECONDS)

    resp_data = VerifiedData(
        user_id=user.id,
        name=user.name,
        mobile=user.mobile,
        email=user.email,
        access_token=token,
        token_type="Bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_SECONDS
    )

    return VerifyOTPResponse(status="success", message="OTP verified successfully.", data=resp_data)
