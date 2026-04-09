"""Full feature test for the Prisme.ai Python SDK."""

import os
import sys
import json
import time
import re
import tempfile

# Add src to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from prismeai import PrismeAI, FileAttachment

# ── Config ──────────────────────────────────────────────────────
client = PrismeAI(
    api_key=os.environ.get("PRISMEAI_API_KEY"),
    environment=os.environ.get("PRISMEAI_ENV", "sandbox"),
)

agent_id = None
tool_id = None
conversation_id = None
context_id = None

passed = []
failed = []
skipped = []


# ── Helpers ─────────────────────────────────────────────────────
def log(label, data=None):
    print(f"  ✅ {label}")
    if data is not None:
        s = json.dumps(data, default=str)
        if len(s) > 300:
            print(f"     {s[:300]}...")
        else:
            print(f"     {s}")


def test(name, fn):
    try:
        fn()
        passed.append(name)
    except Exception as e:
        msg = getattr(e, "message", str(e))
        status = getattr(e, "status_code", None)
        print(f"  ❌ {name}: {msg}")
        if status:
            print(f"     Status: {status}")
        failed.append(name)


def skip(name, reason):
    print(f"  ⏭️  {name} — skipped ({reason})")
    skipped.append(name)


# ════════════════════════════════════════════════════════════════
#  1. AGENTS — CRUD + Publish + Discovery + Export/Import
# ════════════════════════════════════════════════════════════════
def test_agents():
    global agent_id
    print("\n── Agents ─────────────────────────────────────")

    def _create():
        global agent_id
        agent = client.agents.create(
            name=f"SDK-Py-Test-{int(time.time())}",
            description="Created by Python SDK test",
            instructions="You are a test assistant. Keep answers very short (under 20 words).",
            model="gpt-4o",
        )
        agent_id = agent["id"]
        log("Created", {"id": agent["id"], "name": agent.get("name")})

    test("agents.create", _create)

    def _get():
        agent = client.agents.get(agent_id)
        log("Got", {"id": agent["id"], "name": agent.get("name")})

    test("agents.get", _get)

    def _update():
        agent = client.agents.update(agent_id, description="Updated by Python SDK test")
        log("Updated", {"id": agent["id"], "description": agent.get("description")})

    test("agents.update", _update)

    def _list():
        items = []
        for agent in client.agents.list():
            items.append(agent["id"])
            if len(items) >= 3:
                break
        log("Listed", {"count": len(items), "ids": items})

    test("agents.list", _list)

    def _export():
        config = client.agents.export(agent_id)
        log("Exported", {"keys": list(config.keys()) if isinstance(config, dict) else str(type(config))})

    test("agents.export", _export)


# ════════════════════════════════════════════════════════════════
#  1b. PUBLISH + DISCOVERY + DISCARD DRAFT
# ════════════════════════════════════════════════════════════════
def test_publish():
    print("\n── Publish + Discovery ────────────────────────")

    def _publish():
        agent = client.agents.publish(agent_id)
        log("Published", {"id": agent["id"]})

    test("agents.publish", _publish)

    def _discovery():
        items = []
        for agent in client.agents.discovery():
            items.append({"id": agent["id"], "name": agent.get("name")})
            if len(items) >= 3:
                break
        log("Discovery listed", {"count": len(items)})

    test("agents.discovery", _discovery)

    def _discard():
        client.agents.update(agent_id, description="Draft change")
        agent = client.agents.discard_draft(agent_id)
        log("Draft discarded", {"id": agent["id"]})

    test("agents.discardDraft", _discard)


