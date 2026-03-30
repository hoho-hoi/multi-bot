from dataclasses import dataclass

from shared_contracts import IssueWorkItemContract


@dataclass(frozen=True, slots=True)
class WorkerRuntimeStartupReport:
    """Summarizes worker-runtime bootstrap readiness.

    Attributes:
        issue_identifier: Repository-qualified issue identifier.
        next_action_summary: Human-readable summary for the next execution step.
    """

    issue_identifier: str
    next_action_summary: str


def build_worker_runtime_startup_report(
    issue_work_item_contract: IssueWorkItemContract,
) -> WorkerRuntimeStartupReport:
    """Builds a startup report for worker-runtime execution.

    Args:
        issue_work_item_contract: Shared contract for an issue-driven work item.

    Returns:
        A minimal worker-runtime startup report.
    """

    issue_identifier = issue_work_item_contract.to_issue_identifier()
    next_action_summary = (
        "Worker runtime is ready to execute issue "
        f"{issue_identifier} titled '{issue_work_item_contract.issue_title}'."
    )
    return WorkerRuntimeStartupReport(
        issue_identifier=issue_identifier,
        next_action_summary=next_action_summary,
    )
