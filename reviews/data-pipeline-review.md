# Data Pipeline Review

**Review Date:** 2026-01-21
**Scope:** connectors/, etl/, jobs/ directories
**Confidence Threshold:** >70% for reported issues

## Executive Summary

The data pipeline is well-structured with clear separation of concerns. Key strengths include comprehensive error handling in most areas, good deduplication logic, and robust source tracking. However, there are several high-confidence issues around resource management, error handling gaps, and idempotency concerns that should be addressed.

**Critical Issues:** 2
**High Priority:** 8
**Medium Priority:** 6
**Low Priority:** 3

---

## 1. CRITICAL ISSUES

### 1.1 HTTP Client Resource Leak in Connectors

**Confidence:** 95%
**Files:**
- `connectors/va_gov.py:59-69, 333-345`
- `connectors/careeronestop.py:115-125, 350-362`

**Issue:** Both `VAGovConnector` and `CareerOneStopConnector` create HTTP clients that are only closed if used as context managers. In `run()` method, `_get_client()` is called but the client is never explicitly closed.

```python
# va_gov.py:78-85
def run(self) -> list[ResourceCandidate]:
    resources: list[ResourceCandidate] = []
    client = self._get_client()  # Creates client

    for facility_type in ["health", "benefits", "vet_center"]:
        page_resources = self._fetch_facilities_by_type(client, facility_type)
        resources.extend(page_resources)

    return resources  # Client never closed!
```

**Impact:** Unclosed HTTP connections will accumulate, potentially causing connection pool exhaustion in long-running processes or scheduled jobs.

**Recommendation:**
```python
def run(self) -> list[ResourceCandidate]:
    resources: list[ResourceCandidate] = []

    try:
        client = self._get_client()
        for facility_type in ["health", "benefits", "vet_center"]:
            page_resources = self._fetch_facilities_by_type(client, facility_type)
            resources.extend(page_resources)
    finally:
        self.close()  # Ensure cleanup

    return resources
```

---

### 1.2 File Handle Leak in SSVF Connector

**Confidence:** 90%
**File:** `connectors/ssvf.py:70-96`

**Issue:** Excel workbook is opened but only closed explicitly on successful path. If exception occurs after `openpyxl.load_workbook()` but before `workbook.close()`, file handle leaks.

```python
workbook = openpyxl.load_workbook(self.data_path, read_only=True)
sheet = workbook.active
if sheet is None:
    raise ValueError("Excel file has no active sheet")  # Leaks workbook!
# ... more code that could raise exceptions
workbook.close()
```

**Impact:** File handle exhaustion in environments with many repeated runs.

**Recommendation:**
```python
with openpyxl.load_workbook(self.data_path, read_only=True) as workbook:
    sheet = workbook.active
    if sheet is None:
        raise ValueError("Excel file has no active sheet")
    # ... rest of code
```

---

## 2. HIGH PRIORITY ISSUES

### 2.1 Missing Data Validation in Connectors

**Confidence:** 85%
**Files:**
- `connectors/va_gov.py:139-213`
- `connectors/careeronestop.py:210-262`
- `connectors/hud_vash.py:217-284`

**Issue:** Connectors access nested dictionary keys without validation, risking `KeyError` or `AttributeError`.

Example from `va_gov.py:154`:
```python
address_obj = attrs.get("address", {}).get("physical", {})
# What if attrs["address"] is None instead of missing?
```

Example from `careeronestop.py:230-234`:
```python
phone = center.get("Phone")
email = center.get("Email")
address = center.get("Address")
# No validation that these are strings vs other types
```

**Impact:** Pipeline failures with cryptic error messages that don't indicate which resource or field caused the issue.

**Recommendation:** Add defensive checks:
```python
attrs = facility.get("attributes") or {}
address_obj = {}
if isinstance(attrs.get("address"), dict):
    address_obj = attrs["address"].get("physical") or {}
```

---

### 2.2 Silent Data Corruption in Phone Normalization

**Confidence:** 80%
**Files:**
- `connectors/base.py:89-99`
- `etl/normalize.py:272-286`

**Issue:** Phone normalization silently returns original phone number if it doesn't match expected formats, potentially storing malformed data.

```python
def _normalize_phone(self, phone: str | None) -> str | None:
    if not phone:
        return None
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == "1":
        return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    return phone  # Returns malformed phone unchanged!
```

**Impact:** Database contains inconsistent phone formats, making search and validation difficult.

**Recommendation:** Return `None` for unparseable phone numbers or log warnings:
```python
else:
    logger.warning(f"Invalid phone format: {phone}")
    return None  # Or phone.strip() with warning
```

