from __future__ import annotations

import os
from typing import Optional

from ._client import AsyncAPIClient
from ._constants import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, DEFAULT_MAX_RETRIES
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

AGENT_FACTORY_SLUG = "agent-factory"
STORAGE_SLUG = "storage"


class AsyncPrismeAI:
    """Asynchronous Prisme.ai SDK client.

    Usage:
        async with AsyncPrismeAI(api_key="sk-...") as client:
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
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        resolved_url = base_url or DEFAULT_BASE_URL
        headers = _build_auth_headers(api_key, bearer_token)

        client = AsyncAPIClient(
            base_url=resolved_url,
            headers=headers,
            timeout=timeout,
            max_retries=max_retries,
        )

        # Agent Factory resources
        self.agents = AsyncAgents(client, AGENT_FACTORY_SLUG)
        self.conversations = AsyncConversations(client, AGENT_FACTORY_SLUG)
        self.tasks = AsyncTasks(client, AGENT_FACTORY_SLUG)
        self.tools = AsyncTools(client, AGENT_FACTORY_SLUG)
        self.access = AsyncAccess(client, AGENT_FACTORY_SLUG)
        self.analytics = AsyncAnalytics(client, AGENT_FACTORY_SLUG)
        self.evaluations = AsyncEvaluations(client, AGENT_FACTORY_SLUG)
        self.ratings = AsyncRatings(client, AGENT_FACTORY_SLUG)
        self.a2a = AsyncA2A(client, AGENT_FACTORY_SLUG)
        self.artifacts = AsyncArtifacts(client, AGENT_FACTORY_SLUG)
        self.shares = AsyncShares(client, AGENT_FACTORY_SLUG)
        self.activity = AsyncActivity(client, AGENT_FACTORY_SLUG)
        self.profiles = AsyncProfiles(client, AGENT_FACTORY_SLUG)
        self.orgs = AsyncOrgs(client, AGENT_FACTORY_SLUG)

        # Storage resources
        self.files = AsyncFiles(client, STORAGE_SLUG)
        self.vector_stores = AsyncVectorStores(client, STORAGE_SLUG)
        self.skills = AsyncSkills(client, STORAGE_SLUG)
        self.stats = AsyncStats(client, STORAGE_SLUG)

        self._client = client

    async def close(self) -> None:
        await self._client.close()

    async def __aenter__(self) -> "AsyncPrismeAI":
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()


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
