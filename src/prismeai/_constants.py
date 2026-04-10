from __future__ import annotations

DEFAULT_BASE_URL = "https://api.studio.prisme.ai/v2"
DEFAULT_TIMEOUT = 60.0
DEFAULT_MAX_RETRIES = 2
INITIAL_RETRY_DELAY = 0.5
MAX_RETRY_DELAY = 8.0
RETRY_STATUS_CODES = frozenset({408, 429, 500, 502, 503, 504})
