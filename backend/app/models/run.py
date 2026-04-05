from pydantic import BaseModel


class RunRequest(BaseModel):
    slug: str
    input: str


class RunResponse(BaseModel):
    output: dict