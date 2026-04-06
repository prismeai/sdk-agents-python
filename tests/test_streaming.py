from prismeai._streaming import SSEDecoder


def test_sse_decoder_basic():
    decoder = SSEDecoder()
    events = decoder.feed('data: {"type":"delta","text":"Hello"}')
    assert events == []

    events = decoder.feed("")  # empty line = end of event
    assert len(events) == 1
    assert events[0]["type"] == "delta"
    assert events[0]["text"] == "Hello"


def test_sse_decoder_done():
    decoder = SSEDecoder()
    decoder.feed("data: [DONE]")
    events = decoder.feed("")
    assert events == [None] or events == []


def test_sse_decoder_event_type():
    decoder = SSEDecoder()
    decoder.feed("event: message")
    decoder.feed('data: {"text":"Hello"}')
    events = decoder.feed("")
    assert len(events) == 1
    assert events[0]["__event"] == "message"


def test_sse_decoder_multiline_data():
    decoder = SSEDecoder()
    decoder.feed("data: line1")
    decoder.feed("data: line2")
    events = decoder.feed("")
    assert len(events) == 1
    # Non-JSON multiline data
    assert events[0]["data"] == "line1\nline2"


def test_sse_decoder_empty_data():
    decoder = SSEDecoder()
    events = decoder.feed("")
    assert events == []


def test_sse_decoder_comments_ignored():
    decoder = SSEDecoder()
    events = decoder.feed(": this is a comment")
    assert events == []
