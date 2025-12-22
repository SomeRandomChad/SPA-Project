"""rephrase_schemas"""

"""
Implements RephraseRequest / RephraseResponse
as defined in SPA-Project/api/openapi.yml
"""

from pydantic import BaseModel, Field


class RephraseRequest(BaseModel):
    text: str = Field(
        ...,
        description="The input text to be rephrased",
        min_length=1,
        max_length=5000,
        json_schema_extra={
            "example":"Hey guys, let's huddle about AI."
        }
    )


class RephraseResponse(BaseModel):
    professional: str = Field(
        ...,
        description="Professionally rephrased version of the input text"
    )
    casual: str = Field(
        ...,
        description="Casual rephrasing of the input text"
    )
    polite: str = Field(
        ...,
        description="Polite rephrasing of the input text"
    )
    social: str = Field(
        ...,
        description="Social-media-style rephrasing of the input text"
    )


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: list | None = None
