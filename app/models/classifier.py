from typing import Annotated, Optional
from pydantic import BaseModel, Field

class VaugenessResponse(BaseModel):
    is_vague: Annotated[bool, Field(description="Indicates if the given query is vague or not")]
    response: Annotated[Optional[str], Field(description="The response back to user to clarify the vagueness. None if is_vague is False")]