# ════════════════════════════════════════════════════════════════
#  2. MESSAGES — Send + Stream + File Attachments
# ════════════════════════════════════════════════════════════════
def test_messages():
    global context_id
    print("\n── Messages ───────────────────────────────────")

    def _send():
        global context_id
        response = client.agents.messages.send(
            agent_id,
            message={"parts": [{"text": "What is 2+2? Answer with just the number."}]},
        )
        if isinstance(response, dict) and response.get("task", {}).get("contextId"):
            context_id = response["task"]["contextId"]
        log("Sent", response)

    test("messages.send", _send)

    def _stream():
        full_text = ""
        event_count = 0
        with client.agents.messages.stream(
            agent_id,
            message={"parts": [{"text": 'Say the word "hello" and nothing else.'}]},
        ) as stream:
            for event in stream:
                event_count += 1
                # Delta events: {__event: "task.output.delta", delta: {parts: [{text}]}}
                if isinstance(event, dict):
                    evt_type = event.get("__event", "")
                    if evt_type == "task.output.delta":
                        parts = event.get("delta", {}).get("parts", [])
                        for p in parts:
                            if isinstance(p, dict) and p.get("text"):
                                full_text += p["text"]
                    elif event.get("text"):
                        full_text += event["text"]
        log("Streamed", {"events": event_count, "text": full_text.strip()})

    test("messages.stream", _stream)

    def _send_with_file_data():
        response = client.agents.messages.send(
            agent_id,
            message={"parts": [{"text": "I am attaching a text file. What does it say?"}]},
            files=[
                FileAttachment(
                    data=b"The secret word is banana.",
                    filename="secret.txt",
                    mime_type="text/plain",
                )
            ],
        )
        log("Sent with file (base64)", response)

    test("messages.send (file attachment - base64)", _send_with_file_data)

    def _send_with_file_path():
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("This is a test document for the Python SDK.")
            tmp_path = f.name
        try:
            response = client.agents.messages.send(
                agent_id,
                message={"parts": [{"text": "Summarize the attached file in one sentence."}]},
                files=[FileAttachment(path=tmp_path)],
            )
            log("Sent with file (path)", response)
        finally:
            os.unlink(tmp_path)

    test("messages.send (file attachment - path)", _send_with_file_path)

    def _stream_with_file():
        full_text = ""
        event_count = 0
        with client.agents.messages.stream(
            agent_id,
            message={"parts": [{"text": "I attached a file. Read it and reply with its content."}]},
            files=[
                FileAttachment(
                    data=b"Stream file test content.",
                    filename="stream-test.txt",
                    mime_type="text/plain",
                )
            ],
        ) as stream:
            for event in stream:
                event_count += 1
                if isinstance(event, dict):
                    evt_type = event.get("__event", "")
                    if evt_type == "task.output.delta":
                        parts = event.get("delta", {}).get("parts", [])
                        for p in parts:
                            if isinstance(p, dict) and p.get("text"):
                                full_text += p["text"]
                    elif event.get("text"):
                        full_text += event["text"]
        log("Streamed with file", {"events": event_count, "text": full_text.strip()[:200]})

    test("messages.stream (file attachment)", _stream_with_file)

    def _send_with_url():
        response = client.agents.messages.send(
            agent_id,
            message={"parts": [{"text": "What do you see in this image?"}]},
            files=[
                FileAttachment(
                    url="https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png",
                    type="image",
                    mime_type="image/png",
                )
            ],
        )
        log("Sent with URL file", response)

    test("messages.send (file attachment - URL)", _send_with_url)


# ════════════════════════════════════════════════════════════════
#  3. CONVERSATIONS
# ════════════════════════════════════════════════════════════════
def test_conversations():
    global conversation_id
    print("\n── Conversations ──────────────────────────────")

    def _list():
        items = []
        for conv in client.conversations.list(agent_id):
            items.append(conv.get("id") or conv.get("contextId"))
            if len(items) >= 3:
                break
        log("Listed", {"count": len(items)})

    test("conversations.list", _list)

    def _create():
        global conversation_id
        conv = client.conversations.create(agent_id)
        # Normalized: SDK now sets id from contextId if needed
        conversation_id = conv.get("id") or conv.get("contextId")
        log("Created", {"id": conversation_id})

    test("conversations.create", _create)

    def _get():
        conv = client.conversations.get(agent_id, conversation_id)
        log("Got", {"id": conv.get("id") or conv.get("contextId")})

    test("conversations.get", _get)

    def _update():
        conv = client.conversations.update(agent_id, conversation_id, title="SDK Py Test Conv")
        log("Updated", {"id": conv.get("id") or conv.get("contextId")})

    test("conversations.update", _update)

    def _delete():
        client.conversations.delete(agent_id, conversation_id)
        log("Deleted", {"id": conversation_id})

    test("conversations.delete", _delete)


# ════════════════════════════════════════════════════════════════
#  4. TOOLS
# ════════════════════════════════════════════════════════════════
def test_tools():
    global tool_id
    print("\n── Tools ──────────────────────────────────────")

    def _create():
        global tool_id
        tool = client.tools.create(
            agent_id,
            type="function",
            name="get_weather",
            description="Get weather for a city",
            schema={
                "type": "object",
                "properties": {"location": {"type": "string", "description": "City name"}},
                "required": ["location"],
            },
        )
        tool_id = tool["id"]
        log("Created", {"id": tool["id"], "name": tool.get("name")})

    test("tools.create", _create)

    def _list():
        items = []
        for tool in client.tools.list(agent_id):
            items.append({"id": tool["id"], "name": tool.get("name")})
        log("Listed", {"count": len(items), "tools": items})

    test("tools.list", _list)

    def _get():
        tool = client.tools.get(agent_id, tool_id)
        log("Got", {"id": tool["id"], "name": tool.get("name")})

    test("tools.get", _get)

    skip("tools.update", "not supported — update agent instead")

    def _delete():
        client.tools.delete(agent_id, tool_id)
        log("Deleted", {"id": tool_id})

    test("tools.delete", _delete)


