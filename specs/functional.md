# Functional User Stories — Hierarchical Swarm Hand-offs

## Story 1 — Planner → Worker Pool
- As a `Planner`, I want to package a plan into discrete, prioritized work units and submit them to the `Worker Pool` so that work can be executed in parallel according to dependencies and priority.

Acceptance criteria:
- The `Planner` produces a set of task objects containing ID, priority, estimated cost, and dependency metadata.
- The `Worker Pool` acknowledges receipt of each task with a persistent task ID and queue position.
- Tasks are queued in priority order and dependencies are respected before execution begins.

Definition of Done:
- All tasks from the plan are accepted by the `Worker Pool` and assigned task IDs.

## Story 2 — Worker Pool → Judge
- As a `Worker Pool` operator, I want to send completed task outputs, logs, and metrics to the `Judge` so that results can be validated and assessed for correctness and quality.

Acceptance criteria:
- Each completed task submission includes output artifacts, execution logs, and standard metrics (duration, resource usage, success flags).
- The `Judge` returns a structured evaluation (pass/fail, score, and feedback) within a bounded time.
- On a `fail` verdict, the `Worker Pool` records the feedback and flags the task for retry, escalation, or remediation according to policy.

Definition of Done:
- Every completed task submitted to the `Judge` receives a verdict and accompanying feedback recorded in the task history.

## Story 3 — Judge → Planner
- As a `Judge`, I want to return structured evaluations and actionable decisions to the `Planner` so that the plan can be updated, retried, or aborted based on objective results.

Acceptance criteria:
- The `Judge` provides a verdict (accept, request-refinement, reject) with reason codes and suggested next steps.
- The `Planner` ingests verdicts and either marks work as complete, schedules fixes, or replans affected work units.
- All communications include traceable references to original task IDs and relevant logs for auditability.

Definition of Done:
- The `Planner` has updated the plan state for each judged task according to the `Judge` decision, with an auditable record of the change.
