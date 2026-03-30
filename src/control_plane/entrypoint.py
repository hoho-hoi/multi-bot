from dataclasses import dataclass
from enum import StrEnum

from shared_contracts import (
    IssueWorkItemContract,
    RequirementDiscoverySessionState,
    RequirementDiscoverySessionSummary,
    RequirementDiscoveryWorkItemContract,
)


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


class RequirementDiscoveryOrchestrationFailureCode(StrEnum):
    """Enumerates failure categories for requirement discovery orchestration."""

    INVALID_INPUT = "INVALID_INPUT"
    UNSUPPORTED_STATE = "UNSUPPORTED_STATE"


@dataclass(frozen=True, slots=True)
class RequirementDiscoveryOrchestrationSuccess:
    """Represents a successful requirement discovery orchestration decision.

    Attributes:
        work_item_contract: Shared payload ready for worker-runtime execution.
        current_state: Current requirement discovery workflow state.
        next_action_summary: Human-readable summary for the next orchestration step.
    """

    work_item_contract: RequirementDiscoveryWorkItemContract
    current_state: RequirementDiscoverySessionState
    next_action_summary: str


@dataclass(frozen=True, slots=True)
class RequirementDiscoveryOrchestrationFailure:
    """Represents an explicit orchestration failure for the caller.

    Attributes:
        current_state: Current requirement discovery workflow state.
        failure_code: Stable classification for caller-side branching.
        error_message: Human-readable failure reason.
        is_retryable: Whether an automated retry is safe to attempt.
    """

    current_state: RequirementDiscoverySessionState
    failure_code: RequirementDiscoveryOrchestrationFailureCode
    error_message: str
    is_retryable: bool


RequirementDiscoveryOrchestrationResult = (
    RequirementDiscoveryOrchestrationSuccess | RequirementDiscoveryOrchestrationFailure
)


def orchestrate_requirement_discovery_session(
    session_summary: RequirementDiscoverySessionSummary,
) -> RequirementDiscoveryOrchestrationResult:
    """Builds the next worker-runtime work item for requirement discovery.

    Args:
        session_summary: Current requirement discovery session snapshot.

    Returns:
        A success result with a worker-runtime work item, or a failure result that
        the caller can inspect to decide whether retry or user confirmation is needed.
    """

    if session_summary.current_state is RequirementDiscoverySessionState.ISSUE_READY:
        issue_identifier = session_summary.issue_contract.to_issue_identifier()
        issue_work_item_contract = _build_issue_work_item_contract(session_summary)
        return RequirementDiscoveryOrchestrationSuccess(
            work_item_contract=RequirementDiscoveryWorkItemContract(
                issue_work_item_contract=issue_work_item_contract,
                session_summary=session_summary,
            ),
            current_state=session_summary.current_state,
            next_action_summary=(
                "Start requirement discovery for issue "
                f"{issue_identifier} titled '{issue_work_item_contract.issue_title}'."
            ),
        )

    if session_summary.current_state is RequirementDiscoverySessionState.DISCOVERY_IN_PROGRESS:
        latest_prompt_summary = session_summary.latest_prompt_summary
        if latest_prompt_summary is None:
            return RequirementDiscoveryOrchestrationFailure(
                current_state=session_summary.current_state,
                failure_code=RequirementDiscoveryOrchestrationFailureCode.INVALID_INPUT,
                error_message=(
                    "latest_prompt_summary must be provided when current_state is "
                    "STATE_REQUIREMENT_DISCOVERY_IN_PROGRESS."
                ),
                is_retryable=False,
            )

        issue_identifier = session_summary.issue_contract.to_issue_identifier()
        issue_work_item_contract = _build_issue_work_item_contract(session_summary)
        return RequirementDiscoveryOrchestrationSuccess(
            work_item_contract=RequirementDiscoveryWorkItemContract(
                issue_work_item_contract=issue_work_item_contract,
                session_summary=session_summary,
            ),
            current_state=session_summary.current_state,
            next_action_summary=(
                "Continue requirement discovery for issue "
                f"{issue_identifier} with latest user intent: {latest_prompt_summary}"
            ),
        )

    return RequirementDiscoveryOrchestrationFailure(
        current_state=session_summary.current_state,
        failure_code=RequirementDiscoveryOrchestrationFailureCode.UNSUPPORTED_STATE,
        error_message=(
            "current_state "
            f"{session_summary.current_state.value} is not supported for requirement "
            "discovery orchestration."
        ),
        is_retryable=False,
    )


def _build_issue_work_item_contract(
    session_summary: RequirementDiscoverySessionSummary,
) -> IssueWorkItemContract:
    """Builds the generic issue work item shared with worker-runtime."""

    issue_contract = session_summary.issue_contract
    return IssueWorkItemContract(
        repository_reference=issue_contract.repository_contract.repository_reference,
        issue_number=issue_contract.issue_number,
        issue_title=issue_contract.issue_title,
    )
