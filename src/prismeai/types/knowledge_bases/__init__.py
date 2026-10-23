from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict

class KnowledgeBase(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    name: str
    description: Optional[str] = None
    status: Optional[str] = None

class KnowledgeBaseCreate(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: str
    description: Optional[str] = None

class KnowledgeBaseUpdate(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: Optional[str] = None
    description: Optional[str] = None

class SearchHit(BaseModel):
    model_config = ConfigDict(extra="allow")
    document_id: str
    score: float
    content: list[Any]
    source_url: Optional[str] = None
    filename: Optional[str] = None

class Document(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    knowledge_base_id: str
    source_type: str
    status: str
    filename: Optional[str] = None
    native_file_id: Optional[str] = None
    tags: Optional[dict[str, Any]] = None

class AccessBinding(BaseModel):
    model_config = ConfigDict(extra="allow")
    knowledge_base_id: str
    principal_type: str
    principal_id: str
    role: str

class WebSource(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    knowledge_base_id: str
    url: str
    crawler_options: Optional[dict[str, Any]] = None