# ════════════════════════════════════════════════════════════════
#  5. ACCESS
# ════════════════════════════════════════════════════════════════
def test_access():
    print("\n── Access ─────────────────────────────────────")

    def _list():
        items = []
        for entry in client.access.list(agent_id):
            items.append(entry)
            if len(items) >= 3:
                break
        log("Listed", {"count": len(items)})

    test("access.list", _list)
    skip("access.grant", "requires target userId")
    skip("access.revoke", "requires principalType/principalId")


# ════════════════════════════════════════════════════════════════
#  6. ANALYTICS
# ════════════════════════════════════════════════════════════════
def test_analytics():
    print("\n── Analytics ──────────────────────────────────")

    def _get():
        data = client.analytics.get(agent_id, period="7d")
        log("Got analytics", {"keys": list(data.keys()) if isinstance(data, dict) else str(type(data))})

    test("analytics.get", _get)


# ════════════════════════════════════════════════════════════════
#  7. EVALUATIONS
# ════════════════════════════════════════════════════════════════
def test_evaluations():
    print("\n── Evaluations ────────────────────────────────")

    def _list():
        items = []
        for ev in client.evaluations.list(agent_id):
            items.append(ev)
            if len(items) >= 3:
                break
        log("Listed", {"count": len(items)})

    test("evaluations.list", _list)
    skip("evaluations.create", "requires evaluation dataset")


# ════════════════════════════════════════════════════════════════
#  8. A2A
# ════════════════════════════════════════════════════════════════
def test_a2a():
    print("\n── A2A ────────────────────────────────────────")

    def _get_card():
        card = client.a2a.get_card(agent_id)
        log("Got card", {"name": card.get("name") if isinstance(card, dict) else None})

    test("a2a.getCard", _get_card)

    def _get_extended():
        card = client.a2a.get_extended_card(agent_id)
        log("Got extended card", {"keys": list(card.keys()) if isinstance(card, dict) else None})

    test("a2a.getExtendedCard", _get_extended)

    def _send():
        response = client.a2a.send(agent_id, message={"parts": [{"text": "Hello from A2A Python test"}]})
        log("A2A sent", response)

    test("a2a.send", _send)

    def _send_subscribe():
        event_count = 0
        with client.a2a.send_subscribe(agent_id, message={"parts": [{"text": "Hello stream A2A"}]}) as stream:
            for event in stream:
                event_count += 1
                if event_count >= 20:
                    break
        log("A2A streamed", {"events": event_count})

    test("a2a.sendSubscribe", _send_subscribe)


# ════════════════════════════════════════════════════════════════
#  9. TASKS
# ════════════════════════════════════════════════════════════════
def test_tasks():
    print("\n── Tasks ──────────────────────────────────────")

    def _list():
        items = []
        for task in client.tasks.list(agent_id):
            items.append({"id": task["id"], "status": task.get("status")})
            if len(items) >= 3:
                break
        log("Listed", {"count": len(items), "tasks": items})

    test("tasks.list", _list)

    def _get():
        task_id = None
        for task in client.tasks.list(agent_id):
            task_id = task["id"]
            break
        if task_id:
            task = client.tasks.get(agent_id, task_id)
            log("Got", {"id": task["id"], "status": task.get("status")})
        else:
            log("No tasks to get")

    test("tasks.get", _get)
    skip("tasks.cancel", "requires active running task")


# ════════════════════════════════════════════════════════════════
# 10. ARTIFACTS
# ════════════════════════════════════════════════════════════════
def test_artifacts():
    print("\n── Artifacts ──────────────────────────────────")

    def _list():
        items = []
        for artifact in client.artifacts.list():
            items.append(artifact.get("id"))
            if len(items) >= 3:
                break
        log("Listed", {"count": len(items)})

    test("artifacts.list", _list)
    skip("artifacts.get", "requires artifactId")


