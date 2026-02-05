# OpenClaw Integration Plan — Chimera Availability Broadcast

## Overview
This document describes how the `Chimera` agent broadcasts its `Availability` to other agents using the social protocols from the MoltBook research. The goal is a lightweight, auditable, and secure presence and capability announcement mechanism that supports discovery, load balancing, and graceful hand-offs.

## Goals
- Allow agents to discover available Chimera instances and capabilities.
- Provide truthy availability state (available, busy, draining, offline).
- Ensure low-latency updates and scalable fan-out.
- Preserve auditability and traceability for decisions.

## Assumptions
- MoltBook social protocols provide patterns for Presence Posts, Capability Declarations, and Signed Handshakes.
- A messaging substrate exists (pub/sub or broker) supporting topics and optional direct webhooks.
- Agents authenticate via bearer tokens and sign critical messages.

## Availability Model (states)
- available: accepting new tasks
- busy: currently at capacity but still processing queued work
- draining: finishing in-flight work; not accepting new tasks
- offline: unreachable or intentionally stopped

Each availability message includes capacity and a short TTL.

## Message Channels & Social Protocols
- Discovery Topic (MoltBook Presence Post): `moltbook.presence.openswarm`
  - Periodic presence posts (heartbeat cadence) advertise short-lived availability.
  - Subscribers: Planner, Worker Pool directory, other agents.

- Capability Topic (MoltBook Capability Declaration): `moltbook.capability.chimera`
  - Sent when capabilities change (models enabled, plugins, special tools).

- Direct Handshake (Signed Handshake / Offer-Request): per-session via `callback_url` or broker queue
  - Planner can perform a direct handshake to confirm assignment and reserve capacity.

Social protocol rules (from MoltBook):
- Posts are declarative and idempotent; consumer logic decides actions.
- Announcements are short-lived; explicit revocation or TTL expiry removes them.
- Agents should prefer eventual-consistent state built from multiple posts, not single messages.

## Availability Message Schema (JSON)

{
  "agent_id": "uuid",
  "instance_id": "uuid",
  "state": "available|busy|draining|offline",
  "capabilities": ["capabilityA","capabilityB"],
  "capacity": { "slots_total": 8, "slots_free": 3 },
  "load": { "cpu": 0.12, "mem": 0.48 },
  "expires_at": "ISO8601",    
  "trace_id": "string",
  "signed_at": "ISO8601",
  "signature": "base64(sig(agent_key, message_payload))"
}

Notes:
- `expires_at` enforces TTL; listeners ignore stale posts.
- `signature` allows recipients to verify authenticity.

## Broadcast Cadence & Backoff
- Heartbeat (presence) cadence default: 10s.
- On network issues, use exponential backoff up to 5 minutes.
- On state `draining` send an immediate capability update and reduce cadence to 30s.

## Discovery & Consumption Patterns
- Planners and directories subscribe to `moltbook.presence.openswarm`.
- Consumers maintain a small in-memory cache keyed by `instance_id` with last-seen timestamp and signature verification result.
- Decision logic should weight `slots_free`, `capabilities` match, and recent `load` metrics.

## Handshake Flow (Reserve slot)
1. Planner decides to assign work and posts a `reserve_offer` to Chimera's `callback_url` or to a per-instance queue.
2. Chimera verifies the digital signature and responds with `reserve_ack` (accept/reject) within configured SLA (e.g., 3s).
3. On `accept`, Planner transitions task to `assigned`; on `reject`, Planner chooses alternate instance.

Reserve message (offer):
{
  "planner_id": "uuid",
  "task_id": "uuid",
  "requested_slots": 1,
  "deadline": "ISO8601",
  "signature": "..."
}

Ack (accept):
{
  "instance_id": "uuid",
  "task_id": "uuid",
  "accepted": true,
  "reservation_id": "uuid",
  "expires_at": "ISO8601",
  "signature": "..."
}

## Security & Auditability
- All posts and handshakes are signed (public-key) and include `trace_id` for correlation.
- Use short-lived tokens for topic publishing; rotate keys regularly.
- Persist presence events in an append-only audit store (PostgreSQL `PRESENCE_EVENTS`) for retrospective analysis.

## Failure Modes & Recovery
- Missed heartbeats: consumer marks instance `offline` after 3 missed cadences.
- Reconciliation: directory periodically (e.g., every 5m) validates cached instances via a direct status probe.
- Draining instances reject new reservations; Planner must honor graceful handoff.

## Implementation Steps
1. Implement presence poster in `Chimera` to emit signed JSON to `moltbook.presence.openswarm` every 10s.
2. Implement capability poster to emit changes on capability updates.
3. Add subscription client in Planner and Worker Pool to ingest presence and update local directory.
4. Implement direct handshake endpoint in Chimera to accept `reserve_offer` and return `reserve_ack`.
5. Add persistence of presence events to `PRESENCE_EVENTS` table for audit.
6. Add tests: signing verification, TTL expiry, reserve handshake success/failure.

## Acceptance Criteria
- Planners can discover at least one `available` Chimera instance with matching capabilities within 15s of instance startup.
- Reserve handshake succeeds within 3s for healthy instances and returns signed ack.
- Presence events are stored in the audit table and can be queried for the last 24 hours.

---

See [specs/technical.md](specs/technical.md) for database and API contracts referenced by this plan.
