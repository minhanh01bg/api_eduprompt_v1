from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import warnings
warnings.filterwarnings('ignore')

from app.api.main import api_router
from app.core.database import engine
from app import models
from app.core.config import settings
models.Base.metadata.create_all(bind=engine)

from app.core.init_db import create_superuser, create_superuser_for_api
create_superuser()
create_superuser_for_api()
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

origins = ["*", ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(settings.MEDIA_URL, StaticFiles(directory="app/media"), name="app/media")
app.include_router(api_router, prefix=settings.ROUTER)

from app.core.utils import init_session, close_session
@app.on_event("startup")
async def startup_event():
    await init_session()

@app.on_event("shutdown")
async def shutdown_event():
    await close_session()