# ════════════════════════════════════════════════════════════════
# 11. SHARES
# ════════════════════════════════════════════════════════════════
def test_shares():
    print("\n── Shares ─────────────────────────────────────")

    def _list():
        items = []
        for share in client.shares.list():
            items.append(share.get("id"))
            if len(items) >= 3:
                break
        log("Listed", {"count": len(items)})

    test("shares.list", _list)
    skip("shares.get", "requires shareId")


# ════════════════════════════════════════════════════════════════
# 12. RATINGS
# ════════════════════════════════════════════════════════════════
def test_ratings():
    print("\n── Ratings ────────────────────────────────────")

    def _create():
        rating = client.ratings.create(agent_id, rating=5, feedback="Great SDK test from Python!")
        log("Created", rating)

    test("ratings.create", _create)


# ════════════════════════════════════════════════════════════════
# 13. ACTIVITY
# ════════════════════════════════════════════════════════════════
def test_activity():
    print("\n── Activity ───────────────────────────────────")

    def _list():
        items = []
        for entry in client.activity.list():
            items.append(entry)
            if len(items) >= 3:
                break
        log("Listed", {"count": len(items)})

    test("activity.list", _list)


# ════════════════════════════════════════════════════════════════
# 14. PROFILES
# ════════════════════════════════════════════════════════════════
def test_profiles():
    print("\n── Profiles ───────────────────────────────────")

    def _list():
        items = []
        for profile in client.profiles.list():
            items.append(profile)
            if len(items) >= 3:
                break
        log("Listed", {"count": len(items)})

    test("profiles.list", _list)


# ════════════════════════════════════════════════════════════════
# 15. ORGS
# ════════════════════════════════════════════════════════════════
def test_orgs():
    print("\n── Orgs ───────────────────────────────────────")
    skip("orgs.listAgents", "requires orgSlug")


# ════════════════════════════════════════════════════════════════
# 16. STORAGE — Files
# ════════════════════════════════════════════════════════════════
def test_files():
    print("\n── Storage: Files ─────────────────────────────")
    file_id = None

    def _upload():
        nonlocal file_id
        f = client.files.upload(b"Hello from Python SDK test!", filename="sdk-test.txt")
        file_id = f["id"]
        log("Uploaded", {"id": f["id"], "name": f.get("name")})

    test("files.upload", _upload)

    def _list():
        items = []
        for f in client.files.list():
            items.append({"id": f["id"], "name": f.get("name")})
            if len(items) >= 3:
                break
        log("Listed", {"count": len(items)})

    test("files.list", _list)

    def _get():
        if not file_id:
            log("Skipped — no fileId")
            return
        f = client.files.get(file_id)
        log("Got", {"id": f["id"], "name": f.get("name")})

    test("files.get", _get)

    def _download():
        if not file_id:
            log("Skipped — no fileId")
            return
        data = client.files.download(file_id)
        log("Downloaded", {"size": len(data) if data else 0})

    test("files.download", _download)

    def _delete():
        if not file_id:
            log("Skipped — no fileId")
            return
        client.files.delete(file_id)
        log("Deleted", {"id": file_id})

    test("files.delete", _delete)


# ════════════════════════════════════════════════════════════════
# 17. STORAGE — Vector Stores
# ════════════════════════════════════════════════════════════════
def test_vector_stores():
    print("\n── Storage: Vector Stores ─────────────────────")
    vs_id = None

    def _create():
        nonlocal vs_id
        vs = client.vector_stores.create(name=f"SDK-Py-Test-VS-{int(time.time())}")
        vs_id = vs["id"]
        log("Created", {"id": vs["id"], "name": vs.get("name")})

    test("vectorStores.create", _create)

    def _list():
        items = []
        for vs in client.vector_stores.list():
            items.append({"id": vs["id"], "name": vs.get("name")})
            if len(items) >= 3:
                break
        log("Listed", {"count": len(items)})

    test("vectorStores.list", _list)

    def _get():
        if not vs_id:
            log("Skipped")
            return
        vs = client.vector_stores.get(vs_id)
        log("Got", {"id": vs["id"], "name": vs.get("name")})

    test("vectorStores.get", _get)

    def _update():
        if not vs_id:
            log("Skipped")
            return
        vs = client.vector_stores.update(vs_id, name="SDK-Py-Test-VS-Updated")
        log("Updated", {"id": vs["id"], "name": vs.get("name")})

    test("vectorStores.update", _update)

    def _search():
        if not vs_id:
            log("Skipped")
            return
        results = client.vector_stores.search(vs_id, query="test search", limit=3)
        log("Searched", {"results": len(results) if results else 0})

    test("vectorStores.search", _search)

    def _delete():
        if not vs_id:
            log("Skipped")
            return
        client.vector_stores.delete(vs_id)
        log("Deleted", {"id": vs_id})

    test("vectorStores.delete", _delete)


