from fastapi import Request, APIRouter


router = APIRouter(
    prefix="/api/email",
    tags=["email"],
    responses={
        404: {"description": "Email not found"},
        503: {"description": "Email service unavailable"}
    }
)

@router.get("/")
async def root(request: Request):
    host = request.headers.get("host")
    origin = request.headers.get("host")
    ip_client = request.client.host

    print(host, origin, ip_client)

    return { "message": "Hello world"}


@router.get("/test")
async def base_url(request: Request) -> dict:
    print(dict(request))
    print(request.query_params)
    return {
        'status': 'success',
        'data': 'test_data'
    }

@router.get("/items/{item_id}")
async def items_url(item_id: int):
    return { "item_id": item_id}

@router.get("/query_params")
def query_params_test(request:Request, limit:int=0, limit1:int=10):
    query_params = request.query_params
    query_params1 = request.path_params
    print(query_params1)
    print(query_params)
    print(request.headers)
    print(request.state)
    return {
        limit, limit1
    }