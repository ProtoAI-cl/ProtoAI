from typing import Optional

from pydantic import BaseModel


class ImageRequest(BaseModel):
    data: str
    model: Optional[str] = None
