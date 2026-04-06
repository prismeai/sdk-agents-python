from __future__ import annotations

ENVIRONMENTS: dict[str, str] = {
    "sandbox": "https://api.sandbox.prisme.ai/v2",
    "production": "https://api.eda.prisme.ai/v2",
    "prod": "https://api.eda.prisme.ai/v2",
}

DEFAULT_BASE_URL = ENVIRONMENTS["production"]
DEFAULT_TIMEOUT = 60.0
DEFAULT_MAX_RETRIES = 2
INITIAL_RETRY_DELAY = 0.5
MAX_RETRY_DELAY = 8.0
RETRY_STATUS_CODES = frozenset({408, 429, 500, 502, 503, 504})
