from __future__ import annotations

import os
from typing import Optional

from ._client import SyncAPIClient
from ._constants import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, DEFAULT_MAX_RETRIES
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

AGENT_FACTORY_SLUG = "agent-factory"
STORAGE_SLUG = "storage"


class PrismeAI:
    """Synchronous Prisme.ai SDK client.

    Usage:
        client = PrismeAI(api_key="sk-...")

        # List agents
        for agent in client.agents.list():
            print(agent["name"])

        # Stream a message
        with client.agents.messages.stream("agent-id", message={"parts": [{"text": "Hello!"}]}) as stream:
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
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        resolved_url = base_url or DEFAULT_BASE_URL
        headers = _build_auth_headers(api_key, bearer_token)

        client = SyncAPIClient(
            base_url=resolved_url,
            headers=headers,
            timeout=timeout,
            max_retries=max_retries,
        )

        # Agent Factory resources
        self.agents = Agents(client, AGENT_FACTORY_SLUG)
        self.conversations = Conversations(client, AGENT_FACTORY_SLUG)
        self.tasks = Tasks(client, AGENT_FACTORY_SLUG)
        self.tools = Tools(client, AGENT_FACTORY_SLUG)
        self.access = Access(client, AGENT_FACTORY_SLUG)
        self.analytics = Analytics(client, AGENT_FACTORY_SLUG)
        self.evaluations = Evaluations(client, AGENT_FACTORY_SLUG)
        self.ratings = Ratings(client, AGENT_FACTORY_SLUG)
        self.a2a = A2A(client, AGENT_FACTORY_SLUG)
        self.artifacts = Artifacts(client, AGENT_FACTORY_SLUG)
        self.shares = Shares(client, AGENT_FACTORY_SLUG)
        self.activity = Activity(client, AGENT_FACTORY_SLUG)
        self.profiles = Profiles(client, AGENT_FACTORY_SLUG)
        self.orgs = Orgs(client, AGENT_FACTORY_SLUG)

        # Storage resources
        self.files = Files(client, STORAGE_SLUG)
        self.vector_stores = VectorStores(client, STORAGE_SLUG)
        self.skills = Skills(client, STORAGE_SLUG)
        self.stats = Stats(client, STORAGE_SLUG)

        self._client = client

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "PrismeAI":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()



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
