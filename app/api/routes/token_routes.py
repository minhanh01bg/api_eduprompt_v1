from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Union, Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.core.database import get_db
from app.core.security import (
    create_access_token, check_auth_admin, pwd_context, oauth2_scheme, security, get_current_user
) 
from app.crud import login_for_access_token
import app.schemas.schemas as schemas
from app import models
from datetime import datetime
from app import crud
router = APIRouter()


@router.post("/token", response_model=schemas.Token, status_code=status.HTTP_200_OK)
async def access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)
):
    output = login_for_access_token(db, form_data.username, form_data.password, pwd_context)
    if not output:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=[{"msg":"Incorrect username or password"}],
            headers={"WWW-Authenticate": "Bearer"},
        )
    return output

@router.post('/change_password')
async def change_password(data: schemas.ChangePasswordRequest, check=Depends(check_auth_admin), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username==data.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not pwd_context.verify(data.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    # change password
    hashed_new_password = pwd_context.hash(data.new_password)
    user.hashed_password = hashed_new_password
    db.commit()
    # update token
    new_token, to_encode = create_access_token(data={"sub": user.username})
    d = datetime.fromtimestamp(to_encode.get("exp"))
    token = crud.update_token(db, user.username, new_token,expired_at=d)
    return {"message": "Password updated successfully"}