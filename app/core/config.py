import logging


class Settings:
    check = True
    ROUTER = '/api/v1' if check == True else ''
    #  DB
    SQLALCHEMY_DATABASE_URL = "sqlite:///./app/db.sqlite3"
    # SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost/fancy"
    #
    superuser = {
        "id": 1,
        "username": "admin",
        "password": "admin",
        "is_active": True,
        "is_admin": True,
    }

    # Sercurity
    SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 360
    MEDIA_URL = "/app/media"
    # MEDIA_HTTP = "http://localhost:3001/app/media"
    MEDIA_HTTP = "https://gramotion.physcode.com/app/media"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("app.log"),  # Ghi log vào file
            logging.StreamHandler()  # Hiển thị log trong console
        ]
    )
    logger = logging.getLogger(__name__)

    PROMPT_CONFIG_IMAGE_TEXT_2IMAGE = 'What color is in the background of the photo above? and what its content is? Please describe in detail the content of the photo, What is the main character in the photo?'
    PROMPT_WEIGHT = 0.8
    CAPTION_WEIGHT = 0.1
    PROMPT_CAPTION_WEIGHT = 0.1
    DOMAIN = 'https://epadmin.physcode.com'
settings = Settings()
