"""Read-only delivery manifest projection for the v1 business facade.

This deliberately does not mark a task ready or create a package.  It exposes
the evidence currently present so clients can explain why delivery is blocked.
"""
from __future__ import annotations

from typing import Any, Mapping

from .skill_bridge import configuration_readiness


def build_delivery_manifest(task: Mapping[str, Any]) -> dict[str, Any]:
    artifacts = [a for a in task.get("artifacts", []) if not a.get("stale")
                 and a.get("freshness", "fresh") == "fresh"]
    open_blocking = [f for f in task.get("findings", [])
                     if f.get("status") == "open" and f.get("severity") in {"blocking", "major"}]
    package = [a for a in artifacts if a.get("artifact_type") == "delivery_package"]
    # Research may begin with a question and collect public sources inside the
    # task workspace. Those files need no external-directory capability grant.
    # Published source notes/bibliography expose that evidence; they do not
    # replace the separate independent-review and delivery checks.
    research_sources = any(a.get("artifact_type") in {"research_note", "bibliography"}
                           for a in artifacts)
    runner = task.get("legacy_runner") or {}
    # During the P1/P2 migration the academic Runner can finish a paper while
    # the event projection still has no ``artifact.published`` rows.  A
    # terminal Runner package is already an accepted, hash-bound delivery
    # authority; expose that fact read-only instead of reporting a stale
    # event-only blocker.  The caller is still responsible for exposing the
    # hardened download route, which revalidates all bytes before streaming.
    runner_package_ready = (
        runner.get("task_status") == "completed"
        and runner.get("stage") == "target_package_ready"
        and bool(task.get("runner_delivery_package"))
    )
    configuration_ready = configuration_readiness(task)["ready"] or runner_package_ready
    checks = {
        "fresh_package": bool(package) or runner_package_ready,
        "configuration_saved": configuration_ready,
        "materials_available": (bool((task.get("material_inventory") or {}).get("entries"))
                                or research_sources or runner_package_ready),
        "run_contract_current": runner.get("run_contract_fresh", True),
        "materials_current": runner.get("material_inventory_fresh", True),
        "user_choices_resolved": not any(d.get("status") == "pending" and not d.get("stale")
                                         for d in task.get("decisions", [])),
        "blocking_findings_closed": not open_blocking,
        "delivery_recorded": ((task.get("delivery") or {}).get("local_download_ready") is True
                              and not (task.get("delivery") or {}).get("stale", False)) or runner_package_ready,
    }
    labels = {"fresh_package": "尚无当前有效的交付包", "configuration_saved": "论文配置尚未保存或需重新核对",
              "materials_available": "尚无可用材料或研究来源", "run_contract_current": "执行配置尚未更新到当前修订",
              "materials_current": "材料盘点不是当前修订", "user_choices_resolved": "还有待用户确认的选择",
              "blocking_findings_closed": "还有阻塞审核问题", "delivery_recorded": "尚未完成正式的本地交付检查"}
    return {
        "schema_version": "1.0",
        "task_id": task.get("task_id"),
        "task_version": task.get("task_version"),
        "artifact_ids": [a.get("artifact_id") for a in artifacts],
        "artifact_types": sorted({a.get("artifact_type") for a in artifacts if a.get("artifact_type")}),
        "open_blocking_finding_ids": [f.get("finding_id") for f in open_blocking],
        "open_blocking_findings": [{"review_id": f.get("review_id"), "finding_id": f.get("finding_id")}
                                  for f in open_blocking],
        "package_artifact_id": (package[-1].get("artifact_id") if package
                                 else ((task.get("runner_delivery_package") or {}).get("artifact_id")
                                       if runner_package_ready else None)),
        "ready": all(checks.values()),
        "checks": checks,
        "blockers": [labels[name] for name, passed in checks.items() if not passed],
        "submission_ready": False,
        "source": "legacy_runner" if runner_package_ready else "event_projection",
    }
