# Rate Limiting System

## Overview

AI Goals Tracker V2 includes a comprehensive rate limiting system to:
- **Prevent token abuse** - Block excessive OpenAI API calls that consume tokens/costs
- **Track usage** - Monitor every request with full OpenAI token consumption data
- **Detect abuse** - Identify suspicious activity patterns automatically
- **Audit compliance** - Complete audit trail for all requests
- **Cost management** - Estimate and track OpenAI costs in real-time

## Architecture

### Components

1. **Token Bucket Algorithm** (`app/core/rate_limiter.py`)
   - Redis-based distributed rate limiting
   - Atomic operations using Lua scripts
   - Configurable per-action limits
   - Burst traffic support

2. **Middleware** (`app/middleware/rate_limit_middleware.py`)
   - Auto-applies to all API requests
   - Returns HTTP 429 with retry-after headers
   - Automatic audit logging

3. **OpenAI Token Tracker** (`app/core/openai_tracker.py`)
   - Wraps all OpenAI API calls
   - Tracks prompt/completion tokens
   - Request-scoped tracking with ContextVar

4. **Audit Service** (`app/services/rate_limit_audit_service.py`)
   - Logs every request to PostgreSQL
   - Calculates costs automatically
   - Detects suspicious patterns
   - Generates statistics

5. **Admin API** (`app/api/routes/admin/rate_limits.py`)
   - Monitor user limits
   - View audit logs
   - Reset limits
   - Get statistics

## How It Works

### Token Bucket Algorithm

The Token Bucket algorithm allows for:
- **Steady-state limiting** - Max X requests per minute
- **Burst support** - Temporary spikes allowed up to burst_multiplier
- **Auto-refill** - Tokens regenerate at constant rate

**Example:**
```
Config: max_requests=100/min, burst_multiplier=1.5
- Normal limit: 100 requests/minute
- Burst limit: 150 requests (short bursts allowed)
- Refill rate: 100/60 = 1.67 tokens/second
```

**Lua Script (Atomic):**
```lua
1. Get current tokens in bucket
2. Calculate tokens to add based on time passed
3. Refill bucket (up to max capacity)
4. Try to consume requested tokens
5. If success: deduct tokens, update Redis
6. If fail: return retry_after time
```

### Request Flow

```
1. User makes request → Middleware intercepts
2. Check rate limit (Token Bucket) → Redis
3. Log to audit table → PostgreSQL
4. If allowed:
   - Process request
   - Track OpenAI tokens (if applicable)
   - Add rate limit headers to response
5. If blocked:
   - Return HTTP 429
   - Log blocked request
   - Detect if suspicious
```

## Rate Limit Configurations

### Default Limits

| Action | Max/Minute | Burst Multiplier | Effective Burst |
|--------|-----------|------------------|-----------------|
| `api_call` | 100 | 1.5x | 150 |
| `embedding_generation` | 20 | 1.2x | 24 |
| `chat_completion` | 10 | 1.0x | 10 (no burst) |
| `code_validation` | 30 | 1.3x | 39 |
| `rag_search` | 50 | 1.5x | 75 |
| `bulk_create` | 5 | 1.0x | 5 (no burst) |

### Modifying Limits

Edit `app/core/rate_limiter.py`:

```python
class RateLimiter:
    def __init__(self, redis_client: redis.Redis):
        self.configs = {
            "embedding_generation": RateLimitConfig(
                max_requests=50,  # Increase from 20 to 50
                window_seconds=60,
                burst_multiplier=1.5  # Allow more bursts
            ),
        }
```

## OpenAI Token Tracking

### Automatic Tracking

All OpenAI calls are automatically tracked:

```python
# RAG tools use OpenAITracker
from app.core.openai_tracker import OpenAITracker

tracker = OpenAITracker()
embedding = await tracker.create_embedding("text")

# Token usage is automatically recorded
usage = OpenAITracker.get_current_usage()
# {
#   "prompt_tokens": 120,
#   "completion_tokens": 0,
#   "total_tokens": 120,
#   "model": "text-embedding-3-small"
# }
```

