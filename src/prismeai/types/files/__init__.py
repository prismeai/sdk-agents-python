from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict

class FileObject(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    name: str
    url: Optional[str] = None
    mime_type: Optional[str] = None
    size: Optional[int] = None
