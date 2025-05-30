import fastapi
import pydantic
from fastapi import Request
from routers import email_route, sample_route

app = fastapi.FastAPI(
    title="FastAPI"
)

app.include_router(email_route.router)
app.include_router(sample_route.router)