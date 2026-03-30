from dataclasses import dataclass

from shared_contracts import IssueWorkItemContract


@dataclass(frozen=True, slots=True)
class ControlPlaneStartupReport:
    """Summarizes control-plane bootstrap readiness.

    Attributes:
        issue_identifier: Repository-qualified issue identifier.
        next_action_summary: Human-readable summary for the next orchestration step.
    """

    issue_identifier: str
    next_action_summary: str


def build_control_plane_startup_report(
    issue_work_item_contract: IssueWorkItemContract,
) -> ControlPlaneStartupReport:
    """Builds a startup report for control-plane orchestration.

    Args:
        issue_work_item_contract: Shared contract for an issue-driven work item.

    Returns:
        A minimal control-plane startup report.
    """

    issue_identifier = issue_work_item_contract.to_issue_identifier()
    next_action_summary = (
        "Control plane is ready to coordinate issue "
        f"{issue_identifier} titled '{issue_work_item_contract.issue_title}'."
    )
    return ControlPlaneStartupReport(
        issue_identifier=issue_identifier,
        next_action_summary=next_action_summary,
    )