---

### 2.3 Unsafe Datetime Usage - Deprecated `utcnow()`

**Confidence:** 90%
**Files:**
- `etl/loader.py:58, 143, 235, 334, 397`
- `etl/pipeline.py:58, 102, 131`

**Issue:** Using deprecated `datetime.utcnow()` instead of `datetime.now(UTC)` which can cause timezone issues.

```python
# etl/loader.py:235
now = datetime.utcnow()  # Deprecated, naive datetime
```

While other files correctly use `datetime.now(UTC)`, the ETL loader uses the deprecated form.

**Impact:** Timezone-naive datetimes can cause comparison issues and incorrect trust score calculations.

**Recommendation:** Consistently use `datetime.now(UTC)` everywhere.

---

### 2.4 Non-Idempotent ETL Pipeline

**Confidence:** 85%
**File:** `etl/loader.py:96-125`

**Issue:** `load_batch()` commits after **each** resource instead of in a transaction. If the job is interrupted and rerun, some resources will be duplicated or have inconsistent state.

```python
def load_batch(self, resources: list[NormalizedResource]) -> tuple[list[LoadResult], list[ETLError]]:
    results: list[LoadResult] = []
    errors: list[ETLError] = []

    for resource in resources:
        result = self.load(resource)  # Commits inside load()!
        results.append(result)
```

**Impact:** Re-running a failed ETL job will duplicate records or create inconsistent state. Not safe to retry.

**Recommendation:** Either:
1. Use a transaction for the entire batch
2. Mark resources as "processing" before starting and check this flag on retry
3. Use proper upsert logic based on content hashes

---

### 2.5 Race Condition in Organization Caching

**Confidence:** 75%
**File:** `etl/loader.py:127-157`

**Issue:** Organization cache is not thread-safe. If ETL pipeline is run in parallel (which scheduler might do), cache can have stale data.

```python
# Cache lookup
if org_key in self._org_cache:
    return self._org_cache[org_key]

# DB lookup
org = self.session.exec(stmt).first()

# Update cache
self._org_cache[org_key] = org
```

Between cache check and DB query, another thread could create the same organization.

**Impact:** Duplicate organizations in database if jobs run concurrently.

**Recommendation:**
1. Document that Loader is not thread-safe
2. Add database unique constraint on `Organization.name` (case-insensitive)
3. Handle `IntegrityError` and retry lookup

---

### 2.6 Missing Retry Logic for API Calls

**Confidence:** 80%
**Files:**
- `connectors/va_gov.py:100-135`
- `connectors/careeronestop.py:157-193`

**Issue:** No retry logic for transient API failures (network timeouts, rate limits, 503 errors).

```python
try:
    response = client.get(self.BASE_URL, params={...})
    response.raise_for_status()
    # ...
except httpx.HTTPError as e:
    print(f"Error fetching {facility_type} facilities page {page}: {e}")
    break  # Gives up immediately!
```

**Impact:** Transient network issues cause incomplete data fetches. Jobs must be manually re-run.

**Recommendation:** Use exponential backoff retry:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _fetch_with_retry(self, client, url, params):
    response = client.get(url, params=params)
    response.raise_for_status()
    return response
```

---

### 2.7 No Database Rollback on ETL Failure

**Confidence:** 85%
**File:** `etl/pipeline.py:86-93, 127`

**Issue:** Pipeline catches connector exceptions but doesn't rollback the session. Partial data from successful connectors remains committed.

```python
try:
    candidates = connector.run()
    # ... normalize and load ...
except Exception as e:
    errors.append(ETLError(...))
    # No session.rollback() here!
```

**Impact:** Database left in inconsistent state if one connector fails mid-batch.

**Recommendation:**
```python
except Exception as e:
    self.session.rollback()  # Rollback partial changes
    errors.append(ETLError(...))
```

---

### 2.8 Silent Failure in Hash Generation

**Confidence:** 75%
**File:** `etl/normalize.py:416-432`

**Issue:** `_generate_hash()` silently handles missing fields by using empty strings. Two different resources with missing data could get the same hash.

```python
content = "|".join([
    resource.title.lower(),
    resource.org_name.lower(),
    resource.description[:500].lower() if resource.description else "",  # Could be empty
    resource.source_url.lower(),
    resource.address.lower() if resource.address else "",  # Empty
    resource.city.lower() if resource.city else "",  # Empty
    # ...
])
```

**Impact:** Hash collisions cause incorrect deduplication.

**Recommendation:** Include field names in hash or use a sentinel value:
```python
content = "|".join([
    f"title:{resource.title.lower()}",
    f"org:{resource.org_name.lower()}",
    f"desc:{resource.description[:500].lower() if resource.description else 'NONE'}",
    # ...
])
```

---

## 3. MEDIUM PRIORITY ISSUES

### 3.1 Infinite Retry Potential in Deduplicator

**Confidence:** 70%
**File:** `etl/dedupe.py:116-128`

**Issue:** The nested loop in `_dedupe_group()` could have quadratic behavior for large groups of similar resources.

```python
for resource in sorted_group:
    is_duplicate = False
    for kept in keep:  # Inner loop grows with each iteration
        if self._are_duplicates(resource, kept):
            # ...
