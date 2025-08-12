from fastapi import Request
from fastapi.responses import JSONResponse

# reequest is optional
# base?user_id=32&b=23
from enum import Enum
class B(Enum):
    first = "dsa"

from fastapi import Query
@app.get("/base/")
def base(request:Request, user_id, b):
    print(request.auth)
    user_id = request.get('user_id')

from pydantic import BaseModel
from typing import Literal, Annotated, Union

val: Union[str, None]

# Annotated[Type T, metadata x]
class RequestBody(BaseModel):
    string:str

from pydantic import Field
from fastapi import Path, Body

class BaseRequestForm(BaseModel):
    # use when user wanna same so extra field in body in raise error
    model_config = {"extra": "forbid"}

    limit: int = Field(30, lt=100, gt=10, alias="limit")
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "modified_at"] = "created_at"
    tags: list[str] = []

@app.post("/create")
def create_url(request: RequestBody, params: Annotated[BaseRequestForm, Query()]):
    request.schema


class Item(BaseModel):
    name:str
    description:str | None = None
    price: float
    tax: float | None = None

    model_config = {
        "json_schema_extra": {
            "examples": {
                "name": "Foo",
                "description": "Foo",
                "price": "Foo",
                "tax": "Foo",
            }
        }
    }

class SubModel(BaseModel):
    item: Item
    name: str
    data_type: Union[str | None] = None
    items: list[Item] | None = None

    """
        items: [
            {data},
            {data}
        ]
    """
@app.post("/test/{pk}")
def create_base_url(pk: Annotated[int, Path(title="Random title", ge=5, le=20)], item: Item):
    """
        base request:
            item {
            name
            description
            price
            tax
        } -> body will look like that

    """
    # using parameter Body -> its a a additional field inside a body request for
    # we can add example to the field, body etc like a temapte of our data, suggestion make a one example for each field not multiple. Could
    # raise an error
    """
    openapi_examples={
        "normal": {
                    "summary": "A normal example",
                    "description": "A **normal** item works correctly.",
                    "value": {
                        "name": "Foo",
                        "description": "A very nice Item",
                        "price": 35.4,
                        "tax": 3.2,
                    },
                },
                "converted": {
                    "summary": "An example with converted data",
                    "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                    "value": {
                        "name": "Bar",
                        "price": "35.4",
                    },
                },
                "invalid": {
                    "summary": "Invalid data is rejected with an error",
                    "value": {
                        "name": "Baz",
                        "price": "thirty five point four",
                    },
                },
                in requests set(str) we represetn using list inside a request body
    """


class Cookies(BaseModel):
    model_config = {"extra": "forbid"}

    session_id: str
    fatebook_tracker: Union[str, None] = None
    googal_tracker: Union[str, None] = None


async def update_item(item_id: int, item: Annotated[Item, Body(embed=True)]):
    #  uzywajac annotated mozemy wziac dane __metadata__ przy uzyciu tego owo klucza
    # dzieki temu fastapi bedzie oczekiwac request pod kluczem item a nie po prostu jakos lista parametrów w trakcie przesyłania
    pass


from fastapi import Cookie, Header

async def request_with_cookie(request: Request, ads_id: Annotated[str | None, Cookie()]):
    print(ads_id)
    pass


async def cookie_test(cookies: Annotated[Cookies, Cookie()]):
    pass


async def request_with_headers(
        request:Request,
        user_agent: Annotated[str | None, Header()],
        csrf_token: Annotated[list[str] | None, Header()]
):
    # Header(convert_underscores=False) - w takim przypadku nie zamieniamy - na _ czasem niektore serwery
    # header bedzie konwertował - na _ dlatego taki zapis jest taki sam jak poniżej
    # wtedy csrf-token: [ 'bar', 'foo']
    print(csrf_token)
    print(request.headers.get('user-agent'))
    print(user_agent)

from enum import Enum
from fastapi import Cookie

Token = Enum("Token", ["Number", "X", "Y"])


class CommonHeaders(BaseModel):
    host: str
    save_data: bool
    if_modified_since: str | None = None
    traceparent: str | None = None
    x_tag: list[str] = []

class UserResponse(BaseModel):
    pass

# respose model include- > daje informajce ktore pola z modelu powinny zostać zwrócone
# respons emodel exclude unset - zwroci te pola ktore maja wartosci i zrobi exclude tych ktore sa none albo null
@app.post("/create" , response_model=UserResponse, response_model_include={"name", "description"})
def create_user():
    pass