### Cost Calculation

Costs are calculated automatically based on model pricing:

| Model | Input Cost | Output Cost |
|-------|-----------|-------------|
| text-embedding-3-small | $0.02 / 1M tokens | N/A |
| text-embedding-3-large | $0.13 / 1M tokens | N/A |
| gpt-3.5-turbo | $0.50 / 1M tokens | $1.50 / 1M tokens |
| gpt-4 | $30.00 / 1M tokens | $60.00 / 1M tokens |

**Example:**
```
Request: 500 tokens with text-embedding-3-small
Cost: (500 / 1,000,000) * $0.02 = $0.00001 = 0.001¢
```

## Audit System

### What's Logged

Every request logs:
- User ID, endpoint, method, action type
- Rate limit result (allowed/blocked)
- Tokens requested/consumed/available
- OpenAI token usage (prompt/completion/total)
- Estimated cost in USD
- Response time
- IP address, user agent
- Suspicious activity flags

### Suspicious Activity Detection

Automatically detects:
1. **Excessive requests** - >5x normal rate in 5 minutes
2. **Multiple blocks** - >10 blocked requests in 5 minutes

Flagged requests include `alert_reason`:
```
"Excessive requests: 150 in 5 minutes (threshold: 100)"
"Multiple rate limit violations: 12 blocked requests in 5 minutes"
```

## Admin API Endpoints

### 1. Get User Rate Limit Status

```bash
GET /api/v1/admin/rate-limits/users/{user_id}/status
```

**Response:**
```json
{
  "user_id": "usr_123",
  "timestamp": "2025-01-15T10:30:00",
  "limits": {
    "embedding_generation": {
      "available_tokens": 18,
      "max_capacity": 24,
      "refill_rate": 0.33,
      "current_count": 2,
      "max_requests": 20,
      "window_seconds": 60
    }
  }
}
```

### 2. Get Audit Logs

```bash
GET /api/v1/admin/rate-limits/audits?user_id=usr_123&only_blocked=true&limit=50
```

**Query Parameters:**
- `user_id` - Filter by user
- `action` - Filter by action type
- `start_date` - Start date (ISO)
- `end_date` - End date (ISO)
- `only_blocked` - Only blocked requests
- `only_suspicious` - Only suspicious activity
- `limit` - Max results (1-1000)

### 3. Get Statistics

```bash
# User statistics
GET /api/v1/admin/rate-limits/statistics?user_id=usr_123

# Global statistics
GET /api/v1/admin/rate-limits/statistics
```

**Response:**
```json
{
  "user_id": "usr_123",
  "period": {
    "start": "2025-01-15T00:00:00",
    "end": "2025-01-16T00:00:00"
  },
  "requests": {
    "total": 450,
    "allowed": 420,
    "blocked": 30,
    "block_rate": 0.067
  },
  "by_action": {
    "embedding_generation": {
      "total": 180,
      "allowed": 170,
      "blocked": 10
    }
  },
  "openai": {
    "total_tokens": 125000,
    "estimated_cost_usd": 2.50
  },
  "alerts": {
    "total": 5
  },
  "performance": {
    "avg_response_time_ms": 250
  }
}
```

### 4. Reset User Limits

```bash
# Reset all limits
POST /api/v1/admin/rate-limits/users/{user_id}/reset

# Reset specific action
POST /api/v1/admin/rate-limits/users/{user_id}/reset?action=embedding_generation
```

### 5. Get Top Consumers

```bash
GET /api/v1/admin/rate-limits/top-consumers?action=embedding_generation&hours=24&limit=10
```

**Response:**
```json
{
  "period_hours": 24,
  "action": "embedding_generation",
  "top_consumers": [
    {
      "user_id": "usr_456",
      "request_count": 1850,
      "total_tokens": 450000,
      "total_cost_usd": 9.00
    }
  ]
}
```

### 6. Get Suspicious Activities

```bash
GET /api/v1/admin/rate-limits/suspicious?hours=24&limit=100
```

### 7. Get Rate Limit Config

```bash
GET /api/v1/admin/rate-limits/config
```

