"""P1--P4 application core for the frozen PaperSpine dual-facade contract.

P3 extends the original ``OpenTask`` slice only far enough to persist task
    resume, human decisions, and the public paper-delivery lifecycle.  Transport facades translate
trusted host context into the same commands, while this module owns
idempotency, optimistic concurrency, legacy compatibility, domain events,
and rebuildable task/decision projections.
"""

from __future__ import annotations

import hashlib
import io
import json
import sqlite3
from contextlib import closing, contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Mapping
from urllib.parse import quote
from uuid import uuid4

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from .p6_recovery import WorkFailure, command_lock
from .filesystem_paths import native_path

from .product_kernel import (
    ContractError,
    IdempotencyConflictError,
    ProductKernel,
    TaskNotFoundError,
)
from .skill_bridge import (_figure_candidates, configuration_readiness,
                           configuration_with_defaults, export_workflow_files)
from .review_projection import project_review_record, review_event_metadata


P0_SCHEMA_VERSION = "1.0"

# Public option IDs already used by figure decisions. Arbitrary candidate IDs
# need an explicit action; labels, filenames and attached bytes are not intent.
_FIGURE_OPTION_ACTIONS = {"keep": "keep", "adopt": "adopt", "revise": "revise",
                          "modify": "revise", "request-changes": "revise",
                          "request_changes": "revise", "reject": "reject"}


def _figure_option_action(option: Mapping[str, Any]) -> str | None:
    known = _FIGURE_OPTION_ACTIONS.get(option.get("option_id"))
    action = option.get("action")
    if known and action and action != known:
        return None
    return action or known