```

**Impact:** Performance degradation with many similar resources from the same organization.

**Recommendation:** Acceptable for current scale, but add monitoring/logging if group size > 100.

---

### 3.2 Unvalidated State Codes Allow Invalid Data

**Confidence:** 75%
**File:** `etl/normalize.py:288-302`

**Issue:** `_normalize_state()` returns `None` for invalid state codes but doesn't log or warn, so invalid data is silently dropped.

```python
if len(state) == 2:
    code = state.upper()
    return code if code in US_STATES else None  # Silent failure
```

**Impact:** Data loss without visibility into why resources are missing state information.

**Recommendation:** Add warning logs for invalid states.

---

### 3.3 Missing Validation for URL Schemes

**Confidence:** 70%
**File:** `etl/normalize.py:323-342`

**Issue:** URL normalization adds `https://` but doesn't validate the resulting URL structure.

```python
if not url.startswith(("http://", "https://")):
    url = f"https://{url}"  # What if url is "javascript:alert(1)"?
```

**Impact:** Could store XSS vectors or invalid URLs in database.

**Recommendation:**
```python
# Add protocol validation
parsed = urlparse(url)
if parsed.scheme not in ("http", "https"):
    return ""  # Reject invalid schemes
```

---

### 3.4 Geocoder Implementations Are Stubs

**Confidence:** 100%
**Files:**
- `etl/enrich.py:31-40, 269-313`

**Issue:** All geocoder implementations return `None`. This is documented as TODO but means geocoding never happens.

**Impact:** No lat/lng data for location-based search features.

**Recommendation:** Either implement or remove the stub classes to avoid confusion.

---

### 3.5 Jobs Use `print()` Instead of Proper Logging

**Confidence:** 85%
**Files:**
- `jobs/base.py:167-178`
- `jobs/scheduler.py:111, 122`

**Issue:** All jobs use `print()` for logging instead of Python's `logging` module.

```python
def _log(self, message: str, level: str = "info") -> None:
    timestamp = datetime.now(UTC).isoformat()
    prefix = f"[{timestamp}] [{level.upper()}] [jobs.{self.name}]"
    print(f"{prefix} {message}")  # Not configurable, not structured
```

**Impact:** No log levels, no file output, no structured logging for monitoring.

**Recommendation:** Use Python's `logging` module:
```python
import logging

def _log(self, message: str, level: str = "info") -> None:
    logger = logging.getLogger(f"jobs.{self.name}")
    getattr(logger, level)(message)
```

---

### 3.6 AI Validation Can Silently Fail

**Confidence:** 80%
**File:** `jobs/link_checker.py:283-358`

**Issue:** If AI validation fails (API error, parsing error), it defaults to "healthy" with score 1.0, masking broken links.

```python
except Exception as e:
    self._log(f"AI validation failed: {e}", level="warning")
    return {"score": 1.0, "reason": None}  # Optimistic default!
```

**Impact:** Broken links may not be flagged if AI validation fails.

**Recommendation:** Default to requiring human review instead:
```python
return {"score": 0.5, "reason": f"AI validation unavailable: {e}"}
```

---

## 4. LOW PRIORITY ISSUES

### 4.1 Inconsistent Error Handling in Connectors

**Confidence:** 70%
**Files:** Multiple connectors

**Issue:** Some connectors print errors, some raise, some continue silently.

**Impact:** Inconsistent behavior makes debugging harder.

**Recommendation:** Standardize on raising exceptions and letting pipeline handle them.

---

### 4.2 Missing Input Validation in Job Parameters

**Confidence:** 75%
**Files:**
- `jobs/refresh.py:43-58`
- `jobs/discovery.py:102-124`

**Issue:** Jobs accept `**kwargs` but don't validate parameter types or values.

**Impact:** Runtime errors instead of clear parameter validation errors.

**Recommendation:** Add parameter validation at start of `execute()`.

---

### 4.3 Magic Numbers in Configuration

