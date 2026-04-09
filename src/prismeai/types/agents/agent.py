from __future__ import annotations
from typing import Optional, List, Union
from pydantic import BaseModel, ConfigDict
from .sub_agent import SubAgentConfig
from .guardrail import GuardrailConfig
from .tool_permission import ToolPermissions

class Agent(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    slug: str
    name: Union[str, dict[str, str]]
    description: Optional[Union[str, dict[str, str]]] = None
    photo: Optional[str] = None
    status: Optional[str] = None
    labels: Optional[List[str]] = None
    model: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    sub_agents: Optional[List[SubAgentConfig]] = None
    guardrails: Optional[List[GuardrailConfig]] = None
    tool_permissions: Optional[ToolPermissions] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class AgentCreate(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: Union[str, dict[str, str]]
    description: Optional[Union[str, dict[str, str]]] = None
    model: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None
    sub_agents: Optional[List[SubAgentConfig]] = None
    guardrails: Optional[List[GuardrailConfig]] = None
    tool_permissions: Optional[ToolPermissions] = None

class AgentUpdate(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: Optional[Union[str, dict[str, str]]] = None
    description: Optional[Union[str, dict[str, str]]] = None
    model: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None
    sub_agents: Optional[List[SubAgentConfig]] = None
    guardrails: Optional[List[GuardrailConfig]] = None
    tool_permissions: Optional[ToolPermissions] = None