def _delivery_inputs(current: Mapping[str, Any], required_formats: list[str],
                     unavailable_artifact_ids: set[str] | None = None) -> dict[str, Any]:
    """One current-output and exact review selection for preflight/PrepareDelivery."""
    artifacts = [item for item in current.get('artifacts', []) if not item.get('stale')]
    by_id = {item['artifact_id']: item for item in artifacts}
    unavailable = unavailable_artifact_ids or set()
    reviewed = set()
    for review in current.get('reviews', []):
        if review.get('stale'):
            continue
        report_id = review.get('report_artifact_id')
        if report_id and (report_id in unavailable or report_id not in by_id
                          or by_id[report_id]['sha256'] != review.get('report_sha256')):
            continue
        for artifact_id in review.get('reviewed_artifact_ids', []):
            if artifact_id not in unavailable and artifact_id not in review.get('stale_artifact_ids', []):
                reviewed.add((artifact_id, review.get('reviewed_hashes', {}).get(artifact_id)))
    outputs = [item for item in artifacts
               if item['artifact_type'] in {'pdf', 'docx', 'tex', 'figure', 'bibliography'}]
    aliases = {'word': 'docx', 'figures': 'figure'}
    present = {item['artifact_type'] for item in artifacts}
    required = []
    for fmt in required_formats:
        kind = aliases.get(fmt, fmt)
        candidates = [item for item in artifacts if item['artifact_type'] == kind]
        # Publication already retires old versions within each document_id
        # (omission means main). Keep every current document, never infer by name
        # or collapse separate artifact identities merely because bytes match.
        known_ids = {item['artifact_id'] for item in required}
        required.extend(item for item in candidates if item['artifact_id'] not in known_ids)
    return {'artifacts': artifacts, 'outputs': outputs, 'required': required,
            'unreviewed': [item for item in outputs if (item['artifact_id'], item['sha256']) not in reviewed],
            'missing_formats': [fmt for fmt in required_formats if aliases.get(fmt, fmt) not in present]}


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class DomainError(Exception):
    """Shared P0 domain error, usable by either transport facade."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        category: str,
        task_id: str | None = None,
        command_id: str | None = None,
        current_version: int | None = None,
        details: Mapping[str, Any] | None = None,
        retryable: bool = False,
        trace_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.value = {
            "contract": "paperspine.domain-error",
            "schema_version": P0_SCHEMA_VERSION,
            "code": code,
            "message": message,
            "category": category,
            "retryable": retryable,
            "task_id": task_id,
            "command_id": command_id,
            "current_version": current_version,
            "details": dict(details or {}),
            "trace_id": trace_id,
        }
        self.value["details"].setdefault("next_action", "retry" if retryable else "check_request")

    def to_dict(self) -> dict[str, Any]:
        return dict(self.value)


class DomainEventStore:
    """Persistent P1 command/event authority with rebuildable projections."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path).resolve()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._transaction() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS domain_commands (
                    command_id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    command_json TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS domain_events (
                    event_id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    task_version INTEGER NOT NULL,
                    event_json TEXT NOT NULL,
                    UNIQUE(task_id, sequence),
                    UNIQUE(task_id, task_version)
                );
                CREATE TABLE IF NOT EXISTS task_projections (
                    task_id TEXT PRIMARY KEY,
                    task_version INTEGER NOT NULL,
                    projection_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS operation_intents (
                    command_id TEXT PRIMARY KEY,
                    command_json TEXT NOT NULL,
                    state_json TEXT NOT NULL
                );
                """
            )

    @contextmanager
    def _transaction(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        try:
            connection.execute("BEGIN IMMEDIATE")
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def command(self, command_id: str) -> dict[str, Any] | None:
        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                "SELECT task_id, command_json, result_json FROM domain_commands WHERE command_id=?",
                (command_id,),
            ).fetchone()
        if row is None:
            return None
        return {
            "task_id": row["task_id"],
            "command_json": row["command_json"],
            "result": json.loads(row["result_json"]),
        }

    def append(
        self, command: Mapping[str, Any], event: Mapping[str, Any], result: Mapping[str, Any],
        *, operation: tuple[str, dict[str, Any]] | None = None,
    ) -> bool:
        command_json = _canonical(command)
        result_json = _canonical(result)
        event_json = _canonical(event)
        with self._transaction() as connection:
            prior = connection.execute(
                "SELECT command_json FROM domain_commands WHERE command_id=?",
                (command["command_id"],),
            ).fetchone()
            if prior is not None:
                if prior["command_json"] != command_json:
                    raise IdempotencyConflictError("domain command_id was reused with different inputs")
                return False
            row = connection.execute(
                "SELECT task_version, projection_json FROM task_projections WHERE task_id=?",
                (command["task_id"],),
            ).fetchone()
            current_version = 0 if row is None else int(row["task_version"])
            if event["task_version"] - 1 != current_version:
                raise sqlite3.IntegrityError(f"version_conflict:{current_version}")
            current_projection = None if row is None else json.loads(row["projection_json"])
            projection = _apply_event(current_projection, event)
            connection.execute(
                "INSERT INTO domain_events VALUES(?,?,?,?,?)",
                (
                    event["event_id"], event["task_id"], event["sequence"],
                    event["task_version"], event_json,
                ),
            )
            connection.execute(
                "INSERT OR REPLACE INTO task_projections VALUES(?,?,?)",
                (event["task_id"], event["task_version"], _canonical(projection)),
            )
            connection.execute(
                "INSERT INTO domain_commands VALUES(?,?,?,?,?)",
                (command["command_id"], command["task_id"], command_json, result_json, _now()),
            )
            if operation is not None:
                connection.execute("UPDATE operation_intents SET state_json=? WHERE command_id=?",
                                   (_canonical(operation[1]), operation[0]))
            else:
                connection.execute("DELETE FROM operation_intents WHERE command_id=?", (command["command_id"],))
        return True

    def intent(self, command_id: str) -> dict[str, Any] | None:
        with closing(sqlite3.connect(self.database_path)) as connection:
            row = connection.execute("SELECT command_json,state_json FROM operation_intents WHERE command_id=?",
                                     (command_id,)).fetchone()
        return None if row is None else {"command": json.loads(row[0]), "state": json.loads(row[1])}

    def set_intent(self, command: Mapping[str, Any], state: dict[str, Any]) -> None:
        with self._transaction() as connection:
            connection.execute("INSERT OR REPLACE INTO operation_intents VALUES(?,?,?)",
                               (command["command_id"], _canonical(command), _canonical(state)))

    def intents(self) -> list[dict[str, Any]]:
        with closing(sqlite3.connect(self.database_path)) as connection:
            rows = connection.execute("SELECT command_json,state_json FROM operation_intents").fetchall()
        return [{"command": json.loads(row[0]), "state": json.loads(row[1])} for row in rows]

    # Compatibility anchor retained for P1 callers/tests.
    def append_opened(
        self, command: Mapping[str, Any], event: Mapping[str, Any], result: Mapping[str, Any]
    ) -> None:
        self.append(command, event, result)

    def events(self, task_id: str) -> list[dict[str, Any]]:
        with closing(sqlite3.connect(self.database_path)) as connection:
            rows = connection.execute(
                "SELECT event_json FROM domain_events WHERE task_id=? ORDER BY sequence",
                (task_id,),
            ).fetchall()
        return [json.loads(row[0]) for row in rows]

    def projection(self, task_id: str) -> dict[str, Any] | None:
        with closing(sqlite3.connect(self.database_path)) as connection:
            row = connection.execute(
                "SELECT projection_json FROM task_projections WHERE task_id=?", (task_id,)
            ).fetchone()
        return None if row is None else json.loads(row[0])

    def clear_projections(self) -> None:
        with self._transaction() as connection:
            connection.execute("DELETE FROM task_projections")

    def rebuild_projections(self) -> dict[str, dict[str, Any]]:
        rebuilt: dict[str, dict[str, Any]] = {}
        with self._transaction() as connection:
            connection.execute("DELETE FROM task_projections")
            rows = connection.execute(
                "SELECT event_json FROM domain_events ORDER BY task_id, sequence"
            ).fetchall()
            for row in rows:
                event = json.loads(row["event_json"])
                task_id = event["task_id"]
                rebuilt[task_id] = _apply_event(rebuilt.get(task_id), event)
            for task_id, projection in rebuilt.items():
                connection.execute(
                    "INSERT INTO task_projections VALUES(?,?,?)",
                    (task_id, projection["task_version"], _canonical(projection)),
                )
        return rebuilt


def _matching_findings(findings: list[dict[str, Any]], payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    review_id = payload.get("review_id")
    return [item for item in findings if item["finding_id"] == payload["finding_id"]
            and (review_id is None or item["review_id"] == review_id)]


def _finding_to_resolve(current: Mapping[str, Any], payload: Mapping[str, Any]) -> dict[str, Any]:
    matches = _matching_findings(current.get("findings", []), payload)
    if not matches:
        raise DomainError("not_found", "The review finding does not exist.", category="missing")
    open_matches = [item for item in matches if item.get("status") == "open"]
    if not open_matches:
        raise DomainError("idempotency_conflict", "The review finding is already resolved.", category="conflict")
    if len(open_matches) > 1 and "review_id" not in payload:
        raise DomainError("validation_failed", "Multiple open findings share this ID. Specify review_id.",
                          category="validation", details={"finding_id": payload["finding_id"],
                          "review_ids": sorted({item["review_id"] for item in open_matches}),
                          "next_action": "specify_review_id"})
    return open_matches[0]


def _apply_event(
    projection: Mapping[str, Any] | None, event: Mapping[str, Any]
) -> dict[str, Any]:
    event_type = event["event_type"]
    if event_type == "task.failed":
        updated = dict(projection or {"task_id": event["task_id"], "status": "open", "stage": "intake",
                                     "decisions": [], "materials": [], "milestones": [], "evidence_links": [],
                                     "artifacts": [], "reviews": [], "findings": [], "delivery": None})
        updated["task_version"] = event["task_version"]
        updated["recovery"] = dict(event["payload"])
        return updated
    if projection is not None and (projection.get("recovery") or {}).get("operation_id") == event["command_id"]:
        projection = dict(projection)
        projection.pop("recovery", None)
    if event_type == "task.opened":
        if projection is None or not projection.get("opened_mode"):
            return {
                "task_id": event["task_id"], "task_version": event["task_version"],
                "status": "open", "stage": "intake",
                "opened_mode": event["payload"]["mode"], "decisions": [],
                "materials": [], "milestones": [], "evidence_links": [],
                "artifacts": [], "reviews": [], "findings": [],
                "delivery": None,
            }
        if event["payload"]["mode"] != "resume":
            raise ValueError("an existing task may only be opened in resume mode")
        updated = dict(projection)
        updated.update(task_version=event["task_version"], opened_mode="resume")
        return updated
    if projection is None:
        raise ValueError(f"{event_type} requires an opened task")
    updated = dict(projection)
    updated["task_version"] = event["task_version"]
    decisions = [dict(item) for item in projection.get("decisions", [])]
    payload = event["payload"]
    if event_type == "decision.required":
        if any(item["decision_id"] == payload["decision_id"] for item in decisions):
            raise ValueError("decision_id already exists")
        decisions.append({
            "decision_id": payload["decision_id"],
            "decision_type": payload["decision_type"],
            "prompt": payload.get("prompt", payload["decision_type"]),
            "status": "pending",
            "allowed_decisions": list(payload["allowed_decisions"]),
            "allowed_decision_details": list(payload.get("allowed_decision_details", [
                {"option_id": value, "label": value} for value in payload["allowed_decisions"]
            ])),
            **({"figure": dict(payload["figure"])} if "figure" in payload else {}),
            "scope_refs": list(payload["scope_refs"]),
            "requested_by_command_id": payload["requested_by_command_id"],
            "expires_at": payload["expires_at"],
        })
        kind = payload['decision_type'].lower()
        if 'figure' in kind:
            updated['stage'] = 'figure'
        elif 'contribution' in kind or 'motivation' in kind:
            updated['stage'] = 'contribution'
        updated["status"] = "awaiting_decision"
    elif event_type == "decision.resolved":
        match = next((item for item in decisions if item["decision_id"] == payload["decision_id"]), None)
        if match is None:
            raise ValueError("decision does not exist")
        match.update(status="resolved", option_id=payload["option_id"], confirmed_at=payload["confirmed_at"],
                     reason=payload.get("reason", ""))
        updated["status"] = "open" if not any(
            item["status"] == "pending" and not item.get("stale") for item in decisions
        ) else "awaiting_decision"
    elif event_type == "materials.authorized":
        updated["materials"] = [{"grant_id": value} for value in payload["grant_ids"]]
        updated["material_snapshot_sha256"] = payload["snapshot_sha256"]
        if event["schema_version"] == "1.1":
            updated["material_grants"] = payload["grants"]
            updated["material_inventory"] = payload["inventory"]
            if projection.get("material_snapshot_sha256") != payload["snapshot_sha256"]:
                _stale_inputs(updated, "materials_changed", event["task_version"])
                decisions = updated["decisions"]
        else:
            updated["stage"] = "intake"
    elif event_type == "configuration.saved":
        updated["configuration"] = configuration_with_defaults(payload["configuration"])
        updated["run_contract"] = payload["run_contract"]
        if payload.get("inventory") is not None:
            updated["material_inventory"] = payload["inventory"]
        if payload.get("material_grants") is not None:
            updated["material_grants"] = payload["material_grants"]
        updated["configuration_stale"] = False
        actor = event.get("actor") or {}
        # The durable event envelope intentionally keeps only actor_id and
        # surface. `business` is the trusted Web facade; `agent` is a host
        # proposal and can never self-assert user confirmation here.
        if actor.get("surface") == "business":
            updated["configuration_source"] = "web_user"
        elif actor.get("surface") == "agent":
            updated["configuration_source"] = "agent_proposal"
        else:
            updated["configuration_source"] = "legacy_unknown"
        updated["configuration_user_confirmed"] = updated["configuration_source"] == "web_user"
        previous_configuration = projection.get("configuration")
        if (configuration_with_defaults(previous_configuration) if previous_configuration is not None else None) != updated["configuration"]:
            _stale_inputs(updated, "configuration_changed", event["task_version"])
            decisions = updated["decisions"]
    elif event_type == "revision.requested":
        updated["revision_request"] = {
            "feedback": payload["feedback"], "scope": payload["scope"],
            "requested_revision": payload["requested_revision"],
            "previous_completed_revision": payload["previous_completed_revision"],
            "feedback_file": payload.get("feedback_file"),
            "command_id": event["command_id"],
        }
        updated['revision_requests'] = [*projection.get('revision_requests', []), dict(updated['revision_request'])]
        scope = payload['scope']
        affected = _review_scope_ids(projection, 'figure' if scope in {'figures', 'figure_mapping'} else 'draft')
        if scope == 'all':
            affected = {item['artifact_id'] for item in projection.get('artifacts', [])}
        _invalidate_reviews(updated, affected, 'revision_requested', event['task_version'])
        _invalidate_delivery(updated, 'revision_requested')
        updated["stage"] = "figure" if scope in {'figures', 'figure_mapping'} else "draft"
        updated["status"] = "in_progress"
    elif event_type == "milestone.committed":
        milestones = [dict(item) for item in projection.get("milestones", [])]
        milestones.append({
            "milestone_id": payload["milestone_id"], "stage": payload["stage"],
            "artifact_ids": list(payload["artifact_ids"]), "summary": payload.get("summary", ""),
        })
        updated["milestones"] = milestones
        updated["stage"] = payload["stage"]
        updated["status"] = "in_progress"
        if payload['stage'] not in {'review', 'delivery'}:
            affected = _review_scope_ids(projection, payload['stage']) | set(payload['artifact_ids'])
            _invalidate_reviews(updated, affected, 'milestone_committed', event['task_version'])
            _invalidate_delivery(updated, 'milestone_committed')
    elif event_type == "evidence.bound":
        links = [dict(item) for item in projection.get("evidence_links", [])]
        links.append({key: payload[key] for key in ("claim_id", "evidence_id", "relation")})
        updated["evidence_links"] = links
        updated["stage"] = "evidence"
    elif event_type == "artifact.published":
        artifacts = [dict(item) for item in projection.get("artifacts", [])]
        previous = next((item for item in artifacts if item['artifact_id'] == payload['artifact_id']), None)
        supersedes = set(payload.get('supersedes_artifact_ids', []))
        changed = previous is None or previous.get('stale') or (
            previous.get('document_id', 'main') != payload.get('document_id', 'main')) or any(
            previous.get(key) != payload[key] for key in ('sha256', 'artifact_type')) or any(
                item['artifact_id'] in supersedes and not item.get('stale') for item in artifacts)
        affected = set()
        if changed:
            # New events persist inherited identity; old events without document_id
            # retain legacy main-document behavior. Never reinterpret history by name.
            # Figure and package IDs identify distinct panels or archive variants.
            single_formats = {'pdf', 'docx', 'tex', 'manuscript_source', 'bibliography'}
            for item in artifacts:
                if item['artifact_id'] == payload['artifact_id'] or item['artifact_id'] in supersedes or (
                        payload['artifact_type'] in single_formats and item['artifact_type'] == payload['artifact_type']
                        and item.get('document_id', 'main') == payload.get('document_id', 'main')):
                    affected.add(item['artifact_id'])
                    item.update(stale=True, stale_reason='artifact_superseded',
                                stale_since_version=event['task_version'], superseded_by=payload['artifact_id'])
                elif item['artifact_type'] == 'delivery_package' and payload['artifact_type'] in single_formats | {'figure'}:
                    affected.add(item['artifact_id'])
                    item.update(stale=True, stale_reason='packaged_outputs_changed', stale_since_version=event['task_version'])
            if payload['artifact_type'] in {'manuscript_source', 'figure', 'bibliography'}:
                if payload['artifact_type'] == 'figure':
                    affected |= {item['artifact_id'] for item in artifacts
                                 if item['artifact_type'] in {'pdf', 'docx', 'tex'} and not item.get('stale')}
                else:
                    affected |= _review_scope_ids(projection, 'draft')
        artifacts = [item for item in artifacts if item["artifact_id"] != payload["artifact_id"]]
        artifacts.append({key: payload[key] for key in
                          ("artifact_id", "artifact_type", "sha256", "media_type")})
        artifacts[-1]["stage"] = payload.get("stage", projection.get("stage", "intake"))
        if payload.get("document_id"):
            artifacts[-1]["document_id"] = payload["document_id"]
        if payload.get("package_scope"):
            artifacts[-1]["package_scope"] = payload["package_scope"]
        artifacts[-1]['producer_id'] = event['actor']['actor_id']
        replaced = set((previous or {}).get('supersedes_artifact_ids', [])) | supersedes
        if replaced:
            artifacts[-1]['supersedes_artifact_ids'] = sorted(replaced)
        updated["artifacts"] = artifacts
        if changed:
            _invalidate_reviews(updated, affected, 'artifact_published', event['task_version'])
            _invalidate_delivery(updated, 'artifact_published')
    elif event_type == "review.submitted":
        reviews = [dict(item) for item in projection.get("reviews", [])]
        review = project_review_record(event, projection.get("artifacts", []))
        reviews.append(review)
        updated["reviews"] = reviews
        findings = [dict(item) for item in projection.get("findings", [])]
        findings.extend({**item, "review_id": payload["review_id"], "status": "open"}
                        for item in payload.get("findings", []))
        updated["findings"] = findings
        updated["stage"] = "review"
        updated["status"] = "review_blocked" if any(
            item.get("severity") in {"blocking", "major"} for item in findings if item.get("status") == "open"
        ) else "in_progress"
        if updated["status"] == "review_blocked":
            _invalidate_delivery(updated, 'review_findings_open')
    elif event_type == "finding.resolved":
        findings = [dict(item) for item in projection.get("findings", [])]
        matches = _matching_findings(findings, payload)
        if not matches:
            raise ValueError("finding does not exist")
        # Unscoped historical events include hotfix writes. Preserve that
        # writer's first-open rule in submission order and its closed fallback.
        match = next((item for item in matches if item.get("status") == "open"), matches[0])
        match.update(status="resolved", resolution_artifact_ids=list(payload["resolution_artifact_ids"]),
                     explanation=payload.get("explanation"), revision_id=payload.get("revision_id"))
        updated["findings"] = findings
        updated["status"] = "in_progress" if not any(
            item.get("status") == "open" and item.get("severity") in {"blocking", "major"} for item in findings
        ) else "review_blocked"
    elif event_type == "delivery.ready":
        updated["stage"] = "delivery"
        updated["status"] = "delivery_ready"
        updated["delivery"] = {
            "package_artifact_id": payload["package_artifact_id"],
            "local_download_ready": True,
            "submission_ready": payload["submission_ready"], "task_version": event["task_version"],
        }
    else:
        raise ValueError(f"unsupported P4 event: {event_type}")
    updated["decisions"] = decisions
    return updated


def _review_scope_ids(projection: Mapping[str, Any], stage: str) -> set[str]:
    """Invalidate review coverage, without ordering scientific work to rerun."""
    kinds = {'manuscript_source', 'pdf', 'docx', 'tex', 'bibliography'}
    if stage == 'figure':
        kinds = {'figure', 'pdf', 'docx', 'tex'}
    elif stage not in {'draft', 'review', 'delivery'}:
        kinds |= {'figure', 'research_note', 'evidence_graph'}
    return {item['artifact_id'] for item in projection.get('artifacts', [])
            if item['artifact_type'] in kinds and not item.get('stale')}


def _invalidate_reviews(projection: dict[str, Any], affected: set[str], reason: str, version: int) -> None:
    reviews = []
    for original in projection.get('reviews', []):
        review = dict(original)
        covered = set(review.get('reviewed_artifact_ids', []))
        if review.get('report_artifact_id') in affected:
            review.update(stale=True, stale_reason='review_report_changed', stale_since_version=version)
        if covered & affected:
            stale = set(review.get('stale_artifact_ids', [])) | (covered & affected)
            review.update(stale_artifact_ids=sorted(stale), stale_reason=reason, stale_since_version=version)
            if covered <= stale:
                review['stale'] = True
        reviews.append(review)
    projection['reviews'] = reviews


def _invalidate_delivery(projection: dict[str, Any], reason: str) -> None:
    delivery = projection.get('delivery')
    if delivery and not delivery.get('stale'):
        projection['delivery_history'] = [*projection.get('delivery_history', []), dict(delivery)]
        projection['delivery'] = {**delivery, 'local_download_ready': False, 'stale': True, 'stale_reason': reason}
        if projection.get('status') == 'delivery_ready':
            projection['status'] = 'in_progress'


def _stale_inputs(projection: dict[str, Any], reason: str, version: int) -> None:
    """Keep user work; input changes invalidate its claims of current readiness."""
    for key in ("artifacts", "evidence_links", "milestones", "reviews", "decisions"):
        projection[key] = [{**item, "stale": True, "stale_reason": reason,
                            "stale_since_version": version} for item in projection.get(key, [])]
    # Material availability changes do not revoke the user's saved research scope.
    if projection.get("delivery"):
        projection["delivery"] = {**projection["delivery"], "local_download_ready": False,
                                  "stale": True, "stale_reason": reason}
        if projection.get("status") == "delivery_ready":
            projection["status"] = "in_progress"


class LegacyStageAdapter:
    """Hide ProductKernel/Runner/J-stage compatibility behind one P1 boundary."""

    def __init__(self, kernel: ProductKernel, runner: Any | None = None) -> None:
        self._kernel = kernel
        self._runner = runner

    def open_task(self, command: Mapping[str, Any]) -> dict[str, Any]:
        payload = command["payload"]
        if payload["mode"] == "resume":
            return self._kernel.get_task(command["task_id"])
        return self._kernel.create_task(
            command_id=f"p1:{command['command_id']}",
            title=payload.get("title"),
            description=payload.get("description"),
            task_id=payload.get("requested_task_id") or command["task_id"],
            host="codex" if command["actor"]["surface"] == "agent" else "standalone-skill",
        )

    def verify_task_for_decision(self, command: Mapping[str, Any]) -> dict[str, Any]:
        """Keep P3 decision writes behind the compatibility boundary.

        P3 records only the frozen public decision lifecycle.  Translating a
        decision into legacy J-stage academic work belongs to P4.
        """
        return self._kernel.get_task(command["task_id"])

    def apply_public_command(self, command: Mapping[str, Any]) -> dict[str, Any]:
        """Record host work; only material and artifact file effects touch Kernel."""
        task = self._kernel.get_task(command['task_id'])
        if command['command_type'] == 'AuthorizeMaterials':
            from .host_material_files import HostMaterialFiles
            files = getattr(self._kernel, '_p1_material_files', None)
            if files is None:
                files = HostMaterialFiles(self._kernel)
                self._kernel._p1_material_files = files
            return files.authorize(command)
        if command['command_type'] == 'PublishArtifact':
            self.artifact_path(command['task_id'], command['payload']['artifact_id'],
                               expected_sha256=command['payload']['sha256'])
        return task

    def merged_configuration(self, task_id: str, patch: Mapping[str, Any],
                             current: Mapping[str, Any] | None = None) -> dict[str, Any]:
        inputs = self.task_inputs(task_id)
        inherited = dict((inputs.get('run_contract_payload') or {}).get('configuration', {}))
        if 'deliverables' in inherited:
            inherited['formats'] = [{'word': 'docx', 'latex': 'tex'}.get(fmt, fmt)
                                    for fmt in inherited.pop('deliverables')]
        configuration = dict(current if current is not None else inherited)
        for key, value in patch.items():
            if key in {'network_policy', 'privacy', 'budget', 'literature'} and isinstance(value, dict):
                configuration[key] = {**configuration.get(key, {}), **value}
            else:
                configuration[key] = value
        return configuration_with_defaults(configuration)

    def task_inputs(self, task_id: str) -> dict[str, Any]:
        task = self._kernel.get_task(task_id)
        inputs = {'material_grants': task['material_grants'], 'run_contract': {},
                  'run_contract_payload': None, 'material_inventory_payload': None}
        if self._runner is not None:
            try:
                inputs.update(self._runner.task_inputs(task_id))
            except (AttributeError, ContractError, OSError, KeyError, TypeError):
                pass
        inventory = task['state'].get('host_material_inventory')
        if inventory is not None:
            inputs['material_inventory_payload'] = inventory
        for name in ('run_contract', 'material_inventory'):
            pointer = (task['state'].get('runner') or {}).get(name)
            if not inputs.get(name + '_payload') and pointer:
                try:
                    inputs[name + '_payload'] = self.legacy_document(task_id, pointer)
                    inputs[name] = pointer
                except (OSError, ContractError, KeyError, TypeError, ValueError):
                    pass
        if not inputs.get('run_contract_payload') and task['state'].get('configuration'):
            inputs['run_contract_payload'] = {'configuration': task['state']['configuration']}
        return inputs

    def material_snapshot_sha256(self, task_id: str) -> str | None:
        return (self.task_inputs(task_id).get('material_inventory_payload') or {}).get('snapshot_sha256')

    def artifact_path(self, task_id: str, artifact_id: str, *, expected_sha256: str | None = None,
                      allow_historical: bool = False) -> Path:
        matches = [view for view in self._kernel.list_artifacts(task_id)
                   if (view["freshness"] == "fresh" or allow_historical)
                   and view["receipt"].get("artifact_id") == artifact_id
                   and (expected_sha256 is None or view["receipt"].get("sha256") == expected_sha256)]
        if not matches:
            raise TaskNotFoundError(f"fresh artifact does not exist: {artifact_id}")
        receipt = matches[0]["receipt"]
        path = Path(receipt["path"]).resolve()
        body = native_path(path).read_bytes()
        if hashlib.sha256(body).hexdigest() != receipt["sha256"] or len(body) != receipt["size_bytes"]:
            raise ContractError("registered artifact bytes changed")
        return path

    def legacy_document(self, task_id: str, pointer: Mapping[str, Any]) -> dict[str, Any]:
        """Read an exact retained descriptor inside this task, independent of Runner gates."""
        from .p7_artifact_import import read_source
        task = self._kernel.get_task(task_id)
        body, _ = read_source(self._kernel, task_id, None,
                             f"runs/{task['active_run_id']}/{pointer['path']}")
        if hashlib.sha256(body).hexdigest() != pointer['sha256'] or len(body) != pointer['size_bytes']:
            raise ContractError('retained descriptor bytes changed')
        value = json.loads(body)
        if not isinstance(value, dict):
            raise ContractError('retained descriptor must be an object')
        return value

    def historical_outputs(self, task_id: str) -> list[dict[str, Any]]:
        task = self._kernel.get_task(task_id)
        pointers = (task['state'].get('runner') or {}).get('academic_base_artifacts') or {}
        result = []
        for name, kind in (('manuscript_pdf', 'pdf'), ('manuscript_word', 'docx'),
                           ('manuscript_source', 'manuscript_source'), ('bundle_archive', 'delivery_package')):
            pointer = pointers.get(name)
            if not pointer:
                continue
            try:
                doc = self.legacy_document(task_id, pointer)
                if doc.get('contract') not in {'paperspine5.local-file-byte-evidence', 'paperspine5.local-package-archive'}:
                    continue
                relative = f"runs/{task['active_run_id']}/{doc['path']}"
                from .p7_artifact_import import read_source
                body, filename = read_source(self._kernel, task_id, None, relative)
                verified = len(body) == doc['size_bytes'] and hashlib.sha256(body).hexdigest() == doc['sha256']
                if not verified:
                    continue
                result.append({'artifact_id': 'legacy:' + name, 'artifact_type': kind,
                    'sha256': doc['sha256'], 'media_type': doc['media_type'], 'size_bytes': len(body),
                    'filename': filename, 'relative_path': relative, 'source': 'legacy_runner',
                    'stale': True, 'historical': True, 'freshness': 'historical', 'bytes_verified': True})
            except (OSError, ContractError, KeyError, TypeError, ValueError):
                continue
        return result

    def import_public_artifact(self, command: Mapping[str, Any], source_root: str | None) -> dict[str, Any]:
        from .p7_artifact_import import import_artifact
        return import_artifact(self._kernel, dict(command), source_root)


class ApplicationService:
    """The single command path used by both P1 facades."""

    def __init__(
        self,
        event_store: DomainEventStore,
        legacy_adapter: LegacyStageAdapter,
        *,
        contracts_root: str | Path,
        initialize_on_startup: bool = True,
    ) -> None:
        self.event_store = event_store
        self.legacy_adapter = legacy_adapter
        root = Path(contracts_root)
        schemas = {
            name: json.loads((root / name).read_text(encoding="utf-8"))
            for name in (
                "paperspine-domain-commands.schema.json",
                "paperspine-domain-events.schema.json",
                "paperspine-domain-error.schema.json",
                "paperspine-command-result.schema.json",
                "paperspine-domain-commands.v1.1.schema.json",
                "paperspine-domain-events.v1.1.schema.json",
                "paperspine-command-result.v1.1.schema.json",
                "task-configuration-patch.v1.1.schema.json",
                "paperspine-check-delivery.schema.json",
            )
        }
        registry = Registry().with_resources(
            (schema["$id"], Resource.from_contents(schema)) for schema in schemas.values()
        )
        self._literature_validator = Draft202012Validator(
            schemas["task-configuration-patch.v1.1.schema.json"]["properties"]["literature"])
        self._delivery_check_validator = Draft202012Validator(
            schemas['paperspine-check-delivery.schema.json'], registry=registry)
        self._command_validator = Draft202012Validator(
            schemas["paperspine-domain-commands.schema.json"],
            format_checker=FormatChecker(),
            registry=registry,
        )
        self._event_validator = Draft202012Validator(
            schemas["paperspine-domain-events.schema.json"],
            format_checker=FormatChecker(),
            registry=registry,
        )
        self._result_validator = Draft202012Validator(
            schemas["paperspine-command-result.schema.json"],
            format_checker=FormatChecker(),
            registry=registry,
        )
        self._v11_validators = {kind: Draft202012Validator(
            schemas[f"paperspine-{name}.v1.1.schema.json"],
            format_checker=FormatChecker(), registry=registry)
            for kind, name in (("command", "domain-commands"), ("event", "domain-events"),
                               ("result", "command-result"))}
        self._startup_pending = not initialize_on_startup
        if initialize_on_startup:
            with command_lock(self.event_store.database_path):
                self.event_store.rebuild_projections()
                self._recover_interrupted()

    def execute(self, command: Mapping[str, Any]) -> dict[str, Any]:
        with command_lock(self.event_store.database_path):
            self._recover_interrupted()
            return self._run_command(command)

    def _recover_interrupted(self) -> None:
        # One-shot MCP queries may inspect an existing task without triggering
        # recovery, projection rewrites or outbox exports at process startup.
        # Normal commands/get_task retain the same initialization under the lock.
        if self._startup_pending:
            self.legacy_adapter._kernel.recover_outbox()
            self.event_store.rebuild_projections()
            self._startup_pending = False
        for intent in self.event_store.intents():
            if intent["state"].get("status") == "running":
                self._record_failure(intent["command"], WorkFailure("process-restart"))

    def _run_command(self, command: Mapping[str, Any]) -> dict[str, Any]:
        try:
            return self._execute(command)
        except DomainError:
            intent = self.event_store.intent(str(command.get("command_id", "")))
            if intent is not None and intent["state"].get("status") == "running":
                with self.event_store._transaction() as connection:
                    connection.execute("DELETE FROM operation_intents WHERE command_id=?", (command["command_id"],))
            raise
        except Exception as exc:
            if self.event_store.intent(str(command.get("command_id", ""))) is None:
                raise DomainError("internal_error", "暂时无法读取论文任务，请重新连接。", category="internal",
                                  task_id=command.get("task_id"), command_id=command.get("command_id"),
                                  retryable=True, details={"operation": command.get("command_type"),
                                                           "next_action": "reconnect"}) from None
            failure = exc if isinstance(exc, WorkFailure) else WorkFailure(
                "network" if isinstance(exc, (ConnectionError, TimeoutError)) else "tool")
            error = self._record_failure(command, failure)
            raise error from None

    def _record_failure(self, command: Mapping[str, Any], failure: WorkFailure) -> DomainError:
        current = self.event_store.projection(command["task_id"])
        version = (current or {}).get("task_version", 0) + 1
        labels = {"network": "网络连接中断", "model": "模型暂时无法完成工作",
                  "tool": "工具未能完成工作", "process-restart": "上次工作进程已中断"}
        message = labels[failure.kind] + ("。可以安全重试，已保存的论文和选择会保留。" if failure.not_started
                                       else "。执行结果尚不确定，请核对结果后确认未执行，再继续。已保存的论文和选择会保留。")
        payload = {"payload_type": "task.failed", "code": "effect_failed", "message": message,
                   "failure_kind": failure.kind, "operation_id": command["command_id"],
                   "operation": command["command_type"], "retryable": failure.not_started,
                   "next_action": "retry" if failure.not_started else "confirm_no_effect"}
        event = {"contract": "paperspine.domain-event", "schema_version": "1.0",
                 "event_id": f"evt-{uuid4().hex}", "task_id": command["task_id"],
                 "sequence": version, "task_version": version, "event_type": "task.failed",
                 "command_id": f"failure-{uuid4().hex}", "actor": {"actor_id": "recovery", "surface": "system"},
                 "occurred_at": _now(), "payload": payload, "external_action_authorized": False}
        self._event_validator.validate(event)
        error = DomainError("effect_failed", message, category="effect", task_id=command["task_id"],
                            command_id=command["command_id"], current_version=version,
                            retryable=failure.not_started, details={key: value for key, value in payload.items()
                                                                   if key not in {"payload_type", "message", "code"}})
        failed_command = {**command, "command_id": event["command_id"], "expected_version": version - 1}
        self.event_store.append(failed_command, event,
                               {"contract": "paperspine.command-result", "schema_version": "1.0",
                                "result_type": "failed", "task_id": command["task_id"],
                                "task_version": version, "error": error.to_dict()},
                               operation=(command["command_id"], {"status": "failed", "version": version,
                                                                  "error": error.to_dict()}))
        return error

    def recover(self, task_id: str, operation_id: str, *, expected_version: int,
                confirm_no_effect: bool = False, surface: str = "agent") -> dict[str, Any]:
        """Retry the exact previously authorized command; never accept replacement inputs."""
        with command_lock(self.event_store.database_path):
            self._recover_interrupted()
            prior = self.event_store.command(operation_id)
            if prior is not None and prior["task_id"] == task_id:
                return {**prior["result"], "replayed": True}
            intent = self.event_store.intent(operation_id)
            if intent is None or intent["command"]["task_id"] != task_id:
                raise DomainError("not_found", "没有找到需要恢复的操作。", category="missing", task_id=task_id)
            current = self.get_task(task_id)
            if expected_version != current["task_version"]:
                raise DomainError("version_conflict", "论文任务已更新，请刷新后继续。", category="conflict",
                                  task_id=task_id, current_version=current["task_version"])
            error = intent["state"].get("error", {})
            if not error.get("retryable") and not (surface == "business" and confirm_no_effect is True):
                raise DomainError("effect_failed", "结果尚不确定，请由用户核对并确认该操作未执行。",
                                  category="effect", task_id=task_id, command_id=operation_id,
                                  details={"operation": intent["command"]["command_type"], "next_action": "confirm_no_effect"})
            self.event_store.set_intent(intent["command"], {"status": "approved", "version": expected_version,
                "confirmation": {"confirmed_no_effect": confirm_no_effect is True, "surface": surface}})
            return self._run_command(intent["command"])

    def _execute(self, command: Mapping[str, Any]) -> dict[str, Any]:
        command = dict(command)
        task_id = command.get("task_id")
        command_id = command.get("command_id")
        schema_version = command.get("schema_version")
        if schema_version not in (P0_SCHEMA_VERSION, "1.1"):
            raise DomainError(
                "unsupported_schema_version", "Supported schema versions are 1.0 and 1.1.",
                category="capability", task_id=task_id, command_id=command_id,
                details={"supported_versions": [P0_SCHEMA_VERSION, "1.1"]},
            )
        # Exact committed replays keep their original contract, including older
        # figure requests. New writes below must satisfy today's input boundary.
        canonical_command = _canonical(command)
        previous = self.event_store.command(command_id) if isinstance(command_id, str) else None
        if previous is not None:
            if previous["task_id"] != task_id or previous["command_json"] != canonical_command:
                raise DomainError("idempotency_conflict", "command_id was already used with different command inputs.",
                                  category="conflict", task_id=task_id, command_id=command_id)
            return {**previous["result"], "replayed": True}
        payload = command.get("payload")
        if (command.get("command_type") == "RequestDecision" and isinstance(payload, Mapping)
                and payload.get("decision_type") == "figure"):
            if schema_version != "1.1" or not isinstance(payload.get("figure"), Mapping):
                raise DomainError("validation_failed",
                    "新图件请求须使用 schema_version=1.1 并填写 figure：figure_id、label、reference_files、"
                    "comparison_files、current_files、panel_ids；无参考时说明 reference_note。请在同一任务补齐后重新 RequestDecision。",
                    category="validation", task_id=task_id, command_id=command_id,
                    details={"path": ["payload", "figure"], "next_action": "check_request"})
        command_validator = self._v11_validators["command"] if schema_version == "1.1" else self._command_validator
        errors = sorted(command_validator.iter_errors(command), key=lambda item: list(item.path))
        if errors:
            raise DomainError(
                "validation_failed", "请求内容无效，请按缺项在同一任务修正后重新提交。", category="validation",
                task_id=task_id, command_id=command_id,
                details={"path": list(errors[0].absolute_path), "issue": errors[0].message,
                         "next_action": "check_request"},
            )
        current = self.event_store.projection(command["task_id"])
        current_version = 0 if current is None else current["task_version"]
        recovery = (current or {}).get("recovery")
        if recovery and recovery.get("operation_id") != command_id:
            raise DomainError("effect_failed", recovery["message"], category="effect", task_id=task_id,
                              command_id=command_id, current_version=current_version,
                              details={"operation_id": recovery["operation_id"], "operation": recovery["operation"],
                                       "next_action": recovery["next_action"]})
        intent = self.event_store.intent(command_id)
        effective_version = command["expected_version"]
        if intent is not None:
            if _canonical(intent["command"]) != canonical_command:
                raise DomainError("idempotency_conflict", "该操作标识已用于其他内容。", category="conflict",
                                  task_id=task_id, command_id=command_id)
            state = intent["state"]
            if state.get("status") == "failed" and not state["error"]["retryable"]:
                raise DomainError("effect_failed", state["error"]["message"], category="effect",
                                  task_id=task_id, command_id=command_id, details=state["error"]["details"])
            effective_version = state["version"]
        if effective_version != current_version:
            raise DomainError(
                "version_conflict", "expected_version does not match the current task version.",
                category="conflict", task_id=task_id, command_id=command_id,
                current_version=current_version,
                details={"task_summary": current or {"task_id": task_id, "task_version": 0}},
            )
        self._validate_public_state(command, current)
        if command["command_type"] == "RequestDecision":
            payload = command["payload"]
            if payload["task_version"] != command["expected_version"]:
                raise DomainError(
                    "version_conflict", "decision task_version does not match the current task version.",
                    category="conflict", task_id=task_id, command_id=command_id,
                    current_version=current_version, details={"task_summary": current},
                )
            if any(item["decision_id"] == payload["decision_id"] for item in current.get("decisions", [])):
                raise DomainError(
                    "idempotency_conflict", "decision_id already exists.", category="conflict",
                    task_id=task_id, command_id=command_id, current_version=current_version,
                )
            if any(option.get("files") for option in payload["allowed_decisions"]) or "figure" in payload:
                # Use the same discovery boundary as both figure-files HTTP reads.
                # Validate before any intent/effect/event; completed replays stay above.
                task = self.legacy_adapter.verify_task_for_decision(command)
                available = {item["relative_path"] for item in _figure_candidates(
                    task, Path(task["workspace_root"]).resolve())}
                invalid = [
                    {"option_id": option["option_id"], "path": path,
                     "field": ["payload", "allowed_decisions", option_index, "files", file_index]}
                    for option_index, option in enumerate(payload["allowed_decisions"])
                    for file_index, path in enumerate(option.get("files", []))
                    if path not in available
                ]
                if invalid:
                    raise DomainError(
                        "validation_failed",
                        "部分候选文件无法由当前任务预览。请将支持的图件放在 paper/figures/ 或 "
                        "paper/figure-candidates/（可含子目录），使用发现清单中的精确相对路径后重新请求。",
                        category="validation", task_id=task_id, command_id=command_id,
                        current_version=current_version,
                        details={"invalid_files": invalid,
                                 "standard_directories": ["paper/figures/", "paper/figure-candidates/"],
                                 "next_action": "check_request"},
                    )
        if command["command_type"] == "RequestDecision" and "figure" in command["payload"]:
            payload = command["payload"]
            meta = payload["figure"]
            if payload["decision_type"] != "figure":
                raise DomainError("validation_failed", "图件信息只能用于图件选择。", category="validation", task_id=task_id)
            invalid = [{"field": ["payload", "figure", field, index], "path": path}
                       for field in ("reference_files", "comparison_files", "current_files")
                       for index, path in enumerate(meta[field]) if path not in available]
            if invalid:
                raise DomainError("validation_failed",
                    "参考图、对照或当前图无法预览。请在同一任务的 paper/figures/ 或 paper/figure-candidates/ "
                    "放入实际文件，按发现清单的精确相对路径修正后重新 RequestDecision。",
                    category="validation", task_id=task_id,
                    details={"invalid_files": invalid, "next_action": "check_request"})
            options = payload["allowed_decisions"]
            option_ids = [item["option_id"] for item in options]
            selected_files = {path for item in options for path in item.get("files", [])}
            if len(option_ids) != len(set(option_ids)):
                raise DomainError("validation_failed", "option_id 重复；请在同一任务为每个选项使用不同编号后重试。",
                                  category="validation", details={"path": ["payload", "allowed_decisions"],
                                                                  "next_action": "check_request"})
            ambiguous = [item["option_id"] for item in options if _figure_option_action(item) is None]
            if ambiguous:
                raise DomainError("validation_failed",
                    "选项 action 缺失或与既有 option_id 冲突；请在同一任务明确 keep/adopt/revise/reject 后重试，"
                    "修改选项不能声明为采用。",
                    category="validation", details={"option_ids": ambiguous, "next_action": "check_request"})
            aids = set(meta["reference_files"]) | set(meta["comparison_files"])
            overlap = sorted((aids & (selected_files | set(meta["current_files"])))
                             | (set(meta["reference_files"]) & set(meta["comparison_files"])))
            if overlap:
                raise DomainError("validation_failed", "参考图、并排对照应各用独立文件，不能同时作为当前成果或可采用候选；请修正对应文件后在同一任务重试。",
                                  category="validation", details={"overlapping_files": overlap, "next_action": "check_request"})
            if meta.get("panel_id") and meta["panel_id"] not in meta["panel_ids"]:
                raise DomainError("validation_failed", "panel_id 必须在本次 panel_ids 计划中；请在同一任务补全计划后重试。",
                                  category="validation", details={"panel_id": meta["panel_id"],
                                                                  "next_action": "check_request"})
            self._validate_figure_panel_plan(meta, current)
            if any(d.get("status") == "pending" and not d.get("stale") and d.get("figure")
                   and (d["figure"]["figure_id"], d["figure"].get("panel_id")) == (meta["figure_id"], meta.get("panel_id"))
                   for d in current.get("decisions", [])):
                raise DomainError("validation_failed", "此图或子图仍有待确认的方案，请先读取同一任务已有选择与意见。", category="validation", task_id=task_id)
            prior_id = meta.get("replaces_decision_id")
            if prior_id:
                prior = next((item for item in current.get("decisions", []) if item["decision_id"] == prior_id), None)
                if not prior or prior["decision_type"] != "figure" or prior["status"] == "pending":
                    raise DomainError("validation_failed", "请指定已保存的同图版本。", category="validation", task_id=task_id)
                old = prior.get("figure")
                if not old or (old["figure_id"], old.get("panel_id")) != (meta["figure_id"], meta.get("panel_id")):
                    raise DomainError("validation_failed", "新版本不能替代另一张图或子图。", category="validation", task_id=task_id)
                if any(d.get("figure", {}).get("replaces_decision_id") == prior_id for d in current.get("decisions", [])):
                    raise DomainError("validation_failed", "此版本已有后继；请读取同一任务最新图件决策并替代最新版本。",
                                      category="validation", task_id=task_id)
        if command["command_type"] == "ResolveDecision":
            decision = next((d for d in current.get("decisions", [])
                             if d["decision_id"] == command["payload"]["decision_id"]), None)
            if decision and decision.get("figure"):
                # A panel plan may have arrived after the assembly request.
                option = next((item for item in decision.get("allowed_decision_details", [])
                               if item["option_id"] == command["payload"]["option_id"]), {})
                if _figure_option_action(option) not in {"revise", "reject"}:
                    self._validate_figure_panel_plan(decision["figure"], current)
        review_metadata = None
        if command["command_type"] == "SubmitReview" and schema_version == "1.1":
            try:
                review_metadata = review_event_metadata(command["payload"], current)
            except ValueError as exc:
                raise DomainError("validation_failed", str(exc), category="validation",
                                  task_id=task_id, command_id=command_id,
                                  details={"next_action": "check_request"}) from exc
        source_root = None
        if command['command_type'] == 'PublishArtifact' and 'source' in command['payload']:
            grant_id = command['payload']['source'].get('grant_id')
            # Resolve only grants from successfully committed commands of this task.
            for prior_event in self.event_store.events(command['task_id']):
                if prior_event['event_type'] == 'materials.authorized':
                    accepted = self.event_store.command(prior_event['command_id'])
                    if accepted:
                        original = json.loads(accepted['command_json'])
                        for grant in original['payload']['grants']:
                            if grant['grant_id'] == grant_id:
                                root = str(Path(grant['uri']).resolve())
                                if source_root is not None and source_root != root:
                                    raise DomainError('validation_failed', '材料授权编号不唯一，请重新授权。', category='validation')
                                source_root = root
            if grant_id is not None and source_root is None:
                for grant in self.legacy_adapter._kernel.get_task(task_id).get('material_grants', []):
                    if grant['grant_id'] == grant_id:
                        source_root = grant['canonical_target']
                        break
                if source_root is None:
                    raise DomainError('validation_failed', '请先为本任务授权外部材料所在文件夹。', category='validation')
        confirmation = (intent or {}).get("state", {}).get("confirmation")
        self.event_store.set_intent(command, {"status": "running", "version": current_version,
                                              "confirmation": confirmation})
        try:
            effect_command = command
            if command['command_type'] == 'PublishArtifact' and 'source' in command['payload']:
                imported = self.legacy_adapter.import_public_artifact(command, source_root)
                effect_command = {**command, 'payload': imported}
            legacy_task = (self.legacy_adapter.open_task(command)
                           if command["command_type"] == "OpenTask"
                           else self.legacy_adapter.apply_public_command(effect_command))
        except TaskNotFoundError as exc:
            raise DomainError(
                "not_found", "无法找到所需的论文任务或文件。", category="missing", task_id=task_id, command_id=command_id,
                current_version=current_version,
            ) from exc
        except ContractError as exc:
            raise DomainError("validation_failed", str(exc), category="validation",
                              task_id=task_id, command_id=command_id, current_version=current_version) from exc
        except IdempotencyConflictError as exc:
            raise DomainError(
                "idempotency_conflict", "操作与已保存的任务内容冲突，请刷新后检查。", category="conflict",
                task_id=task_id, command_id=command_id, current_version=current_version,
            ) from exc
        if legacy_task["task_id"] != command["task_id"]:
            raise DomainError(
                "effect_failed", "legacy task identity did not match the domain task.",
                category="effect", task_id=task_id, command_id=command_id,
                current_version=current_version,
            )
        if command["command_type"] == "OpenTask":
            if current is not None and current.get("opened_mode") and command["payload"]["mode"] != "resume":
                raise DomainError(
                    "version_conflict", "An existing task can only be resumed.",
                    category="conflict", task_id=task_id, command_id=command_id,
                    current_version=current_version, details={"task_summary": current},
                )
            event_type = "task.opened"
            event_payload = {"payload_type": event_type, "mode": command["payload"]["mode"]}
        elif command["command_type"] == "RequestDecision":
            requested_version = command["payload"]["task_version"]
            decision_id = command["payload"]["decision_id"]
            event_type = "decision.required"
            event_payload = {
                "payload_type": event_type,
                "decision_id": decision_id,
                "task_version": requested_version,
                "decision_type": command["payload"]["decision_type"],
                "prompt": command["payload"]["prompt"],
                "allowed_decisions": [item["option_id"] for item in command["payload"]["allowed_decisions"]],
                "allowed_decision_details": list(command["payload"]["allowed_decisions"]),
                **({"figure": dict(command["payload"]["figure"])} if "figure" in command["payload"] else {}),
                "scope_refs": list(command["payload"]["scope_refs"]),
                "requested_by_command_id": command["payload"]["requested_by_command_id"],
                "expires_at": command["payload"]["expires_at"],
            }
        elif command["command_type"] == "ResolveDecision":
            decision_id = command["payload"]["decision_id"]
            decision = next(
                (item for item in current.get("decisions", []) if item["decision_id"] == decision_id), None
            )
            if decision is None:
                raise DomainError(
                    "not_found", "The requested decision does not exist.", category="missing",
                    task_id=task_id, command_id=command_id, current_version=current_version,
                )
            if decision["status"] != "pending":
                raise DomainError(
                    "decision_already_resolved", "The decision has already been resolved.",
                    category="decision", task_id=task_id, command_id=command_id,
                    current_version=current_version,
                )
            if command["payload"]["option_id"] not in decision["allowed_decisions"]:
                raise DomainError(
                    "validation_failed", "option_id is not allowed for this decision.",
                    category="validation", task_id=task_id, command_id=command_id,
                    current_version=current_version,
                    details={"allowed_decisions": decision["allowed_decisions"]},
                )
            event_type = "decision.resolved"
            event_payload = {
                "payload_type": event_type, "decision_id": decision_id,
                "option_id": command["payload"]["option_id"],
                "confirmed_at": command["payload"]["confirmed_at"],
                "reason": command["payload"].get("reason", ""),
            }
        else:
            payload = effect_command["payload"]
            event_type, event_payload = self._event_for_public_command(
                command["command_type"], payload, current or {},
                expected_revision=command.get("expected_revision"))
            if review_metadata is not None:
                event_payload.update(review_metadata)
            if schema_version == "1.1" and command["command_type"] == "AuthorizeMaterials":
                inputs = self.legacy_adapter.task_inputs(task_id)
                grants = {} if payload.get("replace") else {item["grant_id"]: item for item in (current or {}).get("material_grants", [])}
                for grant in payload["grants"]:
                    canonical = str(Path(grant["uri"]).resolve())
                    legacy = next(item for item in inputs["material_grants"]
                                  if str(Path(item["canonical_target"]).resolve()) == canonical)
                    grants[grant["grant_id"]] = {**grant, "uri": canonical,
                                                "runner_grant_id": legacy["grant_id"]}
                event_payload.update(grants=list(grants.values()), inventory=inputs["material_inventory_payload"])
        version = current_version + 1
        event = {
            "contract": "paperspine.domain-event",
            "schema_version": schema_version,
            "event_id": f"evt-{uuid4().hex}",
            "task_id": command["task_id"],
            "sequence": version,
            "task_version": version,
            "event_type": event_type,
            "command_id": command["command_id"],
            "actor": {
                "actor_id": command["actor"]["actor_id"],
                "surface": command["actor"]["surface"],
            },
            "occurred_at": _now(),
            "payload": event_payload,
            "external_action_authorized": False,
        }
        if intent is not None:
            event["recovery"] = {"operation_id": command_id,
                                 "confirmed_no_effect": bool((confirmation or {}).get("confirmed_no_effect")),
                                 "surface": (confirmation or {}).get("surface", command["actor"]["surface"])}
        event_validator = self._v11_validators["event"] if schema_version == "1.1" else self._event_validator
        event_errors = list(event_validator.iter_errors(event))
        if event_errors:
            raise DomainError(
                "internal_error", "操作暂时无法保存，请刷新任务后继续。", category="internal",
                task_id=task_id, command_id=command_id, current_version=current_version,
                details={"validation_path": list(event_errors[0].absolute_path),
                         "validation_message": event_errors[0].message},
            )
        projection = _apply_event(current, event)
        result = {
            "contract": "paperspine.command-result",
            "schema_version": schema_version,
            "result_type": "completed",
            "task_id": command["task_id"],
            "task_version": version,
            "events": [event],
            "projection": projection,
            "replayed": False,
        }
        result_validator = self._v11_validators["result"] if schema_version == "1.1" else self._result_validator
        result_errors = list(result_validator.iter_errors(result))
        if result_errors:
            raise DomainError(
                "internal_error", "操作暂时无法保存，请刷新任务后继续。", category="internal",
                task_id=task_id, command_id=command_id, current_version=current_version,
            )
        try:
            committed = self.event_store.append(command, event, result)
            if not committed:
                previous = self.event_store.command(command["command_id"])
                replayed = dict(previous["result"])
                replayed["replayed"] = True
                return replayed
        except IdempotencyConflictError as exc:
            raise DomainError(
                "idempotency_conflict", str(exc), category="conflict",
                task_id=task_id, command_id=command_id, current_version=current_version,
            ) from exc
        except sqlite3.IntegrityError as exc:
            latest = self.event_store.projection(command["task_id"])
            if str(exc).startswith("version_conflict:"):
                raise DomainError(
                    "version_conflict", "Another command committed first; read the latest task and retry.",
                    category="conflict", task_id=task_id, command_id=command_id,
                    current_version=(latest or {}).get("task_version", 0),
                    details={"task_summary": latest or {"task_id": task_id, "task_version": 0}},
                    retryable=True,
                ) from exc
            raise
        # Materialise a small, stable handoff for the host PaperSpine Skill and
        # Web surface after the event is durable.  This is derived state only;
        # a bridge failure must never turn a successful paper command into a
        # false failure.
        try:
            # The same read enrichment retains legacy config/choices/files when
            # feedback is committed before any new configuration has been saved.
            self.get_task(command['task_id'])
        except (OSError, TypeError, ValueError, KeyError):
            pass
        return result

    @staticmethod
    def _validate_figure_panel_plan(meta: Mapping[str, Any], current: Mapping[str, Any]) -> None:
        """Check explicit identities only; neither filenames nor visual merit are evidence here."""
        same_figure = [d for d in current.get("decisions", []) if not d.get("stale")
                       and d.get("figure", {}).get("figure_id") == meta["figure_id"]]
        planned = set(meta.get("panel_ids", []))
        for decision in same_figure:
            planned.update(decision["figure"].get("panel_ids", []))
        panel = meta.get("panel_id")
        if panel:
            if planned and panel not in planned:
                raise DomainError("validation_failed", "panel_id 不在已声明的 panel_ids 中；请在同一任务修正子图编号或补全计划后重试。",
                                  category="validation", details={"panel_id": panel, "panel_ids": sorted(planned),
                                                                  "next_action": "check_request"})
            return
        # Even pre-plan explicit panel decisions must not be silently swallowed
        # by a later whole-figure choice. Their latest independent answers survive.
        latest = {d["figure"]["panel_id"]: d for d in same_figure if d["figure"].get("panel_id")}
        planned.update(latest)
        missing = sorted(p for p in planned if p not in latest or latest[p].get("status") != "resolved")
        unaccepted = []
        for panel_id in sorted(planned - set(missing)):
            decision = latest[panel_id]
            option = next((item for item in decision.get("allowed_decision_details", [])
                           if item["option_id"] == decision.get("option_id")), {})
            if _figure_option_action(option) not in {"keep", "adopt"}:
                unaccepted.append(panel_id)
        if missing or unaccepted:
            raise DomainError("validation_failed",
                "整图选择尚缺独立子图采纳：" + ", ".join(sorted(set(missing + unaccepted))) +
                "。修改/拒绝或语义未明确的回复不是采纳。请在同一任务读取意见，按 figure_id + panel_id "
                "提交修正版选择（自定义选项填写 action）；各子图明确 keep/adopt 后再请求或确认整图，勿改写旧决定。",
                category="validation", task_id=current["task_id"],
                details={"missing_panel_ids": missing, "unaccepted_panel_ids": unaccepted,
                         "next_action": "check_request"})

    @staticmethod
    def _publication_document_id(payload: Mapping[str, Any], current: Mapping[str, Any]) -> str | None:
        """Resolve replacement identity before effects, then freeze it in the event."""
        published = {item['artifact_id']: item for item in current.get('artifacts', [])}
        identities = set()
        for artifact_id in payload.get('supersedes_artifact_ids', []):
            prior = published.get(artifact_id)
            if artifact_id == payload['artifact_id'] or prior is None or prior['artifact_type'] != payload['artifact_type']:
                raise DomainError('validation_failed',
                                  'Replacement must name a different published artifact of the same type in this task.',
                                  category='validation', details={'artifact_id': artifact_id})
            # Historical targets remain valid; missing identity is the legacy main.
            identities.add(prior.get('document_id', 'main'))
        if 'document_id' in payload:
            return payload['document_id']  # Explicit correction overrides prior classification.
        if len(identities) > 1:
            raise DomainError('validation_failed',
                              'Replacement targets belong to multiple documents; supply an explicit document_id and retry in this task.',
                              category='validation', details={'path': ['payload', 'document_id'],
                                                              'document_ids': sorted(identities),
                                                              'next_action': 'check_request'})
        # Keep new, unrelated publications compatible with legacy omission.
        return next(iter(identities), None)

    def _validate_public_state(self, command: Mapping[str, Any],
                               current: Mapping[str, Any] | None) -> None:
        kind, payload = command["command_type"], command["payload"]
        if kind == "OpenTask":
            return
        if current is None:
            raise DomainError("not_found", "The domain task does not exist.", category="missing",
                              task_id=command["task_id"], command_id=command["command_id"])
        if kind == 'SaveConfiguration':
            configuration = self.legacy_adapter.merged_configuration(
                command['task_id'], payload, current.get('configuration'))
            errors = list(self._literature_validator.iter_errors(configuration['literature']))
            if errors:
                raise DomainError('validation_failed', '文献学习设置无效；自定参考文献数量时须填写正整数。',
                                  category='validation', details={'path': ['literature', *errors[0].absolute_path]})
        if kind == "PublishArtifact" and payload.get("package_scope") and payload["artifact_type"] != "delivery_package":
            raise DomainError("validation_failed", "package_scope只能用于文件包。", category="validation")
        if kind == 'PublishArtifact':
            self._publication_document_id(payload, current)
        if kind == "AuthorizeMaterials" and command["schema_version"] == "1.1":
            prior = {item["grant_id"]: item["uri"] for item in current.get("material_grants", [])}
            for grant in payload["grants"]:
                path = Path(grant["uri"])
                if not path.is_absolute() or not path.is_dir():
                    raise DomainError("validation_failed", "材料路径必须是存在的本地文件夹，请修改后重试。",
                                      category="validation", details={"uri": grant["uri"]})
                if grant["grant_id"] in prior and str(path.resolve()) != prior[grant["grant_id"]]:
                    raise DomainError("validation_failed", "同一授权编号不能改指另一个路径。", category="validation")
        if kind == 'RequestRevision':
            if command['actor']['authority'] != 'authenticated_user' or command['actor']['surface'] != 'business':
                raise DomainError('forbidden', 'User feedback requires the authenticated user.', category='authorization')
            if payload.get('feedback_file'):
                from .p7_artifact_import import read_source
                read_source(self.legacy_adapter._kernel, command['task_id'], None, payload['feedback_file'])
        if kind == "SubmitReview":
            if command["actor"]["authority"] != "independent_reviewer":
                raise DomainError("forbidden", "Review submission requires an independent reviewer.",
                                  category="authorization", task_id=command["task_id"],
                                  command_id=command["command_id"])
            if payload["reviewer_id"] != command["actor"]["actor_id"]:
                raise DomainError("forbidden", "reviewer_id must match trusted reviewer identity.",
                                  category="authorization", task_id=command["task_id"],
                                  command_id=command["command_id"])
            published = {item["artifact_id"]: item for item in current.get("artifacts", [])}
            missing = sorted(set(payload["reviewed_artifact_ids"]) - published.keys())
            if missing:
                raise DomainError("validation_failed", "Review references unpublished artifacts.",
                                  category="validation", details={"artifact_ids": missing})
            if any(item["review_id"] == payload["review_id"] for item in current.get("reviews", [])):
                raise DomainError("idempotency_conflict", "review_id already exists.", category="conflict")
            finding_ids = [item["finding_id"] for item in payload["findings"]]
            if len(finding_ids) != len(set(finding_ids)):
                raise DomainError("validation_failed", "finding_id must be unique within a review.",
                                  category="validation", details={"review_id": payload["review_id"]})
            # Check the exact registered copies before recording intent/effects.
            # A report's prose is not a machine-readable artifact association.
            ids = set(payload['reviewed_artifact_ids'])
            if payload.get('report_artifact_id') in published:
                ids.add(payload['report_artifact_id'])
            invalid = []
            for artifact_id in sorted(ids):
                item = published[artifact_id]
                try:
                    if item.get('stale') or item.get('historical'):
                        raise ContractError('Review target is no longer current.')
                    self._verify_current_artifact_bytes(command['task_id'], item)
                except (ContractError, OSError, ValueError, KeyError):
                    invalid.append(artifact_id)
            if invalid:
                raise DomainError('validation_failed',
                    'Review files are stale, unsafe, unavailable or changed: ' + ', '.join(invalid)
                    + '. Repair/republish these artifacts and review their current bytes in this task.',
                    category='validation', details={'artifact_ids': invalid, 'next_action': 'check_request'})
        if kind == "ResolveFinding":
            # A finding may only be closed against the exact task revision that
            # contains its remediation.  This prevents an old reviewer receipt
            # from silently closing a finding after a newer draft was published.
            if command.get("schema_version") == "1.1":
                revision_id = payload.get("revision_id")
                if not isinstance(revision_id, str) or not revision_id:
                    raise DomainError("validation_failed", "Finding resolution must name the revised version.",
                                      category="validation")
                kernel_revision = current["task_version"]
                if str(revision_id) != str(kernel_revision):
                    raise DomainError("version_conflict", "Finding resolution targets a stale revision.",
                                      category="conflict", retryable=True,
                                      current_version=current.get("task_version"),
                                      details={"current_revision": kernel_revision})
            _finding_to_resolve(current, payload)
            published = {item["artifact_id"] for item in current.get("artifacts", [])}
            missing = sorted(set(payload["resolution_artifact_ids"]) - published)
            if missing:
                raise DomainError("validation_failed", "Finding resolution references unpublished artifacts.",
                                  category="validation", details={"artifact_ids": missing})
        if kind == "PrepareDelivery" and any(
            item.get("status") == "open" and item.get("severity") in {"blocking", "major"}
            for item in current.get("findings", [])
        ):
            raise DomainError("validation_failed", "Blocking or major review findings remain open.",
                              category="validation")

    def _event_for_public_command(self, command_type: str, payload: Mapping[str, Any],
                                  current: Mapping[str, Any], *, expected_revision: int | None = None
                                  ) -> tuple[str, dict[str, Any]]:
        if command_type == 'SaveConfiguration':
            inputs = self.legacy_adapter.task_inputs(str(current['task_id']))
            configuration = self.legacy_adapter.merged_configuration(
                current['task_id'], payload, current.get('configuration'))
            return 'configuration.saved', {'payload_type': 'configuration.saved',
                'configuration': configuration, 'run_contract': {},
                'inventory': inputs.get('material_inventory_payload') or {},
                'material_grants': current.get('material_grants') or [
                    {'grant_id': item['grant_id'], 'uri': item['canonical_target'], 'scope': 'read_only',
                     'runner_grant_id': item['grant_id']} for item in inputs['material_grants']]}
        if command_type == 'RequestRevision':
            previous = current.get('delivery') or (current.get('delivery_history') or [{}])[-1]
            event = {'payload_type': 'revision.requested', 'feedback': payload['feedback'],
                     'scope': payload['scope'], 'requested_revision': current['task_version'] + 1,
                     'previous_completed_revision': previous.get('task_version', 0)}
            if payload.get('feedback_file'):
                event['feedback_file'] = payload['feedback_file']
            return 'revision.requested', event
        if command_type == "AuthorizeMaterials":
            roots = sorted(str(Path(item["uri"]).resolve()) for item in payload["grants"])
            digest = self.legacy_adapter.material_snapshot_sha256(str(current.get("task_id")))
            digest = digest or hashlib.sha256(("\n".join(roots) + "\n").encode("utf-8")).hexdigest()
            return "materials.authorized", {"payload_type": "materials.authorized",
                "grant_ids": [item["grant_id"] for item in payload["grants"]],
                "snapshot_sha256": digest}
        if command_type == "CommitMilestone":
            return "milestone.committed", {"payload_type": "milestone.committed",
                "stage": payload["stage"], "milestone_id": f"milestone-{uuid4().hex}",
                "artifact_ids": list(payload["artifact_ids"]), "summary": payload["summary"]}
        if command_type == "BindEvidence":
            return "evidence.bound", {"payload_type": "evidence.bound",
                **{key: payload[key] for key in ("claim_id", "evidence_id", "relation")}}
        if command_type == "PublishArtifact":
            document_id = self._publication_document_id(payload, current)
            return "artifact.published", {"payload_type": "artifact.published",
                **{key: payload[key] for key in
                   ("artifact_id", "artifact_type", "sha256", "media_type", "stage")},
                **({"package_scope": payload["package_scope"]} if payload.get("package_scope") else {}),
                **({"document_id": document_id} if document_id is not None else {}),
                **({'supersedes_artifact_ids': list(payload['supersedes_artifact_ids'])}
                   if payload.get('supersedes_artifact_ids') else {})}
        if command_type == "SubmitReview":
            findings = [dict(item) for item in payload["findings"]]
            return "review.submitted", {"payload_type": "review.submitted",
                "review_id": payload["review_id"], "finding_ids": [item["finding_id"] for item in findings],
                "reviewed_artifact_ids": list(payload["reviewed_artifact_ids"]),
                "reviewer_id": payload["reviewer_id"], "findings": findings}
        if command_type == "ResolveFinding":
            finding = _finding_to_resolve(current, payload)
            return "finding.resolved", {"payload_type": "finding.resolved",
                "review_id": finding["review_id"], "finding_id": finding["finding_id"],
                **({"revision_id": payload["revision_id"]} if "revision_id" in payload else {}),
                "resolution_artifact_ids": list(payload["resolution_artifact_ids"]),
                "explanation": payload["explanation"]}
        if command_type == "PrepareDelivery":
            if any(item.get('status') == 'pending' and not item.get('stale') for item in current.get('decisions', [])):
                raise DomainError('validation_failed', 'User choices remain pending.', category='validation')
            inputs = _delivery_inputs(current, payload['required_formats'])
            if not inputs['outputs'] or inputs['unreviewed']:
                ids = [item['artifact_id'] for item in inputs['unreviewed']]
                raise DomainError('validation_failed', 'The current manuscript outputs need independent review: '
                                  + ', '.join(ids), category='validation', details={'artifact_ids': ids})
            try:
                for item in current.get('artifacts', []):
                    if not item.get('stale'):
                        self._verify_current_artifact_bytes(current['task_id'], item)
            except (ContractError, TaskNotFoundError, OSError, ValueError, KeyError) as exc:
                raise DomainError('validation_failed', 'Current output bytes are unavailable or changed: '
                                  + item['artifact_id'] + '; repair and republish in this task.',
                                  category='validation', details={'artifact_ids': [item['artifact_id']]}) from exc
            artifacts = inputs['artifacts']
            packages = [item for item in artifacts if item["artifact_type"] == "delivery_package"]
            if not packages:
                raise DomainError("validation_failed", "A fresh delivery package must be published first.",
                                  category="validation")
            missing = inputs['missing_formats']
            if missing:
                raise DomainError("validation_failed", "Required local formats are not published.",
                                  category="validation", details={"missing_formats": missing})
            required = inputs['required']
            from .p7_artifact_import import verify_delivery_archive
            package = packages[-1]
            try:
                path = self.legacy_adapter.artifact_path(current['task_id'], package['artifact_id'],
                                                         expected_sha256=package['sha256'])
                verify_delivery_archive(path, required)
            except (ContractError, TaskNotFoundError, OSError) as exc:
                raise DomainError('validation_failed', str(exc), category='validation',
                                  details=getattr(exc, 'details', {})) from exc
            return "delivery.ready", {"payload_type": "delivery.ready",
                "package_artifact_id": packages[-1]["artifact_id"],
                "local_download_ready": True, "submission_ready": False}
        raise AssertionError(f"unsupported command: {command_type}")

    def _verify_current_artifact_bytes(self, task_id: str, item: Mapping[str, Any],
                                       task: Mapping[str, Any] | None = None) -> None:
        """Read only the exact receipt through the existing safe workspace reader."""
        from .p7_artifact_import import read_source
        kernel = self.legacy_adapter._kernel
        task = task or kernel.get_task(task_id)
        with kernel.store.read_connection() as connection:
            row = connection.execute(
                'SELECT receipt_json,subject_revision FROM artifacts WHERE task_id=? '
                'AND artifact_id=? AND sha256=? ORDER BY rowid DESC LIMIT 1',
                (task_id, item['artifact_id'], item['sha256'])).fetchone()
        if row is None or row['subject_revision'] != task['revision']:
            raise ContractError('Current artifact receipt is unavailable or stale.')
        receipt = json.loads(row['receipt_json'])
        relative = Path(receipt['path']).relative_to(Path(task['workspace_root'])).as_posix()
        output, _ = read_source(kernel, task_id, None, relative)
        if len(output) != receipt['size_bytes'] or hashlib.sha256(output).hexdigest() != item['sha256']:
            raise ContractError('Current output bytes changed; repair and republish.')

    def check_delivery(self, request: Mapping[str, Any]) -> dict[str, Any]:
        """Diagnose one same-task candidate without recovery, file exports or writes."""
        errors = list(self._delivery_check_validator.iter_errors(request))
        if errors:
            raise DomainError('validation_failed', 'Invalid delivery check request.', category='validation',
                              details={'fields': [list(error.absolute_path) for error in errors]})
        task_id = request['task_id']
        # get_task() also recovers operations and exports workflow files. A query
        # must read the authoritative projection directly, not invoke those effects.
        current = self.event_store.projection(task_id)
        if current is None:
            raise DomainError('not_found', 'The domain task does not exist.', category='missing', task_id=task_id)
        from .p7_artifact_import import MAX_SOURCE_BYTES, media_type, read_source, verify_delivery_archive
        inputs = _delivery_inputs(current, request['required_formats'])
        kernel = self.legacy_adapter._kernel
        task = kernel.get_task(task_id)

        def brief(item):
            result = {key: item[key] for key in ('artifact_id', 'artifact_type', 'sha256', 'stage') if key in item}
            if item['artifact_type'] in {'pdf', 'docx', 'tex', 'manuscript_source', 'bibliography'}:
                result['document_id'] = item.get('document_id', 'main')
            return result

        candidate = {'relative_path': request['package_path'], 'max_size_bytes': MAX_SOURCE_BYTES,
                     'archive_checks_passed': False, 'archive': None, 'issues': [],
                     'published_current_artifact_ids': []}
        try:
            body, name = read_source(kernel, task_id, None, request['package_path'])
            candidate.update(size_bytes=len(body), sha256=hashlib.sha256(body).hexdigest())
            candidate['media_type'] = media_type(body, name, 'delivery_package')
            if candidate['media_type'] != 'application/zip':
                raise ContractError('delivery package must be a ZIP archive')
            candidate['archive'] = verify_delivery_archive(io.BytesIO(body), inputs['required'])
            candidate['archive_checks_passed'] = True
        except (ContractError, OSError) as exc:
            details = getattr(exc, 'details', {})
            if 'member_count' in details:
                candidate['archive'] = details
            elif 'size_bytes' in details:
                candidate.update(details)
            candidate['issues'].append({'code': 'validation_failed',
                'message': str(exc) if isinstance(exc, ContractError) else 'Candidate file is unavailable or unsafe.'})
        if candidate.get('sha256'):
            candidate['published_current_artifact_ids'] = [item['artifact_id'] for item in inputs['artifacts']
                if item['artifact_type'] == 'delivery_package' and item['sha256'] == candidate['sha256']]

        # Inspect only explicitly current receipts in this task, never the broad
        # list_artifacts() reader (which also opens unrelated historical files).
        # The shared source reader enforces workspace, links, hardlinks and limits.
        byte_issues = []
        for item in inputs['artifacts']:
            try:
                self._verify_current_artifact_bytes(task_id, item, task)
            except (ContractError, OSError, ValueError, KeyError):
                byte_issues.append({**brief(item), 'message': 'Current output bytes are unavailable, unsafe or changed; repair and republish.'})

        inputs = _delivery_inputs(current, request['required_formats'],
                                  {item['artifact_id'] for item in byte_issues})
        observed = self.event_store.projection(task_id)
        return {'contract': 'paperspine.delivery-check', 'schema_version': '1.0',
                'task_id': task_id, 'task_version': current['task_version'],
                'observed_task_version': observed['task_version'] if observed else None,
                'snapshot_changed': observed is None or observed['task_version'] != current['task_version'],
                'read_only': True, 'readiness_evaluated': False,
                'candidate': candidate, 'required_formats': list(request['required_formats']),
                'required_artifacts': [brief(item) for item in inputs['required']],
                'current_artifact_issues': byte_issues,
                'review': {'outputs_present': bool(inputs['outputs']),
                           'coverage_complete': bool(inputs['outputs']) and not inputs['unreviewed'],
                           'unreviewed_current_artifacts': [brief(item) for item in inputs['unreviewed']]},
                'pending': {'publish_formats': inputs['missing_formats'],
                            'publish_candidate': not bool(candidate['published_current_artifact_ids']),
                            'review_artifact_ids': [item['artifact_id'] for item in inputs['unreviewed']]},
                'pending_decision_ids': [item['decision_id'] for item in current.get('decisions', [])
                                         if item.get('status') == 'pending' and not item.get('stale')],
                'open_findings': [dict(item) for item in current.get('findings', [])
                                  if item.get('status') == 'open' and item.get('severity') in {'major', 'blocking'}],
                'limitations': ['Snapshot diagnostics only; PrepareDelivery remains the delivery authority.',
                    'Missing published formats cannot yet be compared. Publish final outputs, check the candidate again, '
                    'complete actual independent review coverage, then publish the package and prepare using the latest task_version.',
                    'Later output publication may stale a published package. Repeat this read after changes.',
                    'Nested archives are not expanded; required outputs must be direct file members at any directory depth.',
                    'Archive safety does not establish permission to share private contents.']}

    def get_task(self, task_id: str) -> dict[str, Any]:
        """Read the current P1 projection from the same event-store authority."""
        # A surviving REST process must notice an Agent process that died. Never
        # wait for a live operation just to read its already-saved paper state.
        with command_lock(self.event_store.database_path, blocking=False) as acquired:
            if acquired:
                self._recover_interrupted()
        projection = self.event_store.projection(task_id)
        if projection is None:
            raise DomainError(
                "not_found", "The domain task does not exist.", category="missing",
                task_id=task_id,
            )
        # Retained inputs remain readable; only domain events determine current progress.
        try:
            kernel_task = self.legacy_adapter._kernel.get_task(task_id)
            projection["title"] = kernel_task["title"]
            projection["description"] = kernel_task.get("description") or f"围绕“{projection['title']}”的 PaperSpine 论文任务"
            inputs = self.legacy_adapter.task_inputs(task_id)
            inherited = (inputs.get("run_contract_payload") or {}).get("configuration")
            if inherited and not projection.get("configuration"):
                configuration = dict(inherited)
                if 'deliverables' in configuration:
                    configuration["formats"] = [{"word": "docx", "latex": "tex"}.get(fmt, fmt)
                                                for fmt in configuration.pop("deliverables")]
                projection["configuration"] = configuration_with_defaults(configuration)
                projection["configuration_source"] = "legacy_runner"
                projection["configuration_user_confirmed"] = False
                projection["configuration_stale"] = False
                projection["configuration_migration_required"] = False
            if inputs.get("material_inventory_payload") is not None and not projection.get("material_inventory"):
                projection = dict(projection)
                projection["material_inventory"] = inputs["material_inventory_payload"]
                projection["material_grants"] = [
                    {"grant_id": item["grant_id"], "uri": item.get("canonical_target"),
                     "scope": "read_only", "runner_grant_id": item["grant_id"]}
                    for item in inputs.get("material_grants", [])
                ]
                projection["run_contract"] = inputs.get("run_contract")
            # Legacy progress is historical context, never current stage authority.
            runner = self.legacy_adapter._runner
            if runner is not None:
                snapshot = runner.snapshot(task_id)
                issue_fields = ("issue_id", "code", "status", "message", "category")
                projection["legacy_runner"] = {
                    "revision": snapshot.get("revision"),
                    "stage": snapshot.get("stage"),
                    "task_status": snapshot.get("task_status"),
                    "open_issues": [
                        {key: issue.get(key) for key in issue_fields if key in issue}
                        for issue in (snapshot.get("open_issues") or [])
                    ],
                    "next_actions": list(snapshot.get("next_actions") or []),
                    "material_inventory_fresh": bool(snapshot.get("material_inventory_fresh")),
                    "run_contract_fresh": bool(snapshot.get("run_contract_fresh")),
                    "figure_quality_status": (snapshot.get("figure_quality") or {}).get("status"),
                    "migration_status": snapshot.get("migration_status"),
                    "external_action_authorized": False,
                }
        except Exception:
            # An uninitialised or legacy-only task still returns its event
            # projection; normal command errors must remain visible to caller.
            pass
        task = self.legacy_adapter._kernel.get_task(task_id)
        projection['workspace_root'] = task['workspace_root']
        retained = self.legacy_adapter.historical_outputs(task_id)
        projection['historical_artifacts'] = retained
        projection['artifacts'] = [*projection.get('artifacts', []), *retained]
        projection['historical_decisions'] = []
        pointers = (task['state'].get('runner') or {}).get('academic_artifacts') or {}
        pointer = pointers.get('contribution_boundary_decision')
        if pointer:
            try:
                decision = self.legacy_adapter.legacy_document(task_id, pointer)
                projection['historical_decisions'].append({
                    'decision_id': 'legacy:contribution_boundary_decision', 'source': 'legacy_runner',
                    'historical': True, 'accepted': decision.get('accepted'),
                    'confirmed_at': decision.get('confirmed_at'),
                    'candidates': decision.get('candidates', []), 'decisions': decision.get('decisions', [])})
            except (OSError, ContractError, KeyError, TypeError, ValueError):
                pass
        projection['effective_stage'] = projection.get('stage', 'intake')
        projection['stage_source'] = 'domain_events'
        projection['stage_mismatch'] = False
        projection['configuration_readiness'] = configuration_readiness(projection)
        # Present the real registered filenames instead of opaque type labels.
        # The Kernel verifies receipt bytes; transport URLs never accept paths.
        if projection.get("artifacts"):
            views = self.legacy_adapter._kernel.list_artifacts(task_id)
            receipts = {}
            for view in views:
                receipt = view["receipt"]
                receipts.setdefault((receipt.get("artifact_id"), receipt.get("sha256")), view)
            enriched = []
            for artifact in projection["artifacts"]:
                item = dict(artifact)
                view = receipts.get((item["artifact_id"], item["sha256"]))
                if item.get('source') == 'legacy_runner':
                    pass  # historical_outputs already checked descriptor and file hashes
                elif view:
                    receipt = view["receipt"]
                    item["filename"] = (receipt.get("metadata") or {}).get("filename") or Path(receipt["path"]).name
                    item["size_bytes"] = receipt["size_bytes"]
                    item["freshness"] = "stale" if item.get("stale") else view["freshness"]
                else:
                    item["freshness"] = "missing"
                item["bytes_verified"] = item.get('bytes_verified', False) if item.get('historical') else item["freshness"] == "fresh"
                if view and item["freshness"] == "stale":
                    try:
                        body = native_path(view["receipt"]["path"]).read_bytes()
                        item["bytes_verified"] = len(body) == item["size_bytes"] and hashlib.sha256(body).hexdigest() == item["sha256"]
                    except OSError:
                        pass
                item["historical"] = item["freshness"] != "fresh"
                preview_media = (item.get("media_type") or "").split(";", 1)[0].strip().lower()
                item["previewable"] = item["bytes_verified"] and preview_media in {
                    "application/pdf", "image/png", "image/jpeg", "image/gif", "image/webp",
                    "text/plain", "text/markdown"}
                route = f"/api/v1/tasks/{quote(task_id, safe='')}/artifacts/{quote(item['artifact_id'], safe='')}"
                query = "?version=historical" if item["historical"] else ""
                item["content_url"] = route + "/content" + query if item["previewable"] else None
                item["download_url"] = route + "/download" + query
                enriched.append(item)
            projection["artifacts"] = enriched
        # The old workbench's reference/current mapping workspace is a read-only
        # capability of the same Runner.  Expose it as an optional projection so
        # the new Web can reuse real comparison evidence without copying the
        # legacy plan or inventing a quality result.
        try:
            workspace = self.legacy_adapter._runner.project_figure_reference_workspace(
                task_id, actor={"actor_id": "business-read", "surface": "business"}
            )
            if isinstance(workspace, dict):
                workspace = dict(workspace)
                for plan_item in workspace.get("plans", []):
                    plan = plan_item.get("plan") if isinstance(plan_item, dict) else None
                    if not isinstance(plan, dict):
                        continue
                    references = plan.get("references")
                    if isinstance(references, list):
                        plan["references"] = [dict(reference) if isinstance(reference, dict) else reference
                                               for reference in references]
                    for reference in plan.get("references", []):
                        if isinstance(reference, dict) and reference.get("preview_descriptor_id"):
                            reference["content_url"] = (
                                f"/api/v1/tasks/{quote(task_id, safe='')}/figure-references/"
                                f"{quote(reference['preview_descriptor_id'], safe='')}/content"
                            )
                projection["figure_reference_workspace"] = workspace
        except (AttributeError, ContractError, KeyError, TypeError, ValueError):
            # A task without a current verified figure workspace stays honestly
            # empty; old/stale plans must never be presented as current evidence.
            projection["figure_reference_workspace"] = {
                "task_id": task_id, "revision": None, "plans": [],
                "final_mappings": [], "read_only": True,
                "external_action_authorized": False,
            }
        from .delivery_manifest import build_delivery_manifest
        # Legacy progress may be shown separately; it cannot override current readiness.
        manifest_input = {**projection, 'legacy_runner': {}, 'runner_delivery_package': None}
        projection["delivery_manifest"] = build_delivery_manifest(manifest_input)
        # Expose the stable Skill/Web file handoff.  Refreshing this derived
        # view on read also covers legacy tasks created before the bridge was
        # installed, without changing the event authority.
        try:
            legacy_task = self.legacy_adapter._kernel.get_task(task_id)
            bridge = export_workflow_files(legacy_task, projection, legacy_task["workspace_root"])
            projection["skill_bridge"] = bridge
        except (OSError, TypeError, ValueError, KeyError, TaskNotFoundError):
            projection["skill_bridge"] = {
                "directory": None, "files": [],
                "stage": projection.get("effective_stage") or projection.get("stage"),
                "updated_at": None,
            }
        return projection

    def list_tasks(self, *, limit: int = 30) -> list[dict[str, Any]]:
        """Recent public tasks only; reuse domain history and Kernel titles."""
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 100:
            raise DomainError("validation_failed", "任务列表数量必须在 1–100 之间。", category="validation")
        with closing(sqlite3.connect(self.event_store.database_path)) as connection:
            rows = connection.execute(
                "SELECT p.projection_json, MAX(c.created_at) FROM task_projections p "
                "JOIN domain_commands c ON c.task_id=p.task_id "
                "GROUP BY p.task_id ORDER BY MAX(c.created_at) DESC, p.task_id LIMIT ?", (limit,)
            ).fetchall()
        result = []
        for raw, updated_at in rows:
            task = json.loads(raw)
            try:
                kernel_task = self.legacy_adapter._kernel.get_task(task["task_id"])
                title = kernel_task["title"]
                description = kernel_task.get("description") or f"围绕“{title}”的 PaperSpine 论文任务"
            except TaskNotFoundError:
                title = task["task_id"]
                description = "任务简介暂不可用"
            result.append({"task_id": task["task_id"], "title": title, "description": description, "task_version": task["task_version"],
                           "status": task["status"], "stage": task.get("stage", "intake"), "updated_at": updated_at})
        return result

    def read_artifact(self, task_id: str, artifact_id: str, *, allow_historical: bool = False) -> tuple[str, bytes]:
        """Keep download errors within the same public core boundary."""
        try:
            if allow_historical and artifact_id.startswith('legacy:'):
                from .p7_artifact_import import read_source
                historical = next(item for item in self.legacy_adapter.historical_outputs(task_id)
                                  if item['artifact_id'] == artifact_id)
                body, filename = read_source(self.legacy_adapter._kernel, task_id, None, historical['relative_path'])
                if hashlib.sha256(body).hexdigest() != historical['sha256']:
                    raise ContractError('historical output changed while reading')
                return filename, body
            task = self.event_store.projection(task_id) or {}
            artifact = next((item for item in task.get("artifacts", [])
                             if item["artifact_id"] == artifact_id and (allow_historical or not item.get("stale"))), None)
            if artifact is None:
                raise ValueError("Artifact is not published in this task")
            path = self.legacy_adapter.artifact_path(task_id, artifact_id,
                expected_sha256=artifact["sha256"], allow_historical=allow_historical)
            body = native_path(path).read_bytes()
            if hashlib.sha256(body).hexdigest() != artifact["sha256"]:
                raise ValueError("Artifact changed while reading")
            view = next(view for view in self.legacy_adapter._kernel.list_artifacts(task_id)
                        if (allow_historical or view["freshness"] == "fresh") and view["receipt"]["artifact_id"] == artifact_id
                        and view["receipt"]["sha256"] == artifact["sha256"])
            filename = (view["receipt"].get("metadata") or {}).get("filename") or path.name
            return filename, body
        except Exception:
            raise DomainError("effect_failed", "暂时无法读取论文文件，请重试下载。", category="effect",
                              task_id=task_id, retryable=True,
                              details={"operation": "download", "next_action": "retry_download"}) from None

    def read_artifact_preview(self, task_id: str, artifact_id: str, *, allow_historical: bool = False) -> tuple[str, bytes, str]:
        """Only inert, registered reader formats may be served inline."""
        task = self.event_store.projection(task_id) or {}
        artifact = next((item for item in task.get("artifacts", []) if item["artifact_id"] == artifact_id), {})
        if allow_historical and artifact_id.startswith('legacy:'):
            artifact = next((item for item in self.legacy_adapter.historical_outputs(task_id)
                             if item['artifact_id'] == artifact_id), {})
        media = (artifact.get("media_type") or "").split(";", 1)[0].strip().lower()
        text_preview = media in {"text/plain", "text/markdown"}
        signatures = {"application/pdf": b"%PDF-", "image/png": b"\x89PNG\r\n\x1a\n",
                      "image/jpeg": b"\xff\xd8\xff", "image/gif": b"GIF", "image/webp": b"RIFF"}
        if media not in signatures and not text_preview:
            raise DomainError("validation_failed", "此格式只支持下载，不提供页面内预览。", category="validation")
        # Previewing a giant registered file must not allocate it in the Web
        # process. Large sources remain separately downloadable.
        with self.legacy_adapter._kernel.store.read_connection() as connection:
            row = connection.execute("SELECT receipt_json FROM artifacts WHERE task_id=? AND artifact_id=? ORDER BY rowid DESC LIMIT 1",
                                     (task_id, artifact_id)).fetchone()
        if row and json.loads(row[0]).get("size_bytes", 0) > 64 * 1024 * 1024:
            raise DomainError("validation_failed", "文件超过 64 MiB，请下载后在本机查看。", category="validation")
        filename, body = self.read_artifact(task_id, artifact_id, allow_historical=allow_historical)
        if text_preview:
            # Reports are inert text, never rendered as HTML or active Markdown.
            # Keep the same registered-byte/version boundary as image/PDF previews.
            try:
                body.decode("utf-8-sig")
            except UnicodeDecodeError:
                raise DomainError("validation_failed", "文本预览需要 UTF-8 编码，请下载原文件或重新导出 UTF-8 版本。",
                                  category="validation") from None
            if b"\x00" in body:
                raise DomainError("validation_failed", "文件包含非文本字节，请下载后查看。", category="validation")
            return filename, body, "text/plain; charset=utf-8"
        if not body.startswith(signatures[media]) or (media == "image/webp" and body[8:12] != b"WEBP"):
            raise DomainError("validation_failed", "文件字节与登记的预览格式不一致。", category="validation")
        return filename, body, media

    def list_task_events(self, task_id: str, *, after_sequence: int = 0) -> list[dict[str, Any]]:
        """Read ordered events without introducing a facade-owned projection."""
        if not isinstance(after_sequence, int) or isinstance(after_sequence, bool) or after_sequence < 0:
            raise DomainError(
                "validation_failed", "after_sequence must be a non-negative integer.",
                category="validation", task_id=task_id,
            )
        events = self.event_store.events(task_id)
        if not events and self.event_store.projection(task_id) is None:
            raise DomainError(
                "not_found", "The domain task does not exist.", category="missing",
                task_id=task_id,
            )
        return [event for event in events if event["sequence"] > after_sequence]

    def list_decisions(self, task_id: str) -> list[dict[str, Any]]:
        return list(self.get_task(task_id).get("decisions", []))

    def capabilities(self) -> dict[str, Any]:
        return {
            "contract": "paperspine.capabilities", "protocol_version": "1.0",
            "schema_versions": ["1.0", "1.1"],
            "commands": ["OpenTask", "AuthorizeMaterials", "CommitMilestone", "BindEvidence",
                         "PublishArtifact", "RequestDecision", "ResolveDecision", "SubmitReview",
                         "ResolveFinding", "PrepareDelivery", "SaveConfiguration", "RequestRevision"],
            "resources": ["summary", "materials", "evidence", "manuscript", "review", "delivery", "skill_bridge"],
            "event_types": ["task.opened", "materials.authorized", "milestone.committed",
                            "evidence.bound", "artifact.published", "decision.required",
                            "decision.resolved", "review.submitted", "finding.resolved", "delivery.ready", "task.failed", "configuration.saved", "revision.requested"],
            "features": {"sse_resume": True, "persistent_decisions": True, "external_actions": False,
                         "safe_operation_recovery": True, "skill_bridge_files": True,
                         "same_task_feedback": True},
        }


def _reject_untrusted_identity(request: Mapping[str, Any]) -> None:
    forbidden = {"actor", "principal", "actor_id", "authority", "session_id"} & set(request)
    if forbidden:
        raise DomainError(
            "forbidden", "Principal fields must come from trusted facade context.",
            category="authorization", task_id=request.get("task_id"),
            command_id=request.get("command_id"), details={"rejected_fields": sorted(forbidden)},
        )


def agent_open_task(
    service: ApplicationService,
    request: Mapping[str, Any],
    *,
    principal_id: str,
) -> dict[str, Any]:
    """Translate a trusted Agent host call into frozen P0 ``OpenTask``."""
    _reject_untrusted_identity(request)
    command = {
        "contract": "paperspine.domain-command",
        "schema_version": request.get("schema_version"),
        "command_id": request.get("command_id"),
        "task_id": request.get("task_id"),
        "expected_version": request.get("expected_version"),
        "command_type": "OpenTask",
        "actor": {"actor_id": principal_id, "surface": "agent", "authority": "host_agent"},
        "payload": request.get("payload"),
        "external_action_authorized": False,
    }
    return service.execute(command)


def agent_request_decision(
    service: ApplicationService, request: Mapping[str, Any], *, principal_id: str
) -> dict[str, Any]:
    """Allow an Agent to request, but never resolve, a user decision."""
    _reject_untrusted_identity(request)
    return service.execute({
        "contract": "paperspine.domain-command",
        "schema_version": request.get("schema_version"),
        "command_id": request.get("command_id"),
        "task_id": request.get("task_id"),
        "expected_version": request.get("expected_version"),
        "command_type": "RequestDecision",
        "actor": {"actor_id": principal_id, "surface": "agent", "authority": "host_agent"},
        "payload": request.get("payload"),
        "external_action_authorized": False,
    })


def agent_execute(
    service: ApplicationService, request: Mapping[str, Any], *, principal_id: str,
    command_type: str, reviewer: bool = False,
) -> dict[str, Any]:
    """Translate one P4 Agent/Reviewer write into the shared command path."""
    _reject_untrusted_identity(request)
    if command_type == "ResolveDecision":
        raise DomainError("forbidden", "Agents cannot resolve user decisions.",
                          category="authorization", task_id=request.get("task_id"),
                          command_id=request.get("command_id"))
    if command_type == "RequestRevision":
        raise DomainError("forbidden", "Agents cannot submit user revision feedback.",
                          category="authorization", task_id=request.get("task_id"),
                          command_id=request.get("command_id"))
    return service.execute({
        "contract": "paperspine.domain-command", "schema_version": request.get("schema_version"),
        "command_id": request.get("command_id"), "task_id": request.get("task_id"),
        "expected_version": request.get("expected_version"), "command_type": command_type,
        "actor": {"actor_id": principal_id,
                  "surface": "reviewer" if reviewer else "agent",
                  "authority": "independent_reviewer" if reviewer else "host_agent"},
        "payload": request.get("payload"), "external_action_authorized": False,
    })


def business_open_task(
    service: ApplicationService,
    request: Mapping[str, Any],
    *,
    principal_id: str,
    session_id: str,
) -> dict[str, Any]:
    """Translate a trusted authenticated business call into the same command."""
    _reject_untrusted_identity(request)
    payload = request.get("payload")
    # The historical rich workbench posts ``title``/``host`` at the top level
    # while the P0 domain contract wraps them in an explicit OpenTask payload.
    # Normalize that legacy shape at the facade boundary so both workbenches
    # use the same application service and event stream.  Material roots are
    # intentionally handled by the Runner materials command afterwards; an
    # OpenTask must not silently authorize a filesystem path.
    if payload is None and any(key in request for key in ("title", "host", "materials_roots")):
        payload = {
            "mode": "open",
            "title": request.get("title") or "Untitled PaperSpine5 task",
        }
        if request.get("description") is not None:
            payload["description"] = request["description"]
    if not isinstance(payload, Mapping):
        raise DomainError(
            "validation_failed", "OpenTask 需要 payload.mode，可选 title 和 description。",
            category="validation", command_id=request.get("command_id"),
        )
    requested_task_id = payload.get("requested_task_id") if isinstance(payload, Mapping) else None
    command_id = request.get("command_id")
    derived_task_id = (
        f"task-{hashlib.sha256(command_id.encode('utf-8')).hexdigest()[:32]}"
        if isinstance(command_id, str) and command_id
        else None
    )
    command = {
        "contract": "paperspine.domain-command",
        "schema_version": P0_SCHEMA_VERSION,
        "command_id": command_id,
        "task_id": request.get("task_id") or requested_task_id or derived_task_id,
        # Legacy browser creates predate optimistic concurrency and omit the
        # field; a new task always starts at version zero.
        "expected_version": request.get("expected_version", 0),
        "command_type": "OpenTask",
        "actor": {
            "actor_id": principal_id,
            "surface": "business",
            "authority": "authenticated_user",
            "session_id": session_id,
        },
        "payload": payload,
        "external_action_authorized": False,
    }
    return service.execute(command)


def business_request_decision(
    service: ApplicationService, request: Mapping[str, Any], *, principal_id: str,
    session_id: str,
) -> dict[str, Any]:
    _reject_untrusted_identity(request)
    return service.execute({
        "contract": "paperspine.domain-command", "schema_version": P0_SCHEMA_VERSION,
        "command_id": request.get("command_id"), "task_id": request.get("task_id"),
        "expected_version": request.get("expected_version"), "command_type": "RequestDecision",
        "actor": {"actor_id": principal_id, "surface": "business",
                  "authority": "authenticated_user", "session_id": session_id},
        "payload": request.get("payload"), "external_action_authorized": False,
    })


def business_resolve_decision(
    service: ApplicationService, request: Mapping[str, Any], *, principal_id: str,
    session_id: str,
) -> dict[str, Any]:
    """Resolve a decision only from trusted authenticated business context."""
    _reject_untrusted_identity(request)
    return service.execute({
        "contract": "paperspine.domain-command", "schema_version": P0_SCHEMA_VERSION,
        "command_id": request.get("command_id"), "task_id": request.get("task_id"),
        "expected_version": request.get("expected_version"), "command_type": "ResolveDecision",
        "actor": {"actor_id": principal_id, "surface": "business",
                  "authority": "authenticated_user", "session_id": session_id},
        "payload": request.get("payload"), "external_action_authorized": False,
    })


def business_execute(
    service: ApplicationService, request: Mapping[str, Any], *, principal_id: str,
    session_id: str, command_type: str,
) -> dict[str, Any]:
    """Translate a non-OpenTask business write into the shared command path."""
    _reject_untrusted_identity(request)
    # RequestRevision was added in the v1.1 contract.  The browser feedback
    # bridge predates that contract and intentionally sends only the business
    # payload; normalize that one command here so the user-facing revision
    # path remains small and does not require callers to know schema plumbing.
    schema_version = request.get("schema_version")
    if command_type == "RequestRevision" and schema_version is None:
        schema_version = "1.1"
    return service.execute({
        "contract": "paperspine.domain-command", "schema_version": schema_version or P0_SCHEMA_VERSION,
        "command_id": request.get("command_id"), "task_id": request.get("task_id"),
        "expected_version": request.get("expected_version"), "command_type": command_type,
        **({"expected_revision": request["expected_revision"]} if "expected_revision" in request else {}),
        "actor": {"actor_id": principal_id, "surface": "business",
                  "authority": "authenticated_user", "session_id": session_id},
        "payload": request.get("payload"), "external_action_authorized": False,
    })


def reviewer_execute(
    service: ApplicationService, request: Mapping[str, Any], *, reviewer_id: str,
) -> dict[str, Any]:
    """Translate a review endpoint authenticated as an independent reviewer."""
    _reject_untrusted_identity(request)
    return service.execute({
        "contract": "paperspine.domain-command", "schema_version": request.get("schema_version", P0_SCHEMA_VERSION),
        "command_id": request.get("command_id"), "task_id": request.get("task_id"),
        "expected_version": request.get("expected_version"), "command_type": "SubmitReview",
        "actor": {"actor_id": reviewer_id, "surface": "reviewer",
                  "authority": "independent_reviewer"},
        "payload": request.get("payload"), "external_action_authorized": False,
    })
