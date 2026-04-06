from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict

class PaginationParams(BaseModel):
    model_config = ConfigDict(extra="allow")
    page: Optional[int] = None
    limit: Optional[int] = None
