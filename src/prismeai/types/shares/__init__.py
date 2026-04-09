from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict

class Share(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    type: Optional[str] = None
    public: Optional[bool] = None
