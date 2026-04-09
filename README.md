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

```python
# Upload a file
file = client.files.upload(b"Hello World", filename="hello.txt")

# List files
for f in client.files.list():
    print(f["name"], f.get("size"))

# Download
data = client.files.download(file["id"])
```

### Vector Stores (Storage)

```python
# Create a vector store
vs = client.vector_stores.create(name="My Knowledge Base")

# Search
results = client.vector_stores.search(vs["id"], query="How to reset password?", limit=5)

# Manage files
client.vector_stores.files.add(vs["id"], file_id="file-id")

for f in client.vector_stores.files.list(vs["id"]):
    print(f["name"], f.get("status"))
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
