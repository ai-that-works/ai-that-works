"""Constants for the Loops API."""

# API Configuration
LOOPS_BASE_URL = "https://app.loops.so/api/v1"

# Loops allows 10 requests/second per team. Stay under it.
LOOPS_REQUESTS_PER_SECOND = 8

# Retry behavior for 429 / 5xx responses
LOOPS_MAX_RETRIES = 5
LOOPS_BACKOFF_SECONDS = 1.0

# Per-request timeout. Loops occasionally stalls on a lookup.
LOOPS_TIMEOUT_SECONDS = 60

# Default value shown in the Loops UI as the contact's origin
DEFAULT_CONTACT_SOURCE = "Luma"
