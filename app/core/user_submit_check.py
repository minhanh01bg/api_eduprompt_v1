from app.module.s3_config import S3_Config
from fastapi import HTTPException
import os

def check_userid_exists(user_id:str):
    path_user = f"app/media/{S3_Config.image_bucket_name}/{user_id}"
    if not os.path.isdir(path_user):
        raise HTTPException(detail={'error':'User id not found'}, status_code=404)


def check_filename_exists(user_id:str, file_name:str):
    path_user = f"app/media/{S3_Config.image_bucket_name}/{user_id}/{file_name}"
    if not os.path.isdir(path_user):
        raise HTTPException(detail={'error':'File name not found'}, status_code=404)