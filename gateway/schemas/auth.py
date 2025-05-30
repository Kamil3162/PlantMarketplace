from pydantic import BaseModel


class LoginRequest(BaseModel):
    user_id: int
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UserSchema(BaseModel):
    user_id: int
    username: str
    email: str
    is_staff: bool = False
    is_confirmed: bool = False

