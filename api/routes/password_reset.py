from fastapi import APIRouter, Depends, HTTPException, status
from bson.objectid import ObjectId
from ..schemas import PasswordResetRequest, db, NewPassword
from ..oath2 import create_access_token, verify_access_token
from ..send_email import send_password_reset_email
from ..utils import get_password_hash

router = APIRouter(
    prefix="/password",
    tags=["Password Reset"]
)


@router.post("/reset", response_description="Reset password request", status_code=200)
async def reset_password_request(request: PasswordResetRequest):
    email = request.email
    user = await db["users"].find_one({"email": email})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist"
        )

    token = create_access_token(data={"id": str(user["_id"])})
    await send_password_reset_email(
        "Password Reset",
        recipient=email,
        body={
            "title": "Password Reset Request",
            "name": user["name"],
            "reset_link": f"http://localhost:8000/?token={token}"
        })

@router.put("/reset", response_description="Reset password")
async def reset_password(new_password: NewPassword, token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token is invalid or expired",
    )
    
    token_data = verify_access_token(token, credentials_exception)
    
    user_id = token_data.id
    
    hashed_password = get_password_hash(new_password.new_password)
    updated_result = await db["users"].update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"password": hashed_password}}
    )

    if updated_result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not update password for user with id: {user_id}"
        )
    
    return {"message": "Password has been reset successfully"}