@app.get("/item/{item_id}/name", response_model=CommonHeaders, response_model_exclude={"tax"})
def get_item():...

# model pydantic -> dict(), model_dump()
# unio to delcare what kind of respons eparticular function return
# i can return information using plain dict without using pydantic model


@app.get("/ketword-weight/", response_model=dict[str, float])
def keyword_weight():
    return {"foo": 32.2, "b": 32.12}

# i can specify status code for url in @get

@app.get("/base", status_code=201)
def base_url() -> dict[str, str]:
    return {"data": "key"}

# 204 No content

# 300 -399 redirections
# 400 - 499 - client error
# 500 - 599 -> server errors
# fastapi.status
from fastapi import status

# forms work
from fastapi import Form, File
# form data are normally encoded application/x-www-form-urlencoded
# form with file multipart/form-data

@app.post("/register")
def register(request: Request, user_data: Annotated[Item, Form()]):
    pass

url = "google.com"
headers = {
    "user-agent": "my-app/0.0.1"
}
with httpx.Client() as client:
    build_request = client.build_request(
        method="GET",
        headers=headers,
        content="esa",
        cookies={
            "csrf-token": "321321"
        }
    )

    print(build_request.headers)
    response = client.get(url, headers=headersw)


# mozna budaowac isntance Request
request = httpx.Request

# work with file
from fastapi import File, UploadFile
@app.post("/add-photo")
def create_upload_file(request: Request, file: Annotated[bytes, File()]):
    pass

@app.post("/add-photo1")
def create_upload_file(request: Request, file: UploadFile):
    pass

# file seek(0) - back to the start of file
# read - read file data
# wrtie - write file dala
# close()

# send multiple files

@app.post("/create-blog")
def create_blog_post(request: Request, files: Annotated[list[bytes], File()]):
    pass

# dodanie body w files zamiast form podczas przesylu nie da nam application/json tylko multipart/form-data
from fastapi import HTTPException
# send exception
@app.post("/send-num")
def create_variable(number: int):
    if number < 10:
        # to powedruje do klienta z status code 402, to wysle HTTP error do clienta
        raise ServerException(status_code=402, detail="error")
    return {"number": number}

# fast api excpetion handler


class ServerException(Exception):
    pass


@app.add_exception_handler(ServerException)
def server_exception_response(request:Request, exc: ServerException):
    return JSONResponse(
        status_code=404,
        content={
            "message": "raise exc"
        }
    )

from fastapi import status
@app.get("/test-url",
    status_code=status.HTTP_201_CREATED,
    tags=["test"],
    summary="esa",
    description="pooo",
    deprecated=True
)
def test_url():
    pass


# json encoder
# put for update
# patch for partially update a data
from fastapi.encoders import jsonable_encoder
from fastapi import Depends
# dependency injection

async def common_patterns(q: str | None = None, p: str | None = None, limit: int = 100):
    print(q, p, limit)
    return {"q": q, "p": p, "limit": limit}

# q is a param path like &p=32&q=32&limit=456
async def dep_in(param = Cookie()):
    pass

# classes as dependency injections, działa tak samo jak funkcja tylko do konstuktora musze dac te params które chce
class Cat:
    def __init__(self, p: str, q: str, limit: int = 100):
        self.p = p
        self.q = q
        self.limit = limit

@app.get("/items")
async def read_items(request: Request, commons: Annotated[dict, Depends(Cat)]):
    return commons

# to jest to samo co wyzej
@app.get("/itemsv1")
async def read_items(request: Request, commons: Annotated[Cat, Depends()]):
    return commons


def query_extractor(q: str | None = None):
    return q


def query_or_cookie_extractor(
    q: Annotated[str | None, Depends(query_extractor)],
    token: Annotated[str | None, Depends(Cookie)]
):
    if not q:
        return token
    return q

@app.get("/items/")
async def read_query(
    query_or_default: Annotated[str, Depends(query_or_cookie_extractor, use_cache=False)],
):
    return {"q_or_cookie": query_or_default}

# po wywolaniu dependency mozemy to sapisac w cache
class Power:
    def __init__(self, function):
        self.function = function

    def __call__(self, *args, **kwargs):
        result = self.function(*args)
        return result ** 2

@Power
def multiply_together(a, b):
    return a * b

print(multiply_together)

# scope w fastapi to jest metadane o przychodzącym requescie HTTP czyli headers , method query_string servber client scheme