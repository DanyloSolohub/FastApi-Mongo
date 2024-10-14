from contextlib import asynccontextmanager

from api.main import api_router
from core.config import settings
from core.db import initiate_database
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(*args, **kwargs):
    await initiate_database()
    yield


app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
)

if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get('/health')
async def health_check():
    return {'status': 'OK'}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)
