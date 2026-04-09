from prismeai import PrismeAI, AsyncPrismeAI


def test_sync_client_creation():
    client = PrismeAI(api_key="test-key")
    assert client.agents is not None
    assert client.tasks is not None
    assert client.conversations is not None
    assert client.tools is not None
    assert client.access is not None
    assert client.analytics is not None
    assert client.evaluations is not None
    assert client.ratings is not None
    assert client.a2a is not None
    assert client.artifacts is not None
    assert client.shares is not None
    assert client.activity is not None
    assert client.profiles is not None
    assert client.orgs is not None
    assert client.files is not None
    assert client.vector_stores is not None
    assert client.skills is not None
    assert client.stats is not None


def test_sync_client_with_storage():
    client = PrismeAI(api_key="test-key")
    assert client.files is not None
    assert client.vector_stores is not None


def test_sync_client_bearer_token():
    client = PrismeAI(bearer_token="my-jwt")
    assert client.agents is not None


def test_sync_client_custom_base_url():
    client = PrismeAI(
        api_key="test-key",
        base_url="https://api.my-instance.com/v2",
    )
    assert client.agents is not None


def test_async_client_creation():
    client = AsyncPrismeAI(api_key="test-key")
    assert client.agents is not None
    assert client.tasks is not None
    assert client.files is not None
    assert client.vector_stores is not None


def test_sync_client_context_manager():
    with PrismeAI(api_key="test-key") as client:
        assert client.agents is not None


def test_agents_sub_resources():
    client = PrismeAI(api_key="test-key")
    assert client.agents.messages is not None
