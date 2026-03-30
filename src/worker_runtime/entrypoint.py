from dataclasses import dataclass
from enum import StrEnum

from shared_contracts import (
    IssueWorkItemContract,
    ProviderName,
    RequirementDiscoverySessionState,
    RequirementDiscoverySessionSummary,
    RequirementDiscoveryWorkItemContract,
    RequirementDocumentUpdateDraftResult,
    WorkerRoleName,
    build_requirement_document_update_draft_result,
)


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


class RequirementDiscoveryBootstrapFailureCode(StrEnum):
    """Enumerates failure categories for requirement discovery bootstrap."""

    INVALID_INPUT = "INVALID_INPUT"
    UNSUPPORTED_ROLE = "UNSUPPORTED_ROLE"
    UNSUPPORTED_PROVIDER = "UNSUPPORTED_PROVIDER"
    UNSUPPORTED_STATE = "UNSUPPORTED_STATE"


@dataclass(frozen=True, slots=True)
class RequirementDiscoveryBootstrapSuccess:
    """Represents a successful worker-runtime bootstrap response.

    Attributes:
        work_item_contract: Shared payload received from control-plane.
        updated_session_summary: Session summary to persist after the bootstrap step.
        architect_response_message: Minimal Architect-facing response text.
        document_update_draft_result: Typed summary of candidate `docs/` updates.
    """

    work_item_contract: RequirementDiscoveryWorkItemContract
    updated_session_summary: RequirementDiscoverySessionSummary
    architect_response_message: str
    document_update_draft_result: RequirementDocumentUpdateDraftResult


@dataclass(frozen=True, slots=True)
class RequirementDiscoveryBootstrapFailure:
    """Represents an explicit bootstrap failure for caller-side branching.

    Attributes:
        current_state: Current requirement discovery workflow state.
        failure_code: Stable classification for safe failure handling.
        error_message: Human-readable failure reason.
        is_retryable: Whether retrying automatically is safe.
    """

    current_state: RequirementDiscoverySessionState
    failure_code: RequirementDiscoveryBootstrapFailureCode
    error_message: str
    is_retryable: bool


RequirementDiscoveryBootstrapResult = (
    RequirementDiscoveryBootstrapSuccess | RequirementDiscoveryBootstrapFailure
)


def execute_requirement_discovery_work_item(
    work_item_contract: RequirementDiscoveryWorkItemContract,
) -> RequirementDiscoveryBootstrapResult:
    """Executes the minimal worker-runtime bootstrap for requirement discovery.

    Args:
        work_item_contract: Shared work item prepared by the control-plane.

    Returns:
        A success result with an Architect-facing bootstrap response, or a failure
        result that the caller can inspect for safe branching.
    """

    if work_item_contract.role_name is not WorkerRoleName.ARCHITECT:
        return RequirementDiscoveryBootstrapFailure(
            current_state=work_item_contract.session_summary.current_state,
            failure_code=RequirementDiscoveryBootstrapFailureCode.UNSUPPORTED_ROLE,
            error_message=(
                "role_name "
                f"{work_item_contract.role_name.value} is not supported for requirement "
                "discovery bootstrap."
            ),
            is_retryable=False,
        )

    if work_item_contract.provider_name is not ProviderName.CURSOR:
        return RequirementDiscoveryBootstrapFailure(
            current_state=work_item_contract.session_summary.current_state,
            failure_code=RequirementDiscoveryBootstrapFailureCode.UNSUPPORTED_PROVIDER,
            error_message=(
                "provider_name "
                f"{work_item_contract.provider_name.value} is not supported for "
                "requirement discovery bootstrap."
            ),
            is_retryable=False,
        )

    session_summary = work_item_contract.session_summary
    if session_summary.current_state is RequirementDiscoverySessionState.ISSUE_READY:
        return _bootstrap_issue_ready_requirement_discovery(work_item_contract)

    if session_summary.current_state is RequirementDiscoverySessionState.DISCOVERY_IN_PROGRESS:
        return _bootstrap_in_progress_requirement_discovery(work_item_contract)

    return RequirementDiscoveryBootstrapFailure(
        current_state=session_summary.current_state,
        failure_code=RequirementDiscoveryBootstrapFailureCode.UNSUPPORTED_STATE,
        error_message=(
            "current_state "
            f"{session_summary.current_state.value} is not supported for requirement "
            "discovery bootstrap."
        ),
        is_retryable=False,
    )


def _bootstrap_issue_ready_requirement_discovery(
    work_item_contract: RequirementDiscoveryWorkItemContract,
) -> RequirementDiscoveryBootstrapSuccess:
    """Builds the initial Architect bootstrap response for a ready issue."""

    session_summary = work_item_contract.session_summary
    issue_contract = session_summary.issue_contract
    document_update_draft_result = build_requirement_document_update_draft_result(session_summary)
    updated_session_summary = RequirementDiscoverySessionSummary(
        issue_contract=issue_contract,
        current_state=RequirementDiscoverySessionState.DISCOVERY_IN_PROGRESS,
        latest_prompt_summary=(
            "Collect the project goal, constraints, and success criteria needed to "
            "refine the requirement documents."
        ),
    )
    architect_response_message = (
        "Architect bootstrap is ready for issue "
        f"#{issue_contract.issue_number}, '{issue_contract.issue_title}'. "
        "Please share the project goal, constraints, and success criteria that "
        "should drive the requirement documents."
    )
    return RequirementDiscoveryBootstrapSuccess(
        work_item_contract=work_item_contract,
        updated_session_summary=updated_session_summary,
        architect_response_message=architect_response_message,
        document_update_draft_result=document_update_draft_result,
    )


def _bootstrap_in_progress_requirement_discovery(
    work_item_contract: RequirementDiscoveryWorkItemContract,
) -> RequirementDiscoveryBootstrapResult:
    """Builds the follow-up Architect bootstrap response for an active session."""

    session_summary = work_item_contract.session_summary
    latest_prompt_summary = session_summary.latest_prompt_summary
    if latest_prompt_summary is None:
        return RequirementDiscoveryBootstrapFailure(
            current_state=session_summary.current_state,
            failure_code=RequirementDiscoveryBootstrapFailureCode.INVALID_INPUT,
            error_message=(
                "latest_prompt_summary must be provided when current_state is "
                "STATE_REQUIREMENT_DISCOVERY_IN_PROGRESS."
            ),
            is_retryable=False,
        )

    issue_contract = session_summary.issue_contract
    document_update_draft_result = build_requirement_document_update_draft_result(session_summary)
    updated_session_summary = RequirementDiscoverySessionSummary(
        issue_contract=issue_contract,
        current_state=RequirementDiscoverySessionState.DISCOVERY_IN_PROGRESS,
        latest_comment_contract=session_summary.latest_comment_contract,
        latest_prompt_summary=latest_prompt_summary,
    )
    architect_response_message = (
        "Architect bootstrap is continuing for issue "
        f"#{issue_contract.issue_number}, '{issue_contract.issue_title}'. "
        f"Latest user intent: {latest_prompt_summary}"
    )
    return RequirementDiscoveryBootstrapSuccess(
        work_item_contract=work_item_contract,
        updated_session_summary=updated_session_summary,
        architect_response_message=architect_response_message,
        document_update_draft_result=document_update_draft_result,
    )
