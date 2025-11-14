from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.deps import get_db
from app.schemas.member import MemberRequest, MemberResponse, MemberListResponse, MemberData
from app.crud.member import save_member, get_members_by_user
from app.utils.auth_user import get_current_user

router = APIRouter(prefix="/member", tags=["Member"])

# Save or update member
@router.post("/save", response_model=MemberResponse)
def save_member_api(
    req: MemberRequest,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    member = save_member(db, user, req)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found for editing")

    return {
        "status": "success",
        "message": "Member save successfully."
    }

# Get list of members for user
@router.get("/list", response_model=MemberListResponse)
def get_member_list(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    members = get_members_by_user(db, user)
    data = []
    for m in members:
        data.append({
            "member_id": m.id,
            "name": m.name,
            "relation": m.relation
        })
    return {
        "status": "success",
        "message": "Member list fetched successfully.",
        "data": data
    }
