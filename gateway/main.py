import pydantic
from fastapi import Request, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from routers import (
    email_route,
    sample_route,
    universal_route,
    users_route,
    example_routers,
    auth_route
)

from middleware.validator import CredentialsMiddleware
import consul
from celery import Task
from celery.app.task import Context




c = consul.Consul(host='consul1', port=8500)  # nazwa serwisu z docker-compose
app = FastAPI(
    title="FastAPI"
)

@app.on_event("startup")
async def startup():
    c.agent.service.register(
        name="api-gateway",  # lepiej nazwa gateway
        service_id="api-gateway-unique",
        address="api-gateway",  # nazwa kontenera
        port=8010,  # port z docker-compose
        check=consul.Check.http("http://api-gateway:8010/health", interval="10s")
    )

@app.on_event("shutdown")
async def shutdown():
    try:
        c.agent.service.deregister(SERVICE_ID)
    except:
        pass

@app.get("/health")
async def health():
    return {"status": "healthy"}

app.add_middleware(
    CredentialsMiddleware
)

# app.add_middleware(
#     TrustedHostMiddleware,
#     allowed_hosts=["xyz.com", "localhost", "127.0.0.1", ]
#     # allowed_hosts=["xyz.com", "localhost", "127.0.0.1", ]
# )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://xyz.com", "https://xyz.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(email_route.router, tags=["Email"])
app.include_router(sample_route.router, tags=["Sample"])
app.include_router(universal_route.router, tags=["Universal"])
app.include_router(users_route.router, tags=["Users"])
app.include_router(example_routers.router, tags=["Example"])
app.include_router(auth_route.router, tags=["Auth"])

@app.middleware("http")
async def kong_integration_middleware(request: Request, call_next):
    kong_forwarded = request.headers.get("x-kong-forwarded")
    rate_limited_by = request.headers.get("x-rate-limited-by")

    if kong_forwarded and rate_limited_by == "kong":
        real_ip = request.headers.get("x-real-ip") or request.client.host
        rate_limit_remaining = request.headers.get("x-ratelimit-remaining")

        request.state.real_ip = real_ip
        request.state.via_kong = True
        request.state.rate_limit_remaining = int(rate_limit_remaining) if rate_limit_remaining else None

        request.state.skip_internal_rate_limiting = True

    response = await call_next(request)

    if hasattr(request.state, 'via_kong'):
        response.headers["X-Gateway-Processed"] = "true"
        response.headers["X-Available-Services"] = ",".join(ServiceName.get_service_names())

    return response

@app.get("/discover/{service_name}")
async def discover_service(service_name: str):
    # Znajdź serwis w Consul
    services = c.health.service(service_name, passing=True)[1]
    if not services:
        return {"error": "Service not found"}

    # Zwróć wszystkie healthy instancje
    instances = []
    for service in services:
        instances.append({
            "host": service['Service']['Address'],
            "port": service['Service']['Port'],
            "id": service['Service']['ID']
        })
    return {"instances": instances}


@app.get("/call/{service_name}")
async def call_service(service_name: str):
    import requests
    import random

    # Znajdź serwis
    services = c.health.service(service_name, passing=True)[1]
    if not services:
        return {"error": "Service not found"}

    # Wybierz losową instancję
    service = random.choice(services)
    host = service['Service']['Address']
    port = service['Service']['Port']

    # Zrób request (przykład)
    try:
        url = f"http://{host}:{port}/health"
        response = requests.get(url)
        return {"called": f"{host}:{port}", "response": response.json()}
    except Exception as e:
        return {"error": str(e)}