**Response:**
```json
{
  "configs": {
    "api_call": {
      "max_requests": 100,
      "window_seconds": 60,
      "burst_multiplier": 1.5,
      "effective_burst_limit": 150,
      "description": "General API calls"
    }
  },
  "algorithm": "Token Bucket",
  "backend": "Redis"
}
```

## Response Headers

All responses include rate limit headers:

```
X-RateLimit-Limit: 100           # Max requests in window
X-RateLimit-Remaining: 85        # Tokens available
X-RateLimit-Reset: 1705318200    # Unix timestamp when resets
```

When rate limited (HTTP 429):

```
Retry-After: 30                  # Seconds to wait before retry
```

## Database Schema

### `rate_limit_audits` Table

```sql
CREATE TABLE rate_limit_audits (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    endpoint VARCHAR NOT NULL,
    method VARCHAR NOT NULL,
    action ratelimitaction NOT NULL,
    status ratelimitstatus NOT NULL,

    -- Rate limit info
    allowed BOOLEAN NOT NULL,
    tokens_requested INTEGER NOT NULL,
    tokens_available INTEGER NOT NULL,
    tokens_consumed INTEGER NOT NULL,

    -- OpenAI tracking
    openai_prompt_tokens INTEGER,
    openai_completion_tokens INTEGER,
    openai_total_tokens INTEGER,
    openai_model VARCHAR,
    estimated_cost_cents FLOAT,

    -- Performance
    response_time_ms FLOAT,
    http_status_code INTEGER,

    -- Rate limit details
    rate_limit_key VARCHAR,
    rate_limit_window_seconds INTEGER,
    rate_limit_max_requests INTEGER,
    current_request_count INTEGER,

    -- Security
    is_suspicious BOOLEAN DEFAULT FALSE,
    alert_triggered BOOLEAN DEFAULT FALSE,
    alert_reason VARCHAR,
    ip_address VARCHAR,
    user_agent VARCHAR,

    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_rate_limit_audits_user_action ON rate_limit_audits(user_id, action, timestamp);
CREATE INDEX idx_rate_limit_audits_suspicious ON rate_limit_audits(is_suspicious, timestamp);
CREATE INDEX idx_rate_limit_audits_timestamp ON rate_limit_audits(timestamp);
CREATE INDEX idx_rate_limit_audits_action ON rate_limit_audits(action, timestamp);
CREATE INDEX idx_rate_limit_audits_user ON rate_limit_audits(user_id, timestamp);
```

## Testing Rate Limits

### Manual Testing

```bash
# Test normal request (should succeed)
curl -H "X-User-ID: test-user" http://localhost:8000/api/v1/goals

# Spam requests to trigger rate limit
for i in {1..150}; do
  curl -H "X-User-ID: test-user" http://localhost:8000/api/v1/goals
done
# Should start getting HTTP 429 after limit exceeded

# Check user status
curl http://localhost:8000/api/v1/admin/rate-limits/users/test-user/status

# View blocked requests
curl "http://localhost:8000/api/v1/admin/rate-limits/audits?only_blocked=true&limit=10"

# Reset limits
curl -X POST http://localhost:8000/api/v1/admin/rate-limits/users/test-user/reset
```

### Unit Tests

```python
# tests/test_rate_limiter.py
import pytest
from app.core.rate_limiter import RateLimiter, RateLimitConfig

@pytest.mark.asyncio
async def test_token_bucket_allows_within_limit(redis_client):
    limiter = RateLimiter(redis_client)

    # First request should be allowed
    result = await limiter.check_limit("user_123", "api_call", tokens=1)
    assert result.allowed == True
    assert result.tokens_consumed == 1

@pytest.mark.asyncio
async def test_token_bucket_blocks_over_limit(redis_client):
    limiter = RateLimiter(redis_client)

    # Consume all tokens
    for i in range(100):
        await limiter.check_limit("user_123", "api_call", tokens=1)

    # Next request should be blocked
    result = await limiter.check_limit("user_123", "api_call", tokens=1)
    assert result.allowed == False
    assert result.retry_after_seconds is not None
```

