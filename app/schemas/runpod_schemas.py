from pydantic import BaseModel


class APIRequest(BaseModel):
    prompt: str
    source: str


class RequestBodyPrompt(BaseModel):
    prompt: str