**Confidence:** 80%
**Files:**
- `connectors/va_gov.py:27-28`
- `connectors/careeronestop.py:28-29`
- `jobs/link_checker.py:22-30`

**Issue:** Hardcoded limits and thresholds scattered throughout code.

```python
MAX_PAGES = 50  # Should be configurable
DEFAULT_PAGE_SIZE = 100
HTTP_TIMEOUT = 30.0
AI_HEALTH_THRESHOLD = 0.5
```

**Impact:** Difficult to tune without code changes.

**Recommendation:** Move to configuration system (environment variables or config file).

---

## 5. POSITIVE OBSERVATIONS

1. **Good deduplication logic** - Title similarity matching with configurable thresholds
2. **Comprehensive audit trail** - SourceRecord tracking with hashes
3. **Tiered source reliability** - Trust scoring based on source tier
4. **Change detection** - Field-level change tracking in ChangeLog
5. **Review workflow** - Risky changes flagged for human review
6. **Context managers** - VA and CareerOneStop connectors implement `__enter__`/`__exit__`
7. **Batch processing** - ETL handles large datasets efficiently
8. **Error collection** - Pipeline collects errors without stopping completely

---

## 6. RECOMMENDATIONS SUMMARY

### Immediate Actions (Next Sprint)

1. **Fix HTTP client leaks** - Add proper cleanup in `run()` methods (va_gov.py:71, careeronestop.py:127)
2. **Fix workbook leak** - Use context manager in SSVF connector (ssvf.py:70)
3. **Replace deprecated `datetime.utcnow()`** - Update to `datetime.now(UTC)` (loader.py, pipeline.py)
4. **Add transaction management** - Make ETL pipeline idempotent (loader.py:96)

### Short Term (This Quarter)

5. **Add retry logic** - Implement exponential backoff for API calls
6. **Add database constraints** - Unique constraint on Organization.name
7. **Improve logging** - Replace print() with proper logging module
8. **Validate nested data** - Add defensive checks in connector parsing

### Long Term (Backlog)

9. **Implement geocoding** - Replace stub geocoders with real implementations
10. **Extract configuration** - Move magic numbers to config system
11. **Add parameter validation** - Validate job kwargs
12. **Add monitoring** - Track hash collisions, duplicate rates, API failures

---

## 7. TESTING RECOMMENDATIONS

1. **Add integration tests** for connector retry logic
2. **Test idempotency** - Run ETL jobs twice, verify no duplicates
3. **Test resource cleanup** - Verify connections closed on error paths
4. **Load testing** - Test deduplication with 10k+ resources
5. **Chaos testing** - Simulate API failures, network timeouts

---

## Appendix: Issue Reference Table

| ID | Priority | File:Line | Issue | Confidence |
|----|----------|-----------|-------|------------|
| 1.1 | CRITICAL | va_gov.py:71 | HTTP client leak | 95% |
| 1.2 | CRITICAL | ssvf.py:70 | File handle leak | 90% |
| 2.1 | HIGH | va_gov.py:154 | Missing data validation | 85% |
| 2.2 | HIGH | base.py:89 | Silent phone corruption | 80% |
| 2.3 | HIGH | loader.py:235 | Deprecated datetime usage | 90% |
| 2.4 | HIGH | loader.py:96 | Non-idempotent pipeline | 85% |
| 2.5 | HIGH | loader.py:130 | Race condition in cache | 75% |
| 2.6 | HIGH | va_gov.py:132 | Missing retry logic | 80% |
| 2.7 | HIGH | pipeline.py:86 | No rollback on failure | 85% |
| 2.8 | HIGH | normalize.py:416 | Silent hash collision risk | 75% |
| 3.1 | MEDIUM | dedupe.py:116 | Quadratic deduplication | 70% |
| 3.2 | MEDIUM | normalize.py:298 | Unvalidated state codes | 75% |
| 3.3 | MEDIUM | normalize.py:331 | Missing URL validation | 70% |
| 3.4 | MEDIUM | enrich.py:38 | Stub geocoders | 100% |
| 3.5 | MEDIUM | base.py:176 | Print instead of logging | 85% |
| 3.6 | MEDIUM | link_checker.py:357 | Silent AI failure | 80% |
| 4.1 | LOW | Multiple | Inconsistent errors | 70% |
| 4.2 | LOW | refresh.py:43 | Missing param validation | 75% |
| 4.3 | LOW | Multiple | Magic numbers | 80% |

---

**Review Completed:** 2026-01-21
**Reviewed By:** Claude (Code Review Agent)
**Total Issues:** 19 (2 critical, 8 high, 6 medium, 3 low)
