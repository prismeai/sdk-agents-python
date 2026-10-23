# prismeai-sdk-agents

Official Python SDK for the [Prisme.ai](https://prisme.ai) Agent Factory and Storage APIs.

## Installation

```bash
pip install prismeai-sdk-agents
```

## Quick Start

```python
from prismeai import PrismeAI

client = PrismeAI(api_key="sk-...")
```

## Authentication

```python
# API Key (recommended for server-side)
client = PrismeAI(api_key="sk-...")

# Bearer Token (for user-scoped access)
client = PrismeAI(bearer_token="eyJ...")

# Self-hosted instance
client = PrismeAI(
    api_key="sk-...",
    base_url="https://api.your-instance.com/v2",
)
```

Environment variables `PRISMEAI_API_KEY` and `PRISMEAI_BEARER_TOKEN` are also supported.

## Sync and Async

```python
# Sync
from prismeai import PrismeAI

with PrismeAI(api_key="sk-...") as client:
    agent = client.agents.get("agent-id")

# Async
from prismeai import AsyncPrismeAI

async with AsyncPrismeAI(api_key="sk-...") as client:
    agent = await client.agents.get("agent-id")
```

## Usage Examples

### Agents

```python
# List agents (auto-pagination)
for agent in client.agents.list():
    print(agent["name"])

# Create an agent
agent = client.agents.create(
    name="My Agent",
    description="A helpful assistant",
    model="gpt-4o",
    instructions="You are a helpful assistant.",
)

# Get, update, delete
agent = client.agents.get(agent["id"])
updated = client.agents.update(agent["id"], name="Renamed Agent")
client.agents.delete(agent["id"])

# Publish / discard draft
client.agents.publish(agent["id"])
client.agents.discard_draft(agent["id"])
```

### Messages

```python
# Send a message (non-streaming)
response = client.agents.messages.send(
    "agent-id",
    message={"parts": [{"text": "Hello!"}]},
)
print(response["output"])

# Stream a message (SSE)
with client.agents.messages.stream(
    "agent-id",
    message={"parts": [{"text": "Tell me a story"}]},
) as stream:
    for event in stream:
        if event.get("event") == "task.output.delta":
            for part in event["data"]["delta"]["parts"]:
                print(part.get("text", ""), end="")
```

### Tools

```python
# Create a tool for an agent
tool = client.tools.create(
    "agent-id",
    type="function",
    name="get_weather",
    description="Get weather for a location",
    schema={"type": "object", "properties": {"location": {"type": "string"}}},
)

# List tools
for t in client.tools.list("agent-id"):
    print(t["name"])

# Delete a tool
client.tools.delete("agent-id", tool["id"])
```

### Conversations

```python
# List conversations for an agent
for conv in client.conversations.list("agent-id"):
    print(conv["id"], conv.get("title"))

# Create a conversation
conv = client.conversations.create("agent-id")

# Send message in a conversation context
response = client.agents.messages.send(
    "agent-id",
    message={"parts": [{"text": "Hello!"}], "contextId": conv["id"]},
)
```

### A2A (Agent-to-Agent)

```python
# Send message via A2A protocol (JSON-RPC 2.0)
result = client.a2a.send("target-agent-id", message={"parts": [{"text": "Do this"}]})

# Stream A2A response
with client.a2a.send_subscribe("target-agent-id", message={"parts": [{"text": "Do this"}]}) as stream:
    for event in stream:
        print(event)

# Get agent card
card = client.a2a.get_card("agent-id")
```

### Tasks

```python
# List tasks for an agent
for task in client.tasks.list("agent-id"):
    print(task["id"], task["status"])

# Get / cancel a task
task = client.tasks.get("agent-id", "task-id")
client.tasks.cancel("agent-id", "task-id")
```

### Files (Storage)

Files are uploaded privately to the Storage workspace and belong to the authenticated user, so use
`bearer_token`: an `api_key` alone does not identify a user.

```python
# Upload a file (path, bytes, file object or (name, data) tuple), with optional metadata
file = client.files.upload("handbook.pdf", metadata={"team": "docs"})

# Get, download (raw HTTP response)
file = client.files.get(file["id"])
data = client.files.download(file["id"]).content
```

`client.files.delete()` deletes a file you uploaded that no document uses; it answers 409 while a
document does. To remove an indexed file, delete its document from the knowledge base
(`client.knowledge_bases.documents.delete`): the uploaded file is removed with it once no other
document uses it. `client.files.list()` requires edit rights on the Storage workspace.

### Knowledge Bases (Storage)

```python
# Create a knowledge base
kb = client.knowledge_bases.create(name="My Knowledge Base")

# Index an uploaded file by attaching it as a document
file = client.files.upload("handbook.pdf")
doc = client.knowledge_bases.documents.add(kb["id"], native_file_id=file["id"], tags={"team": "docs"})

# Or index a web page
client.knowledge_bases.documents.add(kb["id"], source_url="https://example.com/faq")

# Follow indexing
doc = client.knowledge_bases.documents.get(kb["id"], doc["id"])
print(doc["status"])  # queued, in_progress, completed, failed, ...

# Link to the document's source; an uploaded file's link expires at `expires_at`, resolve it again after
url = client.knowledge_bases.documents.source_url(kb["id"], doc["id"])["url"]

# List and filter
kbs = client.knowledge_bases.list(scope="owned", search="handbook")
failed = client.knowledge_bases.documents.list(kb["id"], status="failed", tags={"team": "docs"})
kb = client.knowledge_bases.get(kb["id"], include="processing")  # adds live processing status

# Update document tags, metadata, expiry or filename
client.knowledge_bases.documents.update(kb["id"], doc["id"], tags={"team": "support"})

# Search
results = client.knowledge_bases.search(kb["id"], query="How to reset password?", limit=5)
for hit in results["data"]:
    print(hit["score"], hit["source_url"])

# Crawl a website on a schedule
client.knowledge_bases.web_sources.add(kb["id"], url="https://example.com/docs")

# Share
client.knowledge_bases.access.grant(kb["id"], principal_type="user", principal_id="user-id", role="reader")

# Remove a document, with its uploaded file once no other document uses it
client.knowledge_bases.documents.delete(kb["id"], doc["id"])
```

### Pagination

All list methods return iterables that auto-paginate:

```python
# Auto-pagination with for loop
for agent in client.agents.list():
    print(agent["name"])

# Manual page control
page = client.agents.list(limit=10)
first_page = page.get_page()
print(first_page.data, first_page.total)

# Collect all into list
all_agents = client.agents.list().to_list()
```

### Error Handling

```python
from prismeai import (
    PrismeAIError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
)

try:
    client.agents.get("nonexistent")
except NotFoundError:
    print("Agent not found")
except RateLimitError as e:
    print(f"Rate limited, retry after {e.retry_after}ms")
except AuthenticationError:
    print("Invalid credentials")
except PrismeAIError as e:
    print(e.message, e.status_code)
```

## Async Usage

```python
import asyncio
from prismeai import AsyncPrismeAI

async def main():
    async with AsyncPrismeAI(api_key="sk-...") as client:
        agent = await client.agents.create(name="Async Agent")

        # Async streaming
        stream = await client.agents.messages.stream(
            "agent-id",
            message={"parts": [{"text": "Hello"}]},
        )
        async with stream:
            async for event in stream:
                print(event)

        # Async pagination
        async for agent in client.agents.list():
            print(agent["name"])

asyncio.run(main())
```

## Migrating from 0.2

Version 0.3 moves storage resources to the Knowledge Bases API. `client.vector_stores` is removed;
existing vector store ids (`vs_...`) are valid knowledge base ids.

| 0.2 | 0.3 |
|-----|-----|
| `vector_stores.list/create/get/update/delete/search` | `knowledge_bases.list/create/get/update/delete/search` |
| `vector_stores.reindex(id)` | `knowledge_bases.reindex(id, **options)`, returns the dispatch status |
| `vector_stores.crawl_status` / `recrawl` | `knowledge_bases.web_sources.list/add/get/delete`; new pages are discovered on the crawl schedule |
| `vector_stores.files.list/add/get/delete` | `knowledge_bases.documents.list/add/get/update/delete` |
| `vector_stores.files.chunks` | `knowledge_bases.documents.chunks`, now an auto-paginating iterable |
| `vector_stores.files.reindex(id, file_id)` | `knowledge_bases.documents.reindex(id, document_id, **options)`, returns the document |
| `vector_stores.access.list/grant/revoke` | `knowledge_bases.access.list/grant/revoke`, plus `update(id, principal_type, principal_id, role=...)` to change a role |
| `files.list(page=..., limit=...)` | `files.list(limit=...)` |

Request bodies use the Knowledge Bases API field names: `native_file_id` or `source_url` to add a
document, `principal_type`, `principal_id` and `role` to grant access. `files.upload` returns the
uploaded file object and accepts `metadata`.

Types: `VectorStore`, `VectorStoreCreate`, `VectorStoreUpdate`, `VectorStoreSearchResult`, `VSFile`
and `VSAccessEntry` become `KnowledgeBase`, `KnowledgeBaseCreate`, `KnowledgeBaseUpdate`,
`SearchHit`, `Document` and `AccessBinding`; `WebSource` is new. `FileObject.mime_type` is now
`mimetype`.

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `api_key` | `str` | `PRISMEAI_API_KEY` env | API key for authentication |
| `bearer_token` | `str` | `PRISMEAI_BEARER_TOKEN` env | Bearer token for auth |
| `base_url` | `str` | `https://api.prisme.ai/v2` | API base URL (for self-hosted) |
| `timeout` | `float` | `60.0` | Request timeout in seconds |
| `max_retries` | `int` | `2` | Max retries on 429/5xx |

## Requirements

- Python 3.9+
- httpx
- pydantic >= 2.0

## License

MIT
