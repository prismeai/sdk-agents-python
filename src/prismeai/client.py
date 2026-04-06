from __future__ import annotations

import os
from typing import Optional

from ._client import SyncAPIClient
from ._constants import ENVIRONMENTS, DEFAULT_BASE_URL, DEFAULT_TIMEOUT, DEFAULT_MAX_RETRIES
from .resources.agents import Agents
from .resources.conversations import Conversations
from .resources.tasks import Tasks
from .resources.tools import Tools
from .resources.access import Access
from .resources.analytics import Analytics
from .resources.evaluations import Evaluations
from .resources.ratings import Ratings
from .resources.a2a import A2A
from .resources.artifacts import Artifacts
from .resources.shares import Shares
from .resources.activity import Activity
from .resources.profiles import Profiles
from .resources.orgs import Orgs
from .resources.files import Files
from .resources.vector_stores import VectorStores
from .resources.skills import Skills
from .resources.stats import Stats


class PrismeAI:
    """Synchronous Prisme.ai SDK client.

    Usage:
        client = PrismeAI(
            api_key="sk-...",
            environment="sandbox",
            agent_factory_workspace_id="6t5T1iC",
            storage_workspace_id="hl2Xm8u",
        )

        # List agents
        for agent in client.agents.list():
            print(agent["name"])

        # Stream a message
        with client.agents.messages.stream("agent-id", text="Hello!") as stream:
            for event in stream:
                print(event)
    """

    agents: Agents
    conversations: Conversations
    tasks: Tasks
    tools: Tools
    access: Access
    analytics: Analytics
    evaluations: Evaluations
    ratings: Ratings
    a2a: A2A
    artifacts: Artifacts
    shares: Shares
    activity: Activity
    profiles: Profiles
    orgs: Orgs
    files: Files
    vector_stores: VectorStores
    skills: Skills
    stats: Stats

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        bearer_token: Optional[str] = None,
        environment: Optional[str] = None,
        base_url: Optional[str] = None,
        agent_factory_workspace_id: str,
        storage_workspace_id: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        resolved_url = _resolve_base_url(base_url, environment)
        headers = _build_auth_headers(api_key, bearer_token)

        af_client = SyncAPIClient(
            base_url=resolved_url,
            headers=headers,
            timeout=timeout,
            max_retries=max_retries,
        )

        # Agent Factory resources
        self.agents = Agents(af_client, agent_factory_workspace_id)
        self.conversations = Conversations(af_client, agent_factory_workspace_id)
        self.tasks = Tasks(af_client, agent_factory_workspace_id)
        self.tools = Tools(af_client, agent_factory_workspace_id)
        self.access = Access(af_client, agent_factory_workspace_id)
        self.analytics = Analytics(af_client, agent_factory_workspace_id)
        self.evaluations = Evaluations(af_client, agent_factory_workspace_id)
        self.ratings = Ratings(af_client, agent_factory_workspace_id)
        self.a2a = A2A(af_client, agent_factory_workspace_id)
        self.artifacts = Artifacts(af_client, agent_factory_workspace_id)
        self.shares = Shares(af_client, agent_factory_workspace_id)
        self.activity = Activity(af_client, agent_factory_workspace_id)
        self.profiles = Profiles(af_client, agent_factory_workspace_id)
        self.orgs = Orgs(af_client, agent_factory_workspace_id)

        # Storage resources
        storage_ws = storage_workspace_id or agent_factory_workspace_id
        storage_client = SyncAPIClient(
            base_url=resolved_url,
            headers=headers,
            timeout=timeout,
            max_retries=max_retries,
        ) if storage_workspace_id else af_client

        self.files = Files(storage_client, storage_ws)
        self.vector_stores = VectorStores(storage_client, storage_ws)
        self.skills = Skills(storage_client, storage_ws)
        self.stats = Stats(storage_client, storage_ws)

        self._af_client = af_client
        self._storage_client = storage_client if storage_workspace_id else None

    def close(self) -> None:
        self._af_client.close()
        if self._storage_client:
            self._storage_client.close()

    def __enter__(self) -> "PrismeAI":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


def _resolve_base_url(base_url: Optional[str], environment: Optional[str]) -> str:
    if base_url:
        return base_url
    if environment:
        env_url = ENVIRONMENTS.get(environment)
        if env_url:
            return env_url
        if environment.startswith("http"):
            return environment
        raise ValueError(
            f'Unknown environment: "{environment}". Use "sandbox", "production", or provide a base_url.'
        )
    return DEFAULT_BASE_URL


def _build_auth_headers(
    api_key: Optional[str], bearer_token: Optional[str]
) -> dict[str, str]:
    headers: dict[str, str] = {}

    if api_key:
        headers["x-prismeai-api-key"] = api_key
    if bearer_token:
        headers["authorization"] = f"Bearer {bearer_token}"

    if not api_key and not bearer_token:
        env_key = os.environ.get("PRISMEAI_API_KEY")
        env_token = os.environ.get("PRISMEAI_BEARER_TOKEN")
        if env_key:
            headers["x-prismeai-api-key"] = env_key
        elif env_token:
            headers["authorization"] = f"Bearer {env_token}"

    return headers
