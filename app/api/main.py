from fastapi import APIRouter
from app.api.routes import score_routes, token_routes, runpod_routes
api_router = APIRouter()
api_router.include_router(token_routes.router, prefix='',tags=['Token'])
api_router.include_router(score_routes.router,prefix='', tags=['Score'])
api_router.include_router(runpod_routes.router, prefix='', tags=['Runpod test'])