## Monitoring and Alerts

### Key Metrics to Monitor

1. **Block Rate** - % of requests blocked
   - Alert if >10% globally
   - Alert if >50% for specific user

2. **Suspicious Activity** - Flagged requests
   - Alert immediately on suspicious patterns

3. **Cost Tracking** - OpenAI token consumption
   - Alert if daily cost exceeds threshold
   - Track per-user costs

4. **Performance** - Response times
   - Monitor avg response time in audit logs

### Queries for Monitoring

```sql
-- Block rate (last hour)
SELECT
    COUNT(*) FILTER (WHERE NOT allowed) * 100.0 / COUNT(*) as block_rate_percent
FROM rate_limit_audits
WHERE timestamp > NOW() - INTERVAL '1 hour';

-- Top 10 users by cost (today)
SELECT
    user_id,
    SUM(openai_total_tokens) as total_tokens,
    SUM(estimated_cost_cents) / 100.0 as total_cost_usd
FROM rate_limit_audits
WHERE timestamp::date = CURRENT_DATE
GROUP BY user_id
ORDER BY total_cost_usd DESC
LIMIT 10;

-- Suspicious activities (last 24h)
SELECT user_id, COUNT(*) as alert_count
FROM rate_limit_audits
WHERE is_suspicious = true
  AND timestamp > NOW() - INTERVAL '24 hours'
GROUP BY user_id
ORDER BY alert_count DESC;
```

## Best Practices

### For Developers

1. **Use OpenAITracker** - Always wrap OpenAI calls
   ```python
   # ✅ Good
   tracker = OpenAITracker()
   embedding = await tracker.create_embedding(text)

   # ❌ Bad
   client = AsyncOpenAI()
   embedding = await client.embeddings.create(input=text)
   ```

2. **Batch operations** - Use bulk endpoints when possible
   ```python
   # ✅ Good - Uses 1 rate limit token
   embeddings = await tracker.create_embeddings_batch([text1, text2, text3])

   # ❌ Bad - Uses 3 rate limit tokens
   emb1 = await tracker.create_embedding(text1)
   emb2 = await tracker.create_embedding(text2)
   emb3 = await tracker.create_embedding(text3)
   ```

3. **Handle 429 responses** - Implement retry logic
   ```python
   import time

   response = requests.post(url)
   if response.status_code == 429:
       retry_after = int(response.headers.get('Retry-After', 60))
       time.sleep(retry_after)
       response = requests.post(url)  # Retry
   ```

### For Admins

1. **Monitor daily** - Check suspicious activities
2. **Review costs** - Track OpenAI token consumption
3. **Adjust limits** - Increase for power users if needed
4. **Reset carefully** - Only reset limits for legitimate cases

## Troubleshooting

### Issue: Redis connection errors

**Symptom:** Rate limiter fails with Redis errors

**Solution:**
- Check Redis is running: `docker ps | grep redis`
- Verify REDIS_URL in `.env`
- Rate limiter fails-open (allows requests) on Redis errors

### Issue: All requests blocked

**Symptom:** Getting HTTP 429 immediately

**Solution:**
```bash
# Check user status
curl /api/v1/admin/rate-limits/users/{user_id}/status

# Reset limits
curl -X POST /api/v1/admin/rate-limits/users/{user_id}/reset
```

### Issue: Costs not calculating

**Symptom:** `estimated_cost_cents` is NULL in audit logs

**Solution:**
- Ensure OpenAITracker is used for all OpenAI calls
- Check openai_usage is passed to audit service

### Issue: Middleware not applying

**Symptom:** No rate limiting happening

**Solution:**
- Check middleware is registered in `main.py`
- Verify `enabled=True` parameter
- Check path not in EXCLUDED_PATHS

## Future Enhancements

1. **User tiers** - Different limits for free/pro/enterprise
2. **Dynamic limits** - Adjust based on load
3. **Grafana dashboards** - Real-time monitoring
4. **Slack alerts** - Notify on suspicious activity
5. **IP-based limiting** - Additional layer of protection
6. **JWT integration** - Remove X-User-ID header hack
