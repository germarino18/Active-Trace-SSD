from pydantic import BaseModel, ConfigDict


class ImpersonateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class ImpersonateEndResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    access_token: str
    token_type: str = "bearer"
    expires_in: int