# ════════════════════════════════════════════════════════════════
# 18. STORAGE — Skills
# ════════════════════════════════════════════════════════════════
def test_skills():
    print("\n── Storage: Skills ────────────────────────────")
    skill_id = None

    def _create():
        nonlocal skill_id
        skill = client.skills.create(
            name=f"SDK-Py-Test-Skill-{int(time.time())}",
            type="text",
            description="Test skill from Python SDK",
            instructions="You are a test skill. Answer briefly.",
        )
        skill_id = skill["id"]
        log("Created", {"id": skill["id"], "name": skill.get("name")})

    test("skills.create", _create)

    def _list():
        items = []
        for skill in client.skills.list():
            items.append({"id": skill["id"], "name": skill.get("name")})
            if len(items) >= 3:
                break
        log("Listed", {"count": len(items)})

    test("skills.list", _list)

    def _get():
        if not skill_id:
            log("Skipped")
            return
        skill = client.skills.get(skill_id)
        log("Got", {"id": skill["id"], "name": skill.get("name")})

    test("skills.get", _get)

    def _update():
        if not skill_id:
            log("Skipped")
            return
        skill = client.skills.update(skill_id, description="Updated Python test skill")
        log("Updated", {"id": skill["id"]})

    test("skills.update", _update)

    def _delete():
        if not skill_id:
            log("Skipped")
            return
        client.skills.delete(skill_id)
        log("Deleted", {"id": skill_id})

    test("skills.delete", _delete)


# ════════════════════════════════════════════════════════════════
# 19. STORAGE — Stats
# ════════════════════════════════════════════════════════════════
def test_stats():
    print("\n── Storage: Stats ─────────────────────────────")

    def _get():
        stats = client.stats.get()
        log("Got stats", stats)

    test("stats.get", _get)


# ════════════════════════════════════════════════════════════════
# 20. AGENTS IMPORT
# ════════════════════════════════════════════════════════════════
def test_import():
    print("\n── Import ─────────────────────────────────────")

    def _import():
        config = client.agents.export(agent_id)
        # Export returns YAML front matter + markdown instructions
        yaml_config = config if isinstance(config, str) else str(config)
        yaml_config = re.sub(r'^name:.*$', f'name: SDK-Py-Imported-{int(time.time())}', yaml_config, flags=re.MULTILINE)
        imported = client.agents.import_(yaml_config)
        log("Imported", {"id": imported["id"], "name": imported.get("name")})
        client.agents.delete(imported["id"])
        log("Cleaned up imported agent")

    test("agents.import", _import)


# ════════════════════════════════════════════════════════════════
# CLEANUP
# ════════════════════════════════════════════════════════════════
def cleanup():
    print("\n── Cleanup ────────────────────────────────────")
    if agent_id:
        try:
            client.agents.delete(agent_id)
            log("Deleted test agent", {"id": agent_id})
        except Exception as e:
            print(f"  ⚠️  Failed to delete agent: {e}")


# ════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════
def main():
    print("🚀 Prisme.ai Python SDK — Full Feature Test")
    print("═" * 50)
    print(f"Environment: {os.environ.get('PRISMEAI_ENV', 'sandbox')}")
    print(f"API Key: {'✅ set' if os.environ.get('PRISMEAI_API_KEY') else '❌ missing!'}")
    print("═" * 50)

    try:
        # Agent Factory
        test_agents()
        test_tools()       # Before publish to ensure tools visible on agent
        test_publish()     # Publish after tools are created
        time.sleep(1)
        test_messages()
        test_conversations()
        test_access()
        test_analytics()
        test_evaluations()
        test_a2a()
        test_tasks()
        test_artifacts()
        test_shares()
        test_ratings()
        test_activity()
        test_profiles()
        test_orgs()
        test_import()

        # Storage
        test_files()
        test_vector_stores()
        test_skills()
        test_stats()
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")

    # Always cleanup
    cleanup()

    # Summary
    print("\n" + "═" * 50)
    print("📊 RESULTS")
    print("═" * 50)
    print(f"  ✅ Passed:  {len(passed)}")
    print(f"  ❌ Failed:  {len(failed)}")
    print(f"  ⏭️  Skipped: {len(skipped)}")
    print(f"  📦 Total:   {len(passed) + len(failed) + len(skipped)}")

    if failed:
        print("\n  Failed tests:")
        for name in failed:
            print(f"    - {name}")

    print("")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
