from pydantic import BaseModel, Field


class WebRadio(BaseModel):
    title: str
    url: str