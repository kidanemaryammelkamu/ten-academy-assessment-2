# Skill: Trend Scraper

Purpose
--
This skill ingests platform-level activity over a configurable time horizon and returns ranked trend objects suitable for storage in Weaviate as content + embeddings. All outward-facing outputs (publication, posting, or external APIs) must follow the project's Safety Gate: content requires `Judge` approval before leaving the system (see specs/_meta.md).

Spec references (traceability)
- [specs/_meta.md](../../specs/_meta.md) — Safety Gate (`Judge`) requirement.
- [specs/technical.md](../../specs/technical.md) — Weaviate usage and API/auth guidance.
- [specs/openclaw.md](../../specs/openclaw.md) — social protocol and presence/handshake guidance for execution orchestration.

JSON Input Contract
--
Accepts `application/json` with the following schema:

{
  "platform": "string",       // e.g. "twitter", "reddit", "github"
  "time_horizon": "string",  // ISO8601 duration (e.g. "P7D") or an ISO8601 interval (e.g. "2026-02-01/2026-02-05")
  "limit": 50,                 // optional integer, max number of trends to return (default 50)
  "filters": {                 // optional platform-specific filters
    "language": "en",
    "region": "us"
  },
  "trace_id": "string"       // optional tracing id for observability
}

Validation rules:
- `platform` must be a non-empty string and one of the supported platforms configured in the service.
- `time_horizon` must be a valid ISO8601 duration or interval.

Example Request
--
{
  "platform": "twitter",
  "time_horizon": "P7D",
  "limit": 25,
  "filters": { "language": "en" },
  "trace_id": "trace-abc-123"
}

JSON Output Contract
--
Responds with `application/json` containing a `trends` array. Each `trend_object` MUST include fields suitable for Weaviate ingestion and downstream judging:

{
  "trends": [
    {
      "trend_id": "uuid",
      "title": "string",
      "summary": "string",
      "example_post": {
        "id": "string",
        "text": "string",
        "url": "string"
      },
      "relevance_score": 0.0,      // float in [0.0, 1.0]
      "sentiment_index": 0.0,      // float in [-1.0, 1.0]
      "embedding": [0.123, ...],   // optional float vector for Weaviate
      "weaviate": {                 // mapping advice for Weaviate ingestion
        "class": "Trend",
        "properties": {
          "title": "string",
          "summary": "string",
          "relevance_score": "number",
          "sentiment_index": "number"
        },
        "meta": { "source_platform": "twitter", "collected_at": "ISO8601" }
      },
      "tags": ["tag1","tag2"]
    }
  ],
  "cursor": "opaque-cursor-or-null",
  "generated_at": "ISO8601"
}

Field definitions and constraints
- `trend_id`: stable UUID for the trend object.
- `relevance_score`: normalized float where 1.0 is most relevant. Used for ranking before Judge review.
- `sentiment_index`: normalized sentiment score where -1.0 is strongly negative, 0 neutral, 1.0 strongly positive. Use a consistent sentiment model across platforms.
- `embedding`: vector of floats matching the dimensionality used for Weaviate (record dimensionality in `weaviate` metadata if needed).
- `weaviate.class`: recommended Weaviate class name for ingestion (implementers can adapt to their schema but must record mapping in traceability notes).

Acceptance criteria
- Output must include `relevance_score` and `sentiment_index` for every `trend_object`.
- Embeddings (if produced) must match the project's Weaviate dimensionality and be included under `embedding` for direct ingestion.
- All outward-facing publication of trends requires `Judge` approval before push to external endpoints per [specs/_meta.md](../../specs/_meta.md).

Operational notes
- Include `trace_id` in all logs and outgoing messages to support observability.
- Persist raw scraped data and computed trend objects in PostgreSQL for auditability, and store dense embeddings in Weaviate as references per [specs/technical.md](../../specs/technical.md).
- Respect platform rate limits and authentication policies.

Example Response
--
{
  "trends": [
    {
      "trend_id": "d4f8c9b2-...",
      "title": "AI-assisted code completion",
      "summary": "Rapid adoption of AI tools for developer productivity.",
      "example_post": { "id": "12345", "text": "Loving the new AI tooling...", "url": "https://..." },
      "relevance_score": 0.92,
      "sentiment_index": 0.15,
      "embedding": [0.001, 0.234, ...],
      "weaviate": { "class": "Trend", "properties": { "title": "AI-assisted code completion", "relevance_score": 0.92, "sentiment_index": 0.15 }, "meta": { "source_platform": "twitter", "collected_at": "2026-02-05T12:00:00Z" } },
      "tags": ["ai","developer"]
    }
  ],
  "cursor": null,
  "generated_at": "2026-02-05T12:01:00Z"
}

Traceability
--
All changes to the skill implementation must reference one or more `specs/` files in commit footers and PR bodies (see repository Prime Directive). Record mapping between code behavior and spec clauses in `TRACE.md` included with the branch.

License & Authors
--
Author: Project Chimera contributors
License: see repository LICENSE
