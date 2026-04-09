from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict

class VectorStore(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    name: str
    description: Optional[str] = None
    status: Optional[str] = None

class VectorStoreCreate(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: str
    description: Optional[str] = None

class VectorStoreUpdate(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: Optional[str] = None
    description: Optional[str] = None

class VectorStoreSearchResult(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    content: str
    score: float
    metadata: Optional[dict[str, Any]] = None

class VSFile(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    name: str
    vector_store_id: str
    status: Optional[str] = None

class VSAccessEntry(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    role: str
    email: Optional[str] = None
