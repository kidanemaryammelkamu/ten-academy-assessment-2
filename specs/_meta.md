Project Chimera — Specs Index & Meta
--

Project Chimera is an agentic infrastructure for coordinating autonomous agents and services to perform domain workflows at scale. The system implements a Hierarchical Swarm pattern (workers → local leaders → regional coordinators → global orchestrator) described in detail in the Hierarchical Swarm blueprint.

- Blueprint: [specs/hierarchical_swarm.md](specs/hierarchical_swarm.md)

Safety & Publication Workflow
--
All outward-facing outputs (external publication, public APIs, or user-visible messages) are gated by a dedicated `Judge` agent. The `Judge` acts as the final safety gatekeeper and must explicitly approve content before it leaves the system. Approval includes policy checks, provenance validation, and audit logging. No external publication occurs without `Judge` approval.

Governance & Audit
--
- `Judge` maintains immutable audit logs for approvals and rejections.
- CI/CD includes automated schema and contract tests before `Judge` review.
- Escalation: regional coordinators may raise high-risk items to the global orchestrator and human reviewers.

--

- Hierarchical Swarm blueprint: [specs/hierarchical_swarm.md](specs/hierarchical_swarm.md)

