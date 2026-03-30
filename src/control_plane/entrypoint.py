from dataclasses import dataclass
from enum import StrEnum

from shared_contracts import (
    EngineerExecutionWorkItemContract,
    EngineerJobInput,
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


class EngineerExecutionStartStatus(StrEnum):
    """Enumerates outcomes for starting engineer execution."""

    READY = "READY"
    INPUT_REQUIRED = "INPUT_REQUIRED"
    INVALID_INPUT = "INVALID_INPUT"
    UNSUPPORTED_STATE = "UNSUPPORTED_STATE"


@dataclass(frozen=True, slots=True)
class EngineerExecutionStartResult:
    """Represents whether engineer execution can start from backlog-ready inputs.

    Attributes:
        status: High-level result for caller-side branching.
        current_state: Workflow state observed before the start decision.
        next_state: Workflow state after interpreting the result.
        summary_message: Human-readable summary of the start decision.
        missing_information_items: Missing inputs required before execution can start.
        work_item_contract: Engineer execution work item when status is `READY`.
    """

    status: EngineerExecutionStartStatus
    current_state: RequirementDiscoverySessionState
    next_state: RequirementDiscoverySessionState
    summary_message: str
    missing_information_items: tuple[str, ...] = ()
    work_item_contract: EngineerExecutionWorkItemContract | None = None

    def __post_init__(self) -> None:
        """Validates engineer execution start result consistency."""

        if not self.summary_message.strip():
            raise ValueError("summary_message must not be empty.")
        if not isinstance(self.current_state, RequirementDiscoverySessionState):
            raise ValueError("current_state must be a RequirementDiscoverySessionState value.")
        if not isinstance(self.next_state, RequirementDiscoverySessionState):
            raise ValueError("next_state must be a RequirementDiscoverySessionState value.")
        if any(not missing_item.strip() for missing_item in self.missing_information_items):
            raise ValueError("missing_information_items must not contain empty values.")
        if len(set(self.missing_information_items)) != len(self.missing_information_items):
            raise ValueError("missing_information_items must not contain duplicate values.")

        if self.status is EngineerExecutionStartStatus.READY:
            if self.work_item_contract is None:
                raise ValueError("work_item_contract must be provided when status is READY.")
            if self.missing_information_items:
                raise ValueError("missing_information_items must be empty when status is READY.")
            if self.next_state is not RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING:
                raise ValueError(
                    "next_state must be STATE_ENGINEER_JOB_RUNNING when status is READY."
                )
            return

        if self.work_item_contract is not None:
            raise ValueError("work_item_contract must be empty unless status is READY.")

        if self.status is EngineerExecutionStartStatus.INPUT_REQUIRED:
            if not self.missing_information_items:
                raise ValueError(
                    "missing_information_items must not be empty when status is INPUT_REQUIRED."
                )
            if self.next_state is not RequirementDiscoverySessionState.IMPLEMENTATION_BACKLOG_READY:
                raise ValueError(
                    "next_state must be STATE_IMPLEMENTATION_BACKLOG_READY when status is "
                    "INPUT_REQUIRED."
                )
            return

        if self.missing_information_items:
            raise ValueError(
                "missing_information_items must be empty for INVALID_INPUT and UNSUPPORTED_STATE."
            )
        if self.status is EngineerExecutionStartStatus.INVALID_INPUT:
            if self.next_state is not RequirementDiscoverySessionState.IMPLEMENTATION_BACKLOG_READY:
                raise ValueError(
                    "next_state must be STATE_IMPLEMENTATION_BACKLOG_READY when status is "
                    "INVALID_INPUT."
                )
            return

        if self.next_state is not self.current_state:
            raise ValueError(
                "next_state must match current_state when status is UNSUPPORTED_STATE."
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


def start_engineer_execution(
    session_summary: RequirementDiscoverySessionSummary,
    issue_work_item_contract: IssueWorkItemContract | None,
    engineer_job_input: EngineerJobInput | None,
) -> EngineerExecutionStartResult:
    """Builds the engineer execution work item from backlog-ready inputs.

    Args:
        session_summary: Current delivery workflow session snapshot.
        issue_work_item_contract: Backlog-ready implementation issue metadata.
        engineer_job_input: Strict engineer job input prepared for the issue.

    Returns:
        A typed result describing whether engineer execution can start immediately.

    Example:
        result = start_engineer_execution(
            session_summary=session_summary,
            issue_work_item_contract=issue_work_item_contract,
            engineer_job_input=engineer_job_input,
        )
        if result.status is EngineerExecutionStartStatus.READY:
            assert result.work_item_contract is not None
    """

    current_state = session_summary.current_state
    if current_state is not RequirementDiscoverySessionState.IMPLEMENTATION_BACKLOG_READY:
        return EngineerExecutionStartResult(
            status=EngineerExecutionStartStatus.UNSUPPORTED_STATE,
            current_state=current_state,
            next_state=current_state,
            summary_message=(
                "Engineer execution start is not supported for workflow state "
                f"{current_state.value}."
            ),
        )

    missing_information_items: list[str] = []
    if issue_work_item_contract is None:
        missing_information_items.append("implementation issue work item contract")
    if engineer_job_input is None:
        missing_information_items.append("engineer job input")

    if missing_information_items:
        return EngineerExecutionStartResult(
            status=EngineerExecutionStartStatus.INPUT_REQUIRED,
            current_state=current_state,
            next_state=RequirementDiscoverySessionState.IMPLEMENTATION_BACKLOG_READY,
            summary_message=(
                "Engineer execution start requires backlog-ready issue metadata and strict "
                "engineer job input."
            ),
            missing_information_items=tuple(missing_information_items),
        )

    if issue_work_item_contract is None or engineer_job_input is None:
        raise ValueError("Engineer execution inputs must be available after validation.")

    try:
        work_item_contract = EngineerExecutionWorkItemContract.create_from_issue_and_job_input(
            issue_work_item_contract=issue_work_item_contract,
            engineer_job_input=engineer_job_input,
        )
    except ValueError as error:
        return EngineerExecutionStartResult(
            status=EngineerExecutionStartStatus.INVALID_INPUT,
            current_state=current_state,
            next_state=RequirementDiscoverySessionState.IMPLEMENTATION_BACKLOG_READY,
            summary_message=str(error),
        )

    issue_identifier = issue_work_item_contract.to_issue_identifier()
    return EngineerExecutionStartResult(
        status=EngineerExecutionStartStatus.READY,
        current_state=current_state,
        next_state=RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING,
        summary_message=(
            f"Prepared the engineer execution work item for backlog-ready issue {issue_identifier}."
        ),
        work_item_contract=work_item_contract,
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
