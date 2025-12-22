"""rephrase_service"""

from app.schemas.rephrase import RephraseRequest, RephraseResponse


class ValidationError(Exception):
    """Service-level validation error."""
    pass


def validate_input(input: RephraseRequest) -> str:
    trimmed = input.text.strip()
    if len(trimmed) == 0:
        raise ValidationError('"text" must not be empty')

    max_len = 5000
    if len(trimmed) > max_len:
        raise ValidationError(f'"text" must be <= {max_len} characters')

    return trimmed


async def rephrase_service(input: RephraseRequest) -> RephraseResponse:
    text = validate_input(input)
    return RephraseResponse(
        professional=text,
        casual=text,
        polite=text,
        social=text,
    )