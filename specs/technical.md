# Technical Specifications — DB Schemas & Planner → Worker Pool API

## Mermaid ERD — PostgreSQL schema
```mermaid
erDiagram
    PLANNER {
        UUID planner_id PK
        string name
        timestamptz created_at
    }

    PLAN {
        UUID plan_id PK
        string title
        UUID planner_id FK
        string status
        timestamptz created_at
    }

    TASK {
        UUID task_id PK
        UUID plan_id FK
        string title
        int priority
        jsonb payload
        UUID assigned_worker FK
        string status
        jsonb dependency_ids
        int estimated_cost
        timestamptz created_at
    }

    WORKER {
        UUID worker_id PK
        string name
        string capabilities
        string status
        timestamptz last_heartbeat
    }

    EXECUTION {
        UUID exec_id PK
        UUID task_id FK
        UUID worker_id FK
        timestamptz started_at
        timestamptz finished_at
        jsonb metrics
        bool success
    }

    JUDGMENT {
        UUID judgment_id PK
        UUID exec_id FK
        string verdict
        float score
        jsonb feedback
        timestamptz judged_at
    }

    PLANNER ||--o{ PLAN : owns
    PLAN ||--o{ TASK : contains
    TASK ||--o{ EXECUTION : executed_by
    WORKER ||--o{ EXECUTION : runs
    EXECUTION ||--o{ JUDGMENT : evaluated_by

```

## Mermaid ERD — Weaviate schema (conceptual)
```mermaid
erDiagram
    WEAVIATE_Content {
        UUID id PK
        string title
        text body
        json meta
        vector embedding
    }

    WEAVIATE_Embedding {
        UUID id PK
        UUID content_id FK
        vector values
        json origin
    }

    WEAVIATE_Metadata {
        UUID id PK
        UUID content_id FK
        json properties
    }

    WEAVIATE_Content ||--o{ WEAVIATE_Embedding : has
    WEAVIATE_Content ||--o{ WEAVIATE_Metadata : has
```

Notes:
- PostgreSQL stores plan/task lifecycle, execution details, and judgment records; Weaviate stores dense vectors and searchable content objects referenced by task payloads.

---

## JSON API Contract — Planner → Worker Pool ('Content Request')

- Endpoint: `POST /api/v1/worker-pool/content-requests`
- Auth: `Authorization: Bearer <token>`
- Content-Type: `application/json`
- Idempotency: optional `Idempotency-Key` header supported

Request JSON Schema (application/json):

{
  "planner_id": "uuid",          // origin planner
  "plan_id": "uuid",             // parent plan
  "task": {
    "task_id": "uuid",           // client-generated or server-assigned
    "title": "string",
    "priority": 1,                 // integer (higher = earlier)
    "dependencies": ["uuid"],    // optional
    "deadline": "ISO8601",       // optional
    "payload": {                   // task-specific content request
      "type": "content_generation|fetch|transform",
      "content_spec": { /* domain specific */ },
      "weaviate_refs": [ { "class": "Content", "id": "uuid" } ]
    }
  },
  "meta": {                        // optional routing/observability
    "callback_url": "https://...",
    "trace_id": "string"
  }
}

Minimal validation rules:
- `planner_id`, `plan_id`, and `task.task_id` must be valid UUIDs when present.
- `task.payload.type` must be one of the allowed values.

Success responses:
- 201 Created (synchronous acceptance)

Example 201 body:

{
  "status": "accepted",
  "task_id": "uuid",
  "queue_position": 12,
  "accepted_at": "2026-02-05T12:00:00Z"
}

- 202 Accepted (async processing; task queued)

Example 202 body:

{
  "status": "queued",
  "task_id": "uuid",
  "estimated_start": "2026-02-05T12:05:00Z"
}

Error responses:
- 400 Bad Request — malformed JSON or missing required fields.
- 401 Unauthorized — invalid or missing auth token.
- 409 Conflict — idempotency conflict for same `Idempotency-Key`.
- 422 Unprocessable Entity — schema validation failed (include `errors` list).

Failure example (422):

{
  "status": "error",
  "errors": [ { "field": "task.payload.type", "message": "unknown type" } ]
}

Behavioral contract / lifecycle:
- Upon valid request the Worker Pool returns a task identifier and queue info.
- The Worker Pool will persist the request to PostgreSQL (`TASK`) linking to `PLAN`.
- If the payload references Weaviate objects, the Worker Pool SHOULD dereference or validate references prior to execution and record any missing refs in `TASK.payload` metadata.
- On task completion the Worker Pool POSTs the execution result to the Judge API (separate contract) including `exec_id`, `task_id`, `logs`, and `metrics`.

Idempotency & retries:
- Clients should set `Idempotency-Key` for at-least-once safe retries; Worker Pool must return the same `task_id` for repeated idempotent requests.

Observability & tracing:
- Support `traceparent` or `trace_id` in `meta` for cross-system tracing.

---

Files created:
- See [specs/technical.md](specs/technical.md) for this content.
