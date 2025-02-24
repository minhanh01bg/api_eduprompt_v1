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
    DOMAIN = "http://192.168.1.21:7000"

    # vmhieu account
    API_URL_ITT = 'https://api.runpod.ai/v2/h2zfmy7vokxl8x/runsync'
    API_KEY_VMH = 'O461H84OAYQK5UG9K5C24AR7XHMDRDEFSXCW4B5T'

    # hieuvm account
    API_URL_ITC = 'https://api.runpod.ai/v2/iwupjthns1gw11/runsync'
    API_URL_TEXT2IMAGE_SD3 = 'https://api.runpod.ai/v2/7wt9c65qtmm1uj/runsync'
    API_URL_TEXT2IMAGE_DYNA = 'https://api.runpod.ai/v2/kmqs39hnzvowhd/runsync'
    API_KEY_HIEUVM = 'rpa_7DWIWXV9FLMKPRA01519O44QW7Q0NKR2QYU7RULC12ygum'

    # flux
    API_URL_TEXT2IMAGE2 = 'https://api.runpod.ai/v2/pyrat8v5lumbfb/runsync'
    API_KEY_TEXT2IMAGE2 = 'O461H84OAYQK5UG9K5C24AR7XHMDRDEFSXCW4B5T'

    
settings = Settings()
