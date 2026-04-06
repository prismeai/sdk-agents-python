from __future__ import annotations

import os
from typing import Optional

from ._client import AsyncAPIClient
from ._constants import ENVIRONMENTS, DEFAULT_BASE_URL, DEFAULT_TIMEOUT, DEFAULT_MAX_RETRIES
from .resources.agents import AsyncAgents
from .resources.conversations import AsyncConversations
from .resources.tasks import AsyncTasks
from .resources.tools import AsyncTools
from .resources.access import AsyncAccess
from .resources.analytics import AsyncAnalytics
from .resources.evaluations import AsyncEvaluations
from .resources.ratings import AsyncRatings
from .resources.a2a import AsyncA2A
from .resources.artifacts import AsyncArtifacts
from .resources.shares import AsyncShares
from .resources.activity import AsyncActivity
from .resources.profiles import AsyncProfiles
from .resources.orgs import AsyncOrgs
from .resources.files import AsyncFiles
from .resources.vector_stores import AsyncVectorStores
from .resources.skills import AsyncSkills
from .resources.stats import AsyncStats


class AsyncPrismeAI:
    """Asynchronous Prisme.ai SDK client.

    Usage:
        async with AsyncPrismeAI(
            api_key="sk-...",
            environment="sandbox",
            agent_factory_workspace_id="6t5T1iC",
        ) as client:
            async for agent in client.agents.list():
                print(agent["name"])
    """

    agents: AsyncAgents
    conversations: AsyncConversations
    tasks: AsyncTasks
    tools: AsyncTools
    access: AsyncAccess
    analytics: AsyncAnalytics
    evaluations: AsyncEvaluations
    ratings: AsyncRatings
    a2a: AsyncA2A
    artifacts: AsyncArtifacts
    shares: AsyncShares
    activity: AsyncActivity
    profiles: AsyncProfiles
    orgs: AsyncOrgs
    files: AsyncFiles
    vector_stores: AsyncVectorStores
    skills: AsyncSkills
    stats: AsyncStats

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

        af_client = AsyncAPIClient(
            base_url=resolved_url,
            headers=headers,
            timeout=timeout,
            max_retries=max_retries,
        )

        # Agent Factory resources
        self.agents = AsyncAgents(af_client, agent_factory_workspace_id)
        self.conversations = AsyncConversations(af_client, agent_factory_workspace_id)
        self.tasks = AsyncTasks(af_client, agent_factory_workspace_id)
        self.tools = AsyncTools(af_client, agent_factory_workspace_id)
        self.access = AsyncAccess(af_client, agent_factory_workspace_id)
        self.analytics = AsyncAnalytics(af_client, agent_factory_workspace_id)
        self.evaluations = AsyncEvaluations(af_client, agent_factory_workspace_id)
        self.ratings = AsyncRatings(af_client, agent_factory_workspace_id)
        self.a2a = AsyncA2A(af_client, agent_factory_workspace_id)
        self.artifacts = AsyncArtifacts(af_client, agent_factory_workspace_id)
        self.shares = AsyncShares(af_client, agent_factory_workspace_id)
        self.activity = AsyncActivity(af_client, agent_factory_workspace_id)
        self.profiles = AsyncProfiles(af_client, agent_factory_workspace_id)
        self.orgs = AsyncOrgs(af_client, agent_factory_workspace_id)

        # Storage resources
        storage_ws = storage_workspace_id or agent_factory_workspace_id
        storage_client = AsyncAPIClient(
            base_url=resolved_url,
            headers=headers,
            timeout=timeout,
            max_retries=max_retries,
        ) if storage_workspace_id else af_client

        self.files = AsyncFiles(storage_client, storage_ws)
        self.vector_stores = AsyncVectorStores(storage_client, storage_ws)
        self.skills = AsyncSkills(storage_client, storage_ws)
        self.stats = AsyncStats(storage_client, storage_ws)

        self._af_client = af_client
        self._storage_client = storage_client if storage_workspace_id else None

    async def close(self) -> None:
        await self._af_client.close()
        if self._storage_client:
            await self._storage_client.close()

    async def __aenter__(self) -> "AsyncPrismeAI":
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()


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
