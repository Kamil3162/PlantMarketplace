import enum
from pprint import pp
import pydantic
import typing
from fastapi import APIRouter, Request,Query
from fastapi.responses import JSONResponse


router = APIRouter(
    prefix='/example/route',
    tags=['example']
)

class PredefinedParameter(enum.Enum):
    alexnet = "alexnet"
    resnt = "resnet"
    lenet = "lenet"

class BaseRequest(pydantic.BaseModel):
    name:str
    description: str | None = None
    price: float
    tax: float | None = None

@router.get('/')
async def example_url(request: Request) -> JSONResponse:

    print(request)

    return JSONResponse(
        content={
            'status': 'proceed',
            'data':'random_data'
        }
    )


@router.get('/{user_id}')
async def detail_url(request: Request, user_id:int) -> JSONResponse:

    print(user_id)
    print(request)
    pp(dict(request))

    return JSONResponse(
        content={
            'status': 'proceed',
            'data':'random_data'
        }
    )

@router.get("/architecture/{architecture}")
async def predefined_value(request: Request, architecture: PredefinedParameter, q: str):
    print(q)

    response_data = {
        'status': 'architecture',
        'info': str(architecture)
    }

    if architecture is PredefinedParameter.lenet:
        response = JSONResponse(content=response_data)
        response.status_code = 203
        return response

@router.api_route("/t/test-route", methods=["GET", "POST"])
async def randomtest_router(
        request: Request,
        body: BaseRequest = None,
        q: typing.Union[str | None] = Query(default=None, max_length=5)
):
    pp(request)
    print(q)
    print(body)
    return JSONResponse(
        content={
            'response': 'response',
            'data': 'data'
        }
    )

@router.get('/coumple/test/param/')
async def couple_test_param(q: typing.Annotated[list[str], Query()] = ["foo", "bar"]):
    print(q)
    return q
