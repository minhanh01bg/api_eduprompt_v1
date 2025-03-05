from sqlalchemy.orm import Session
from app import models
from app.core.database import SessionLocal
from app.core.security import create_access_token, pwd_context
from app import crud
from datetime import datetime
from app.core.config import settings
def create_superuser():
    password = settings.superuser['password']
    settings.superuser['password'] = pwd_context.hash(password)

    database_addsuperuser = SessionLocal()
    user = database_addsuperuser.query(models.User).filter(models.User.username == settings.superuser['username']).first()
    if user is None:
        addsuperuser = models.User(id=settings.superuser['id'], username=settings.superuser['username'],
                                hashed_password=settings.superuser['password'], is_active=settings.superuser['is_active'], is_admin=settings.superuser['is_admin'])
        
        database_addsuperuser.add(addsuperuser)
        database_addsuperuser.commit()
        database_addsuperuser.refresh(addsuperuser)
        # create token
        access_token, to_encode = create_access_token(
            data={"sub": settings.superuser['username']}
        )
        d = datetime.fromtimestamp(to_encode.get("exp"))
        db_token = models.Token(id=settings.superuser['id'], access_token=access_token, username=addsuperuser.username, expired_at=d)
        database_addsuperuser.add(db_token)
        database_addsuperuser.commit()
        database_addsuperuser.refresh(db_token)
        database_addsuperuser.close()
    else:
        database_addsuperuser.close()
        print('admin is oke')

# create_superuser()

def create_superuser_for_api():
    password = settings.superuser_api['password']
    settings.superuser_api['password'] = pwd_context.hash(password)

    database_addsuperuser_api = SessionLocal()
    user = database_addsuperuser_api.query(models.User).filter(models.User.username == settings.superuser_api['username']).first()
    if user is None:
        add_superuser = models.User(id=settings.superuser_api['id'], username=settings.superuser_api['username'],
                                hashed_password=settings.superuser_api['password'], is_active=settings.superuser_api['is_active'], is_admin=settings.superuser_api['is_admin'])
        
        database_addsuperuser_api.add(add_superuser)
        database_addsuperuser_api.commit()
        database_addsuperuser_api.refresh(add_superuser)

        # create token
        access_token, to_encode = create_access_token(
            data={"sub": settings.superuser_api['username']}
        )
        
        access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbl9hcGkiLCJleHAiOjE3NDExNjg5Mjh9.ZgSG19nATGUgJfOhHw289BjwEgR5p63tIoqTDNwbkco"
        d = datetime.fromtimestamp(to_encode.get("exp"))
        db_token = models.Token(id=settings.superuser_api['id'], access_token=access_token, username=add_superuser.username, expired_at=d)
        database_addsuperuser_api.add(db_token)
        database_addsuperuser_api.commit()
        database_addsuperuser_api.refresh(db_token)
        database_addsuperuser_api.close()
    else:
        database_addsuperuser_api.close()
        print('admin is oke')

