from dataclasses import dataclass
from enum import StrEnum

from control_plane import (
    EngineerExecutionStartResult,
    EngineerExecutionStartStatus,
    RequirementDiscoveryOrchestrationFailure,
    RequirementDiscoveryOrchestrationFailureCode,
    orchestrate_requirement_discovery_session,
    start_engineer_execution,
)
from shared_contracts import (
    EngineerExecutionFocus,
    EngineerExecutionWorkItemContract,
    EngineerJobInput,
    ImplementationBlockerResult,
    ImplementationPullRequestOpenResult,
    ImplementationPullRequestOpenStatus,
    IssueWorkItemContract,
    RequirementDiscoverySessionState,
    RequirementDiscoverySessionSummary,
    RequirementDocumentUpdateDraftResult,
    RequirementPullRequestOpenResult,
    RequirementPullRequestPreparationResult,
    build_implementation_pull_request_open_result,
)
from worker_runtime import (
    EngineerBlockerReportingPolicy,
    EngineerExecutionBootstrapFailure,
    EngineerExecutionBootstrapFailureCode,
    EngineerExecutionBootstrapSuccess,
    RequirementDiscoveryBootstrapFailure,
    RequirementDiscoveryBootstrapFailureCode,
    RequirementDiscoveryBootstrapSuccess,
    execute_engineer_execution_work_item,
    execute_requirement_discovery_work_item,
)


class RequirementDiscoveryIntegrationFailureStage(StrEnum):
    """Enumerates the stage that produced an integration failure."""

    CONTROL_PLANE = "CONTROL_PLANE"
    WORKER_RUNTIME = "WORKER_RUNTIME"


class EngineerExecutionIntegrationFailureStage(StrEnum):
    """Enumerates the stage that produced an engineer execution integration failure."""

    CONTROL_PLANE = "CONTROL_PLANE"
    WORKER_RUNTIME = "WORKER_RUNTIME"


@dataclass(frozen=True, slots=True)
class RequirementDiscoveryIntegrationFailureDetail:
    """Represents a classified integration failure for caller-side branching.

    Attributes:
        stage: Boundary that returned the failure.
        failure_code: Stable code preserved from the source boundary.
        error_message: Human-readable explanation of the failure.
        is_retryable: Whether automated retry is safe.
    """

    stage: RequirementDiscoveryIntegrationFailureStage
    failure_code: (
        RequirementDiscoveryOrchestrationFailureCode | RequirementDiscoveryBootstrapFailureCode
    )
    error_message: str
    is_retryable: bool


@dataclass(frozen=True, slots=True)
class EngineerExecutionIntegrationFailureDetail:
    """Represents a classified engineer execution integration failure.

    Attributes:
        stage: Boundary that returned the failure.
        failure_code: Stable stage-specific code preserved from the source boundary.
        error_message: Human-readable explanation of the failure.
        is_retryable: Whether automated retry is safe.
    """

    stage: EngineerExecutionIntegrationFailureStage
    failure_code: EngineerExecutionStartStatus | EngineerExecutionBootstrapFailureCode
    error_message: str
    is_retryable: bool

    def __post_init__(self) -> None:
        """Validates failure detail consistency."""

        if not self.error_message.strip():
            raise ValueError("error_message must not be empty.")

        if self.stage is EngineerExecutionIntegrationFailureStage.CONTROL_PLANE:
            if not isinstance(self.failure_code, EngineerExecutionStartStatus):
                raise ValueError(
                    "failure_code must be an EngineerExecutionStartStatus for "
                    "control-plane failures."
                )
            if self.failure_code is EngineerExecutionStartStatus.READY:
                raise ValueError(
                    "failure_code must not be READY for control-plane integration failures."
                )
            return

        if not isinstance(self.failure_code, EngineerExecutionBootstrapFailureCode):
            raise ValueError(
                "failure_code must be an EngineerExecutionBootstrapFailureCode for "
                "worker-runtime failures."
            )


@dataclass(frozen=True, slots=True)
class RequirementDiscoveryIntegrationResult:
    """Represents the end-to-end outcome for requirement discovery bootstrap.

    Attributes:
        architect_response_message: Architect-facing response text when bootstrap succeeds.
        document_update_draft_result: Typed summary of candidate `docs/` updates.
        pull_request_preparation_result: Typed readiness result for requirement PR preparation.
        pull_request_open_result: Typed result for requirement PR creation payload and state.
        updated_session_summary: Updated session summary when bootstrap succeeds.
        failure: Failure classification when orchestration or bootstrap fails.
    """

    architect_response_message: str | None
    document_update_draft_result: RequirementDocumentUpdateDraftResult | None
    pull_request_preparation_result: RequirementPullRequestPreparationResult | None
    pull_request_open_result: RequirementPullRequestOpenResult | None
    updated_session_summary: RequirementDiscoverySessionSummary | None
    failure: RequirementDiscoveryIntegrationFailureDetail | None

    @property
    def is_successful(self) -> bool:
        """Returns whether the integration call completed successfully."""

        return self.failure is None


@dataclass(frozen=True, slots=True)
class EngineerExecutionIntegrationResult:
    """Represents the end-to-end outcome for engineer execution bootstrap.

    Attributes:
        start_result: Control-plane start decision preserved for caller-side branching.
        engineer_response_message: Engineer-facing bootstrap response text when successful.
        execution_focus: Initial execution focus when engineer execution starts.
        blocker_reporting_policy: Typed fallback policy when implementation is blocked.
        failure: Failure classification when control-plane or worker-runtime fails.

    Example:
        result = start_engineer_execution_from_backlog_ready_issue(
            session_summary=session_summary,
            issue_work_item_contract=issue_work_item_contract,
            engineer_job_input=engineer_job_input,
        )
        if result.is_successful:
            assert result.next_state.value == "STATE_ENGINEER_JOB_RUNNING"
    """

    start_result: EngineerExecutionStartResult
    engineer_response_message: str | None
    execution_focus: EngineerExecutionFocus | None
    blocker_reporting_policy: EngineerBlockerReportingPolicy | None
    failure: EngineerExecutionIntegrationFailureDetail | None

    def __post_init__(self) -> None:
        """Validates integration result consistency."""

        if self.failure is None:
            if self.start_result.status is not EngineerExecutionStartStatus.READY:
                raise ValueError("start_result.status must be READY when integration succeeds.")
            if self.engineer_response_message is None:
                raise ValueError(
                    "engineer_response_message must be provided when integration succeeds."
                )
            if self.execution_focus is None:
                raise ValueError("execution_focus must be provided when integration succeeds.")
            if self.blocker_reporting_policy is None:
                raise ValueError(
                    "blocker_reporting_policy must be provided when integration succeeds."
                )
            return

        if self.engineer_response_message is not None:
            raise ValueError("engineer_response_message must be empty when integration fails.")
        if self.execution_focus is not None:
            raise ValueError("execution_focus must be empty when integration fails.")
        if self.blocker_reporting_policy is not None:
            raise ValueError("blocker_reporting_policy must be empty when integration fails.")

    @property
    def current_state(self) -> RequirementDiscoverySessionState:
        """Returns the workflow state observed before the start decision."""

        return self.start_result.current_state

    @property
    def next_state(self) -> RequirementDiscoverySessionState:
        """Returns the workflow state selected by the control-plane."""

        return self.start_result.next_state

    @property
    def summary_message(self) -> str:
        """Returns the preserved control-plane summary message."""

        return self.start_result.summary_message

    @property
    def missing_information_items(self) -> tuple[str, ...]:
        """Returns missing inputs preserved from the control-plane result."""

        return self.start_result.missing_information_items

    @property
    def work_item_contract(self) -> EngineerExecutionWorkItemContract | None:
        """Returns the validated engineer execution work item when available."""

        return self.start_result.work_item_contract

    @property
    def is_successful(self) -> bool:
        """Returns whether the integration call completed successfully."""

        return self.failure is None


def generate_requirement_discovery_architect_response(
    session_summary: RequirementDiscoverySessionSummary,
) -> RequirementDiscoveryIntegrationResult:
    """Generates the next Architect response for requirement discovery.

    This entrypoint keeps `control_plane` and `worker_runtime` decoupled while
    providing a single application-level result object for callers.

    Args:
        session_summary: Current requirement discovery session snapshot.

    Returns:
        An integration result containing the Architect response, updated session
        summary, and preserved failure classification when applicable.

    Example:
        summary = RequirementDiscoverySessionSummary.create_initial(issue_contract)
        result = generate_requirement_discovery_architect_response(summary)
        if result.is_successful:
            assert result.architect_response_message is not None
    """

    orchestration_result = orchestrate_requirement_discovery_session(session_summary)
    if isinstance(orchestration_result, RequirementDiscoveryOrchestrationFailure):
        return _build_orchestration_failure_result(orchestration_result)

    bootstrap_result = execute_requirement_discovery_work_item(
        orchestration_result.work_item_contract,
    )
    if isinstance(bootstrap_result, RequirementDiscoveryBootstrapFailure):
        return _build_bootstrap_failure_result(bootstrap_result)

    return _build_success_result(bootstrap_result)


def start_engineer_execution_from_backlog_ready_issue(
    *,
    session_summary: RequirementDiscoverySessionSummary,
    issue_work_item_contract: IssueWorkItemContract | None,
    engineer_job_input: EngineerJobInput | None,
) -> EngineerExecutionIntegrationResult:
    """Starts engineer execution through the application-layer entrypoint.

    This entrypoint keeps `control_plane` and `worker_runtime` decoupled while
    returning one strict result for success, caller-actionable control-plane
    failures, and worker-runtime bootstrap failures.

    Args:
        session_summary: Current delivery workflow session snapshot.
        issue_work_item_contract: Backlog-ready implementation issue metadata.
        engineer_job_input: Strict engineer job input prepared for the issue.

    Returns:
        An integration result containing the running-state transition,
        execution focus, blocker reporting policy, and preserved failure
        classification when applicable.

    Example:
        result = start_engineer_execution_from_backlog_ready_issue(
            session_summary=session_summary,
            issue_work_item_contract=issue_work_item_contract,
            engineer_job_input=engineer_job_input,
        )
        if result.is_successful:
            assert result.execution_focus is not None
    """

    start_result = start_engineer_execution(
        session_summary=session_summary,
        issue_work_item_contract=issue_work_item_contract,
        engineer_job_input=engineer_job_input,
    )
    if start_result.status is not EngineerExecutionStartStatus.READY:
        return _build_engineer_execution_start_failure_result(start_result)

    work_item_contract = start_result.work_item_contract
    if work_item_contract is None:
        raise ValueError("work_item_contract must be available when start_result is READY.")

    bootstrap_result = execute_engineer_execution_work_item(
        work_item_contract=work_item_contract,
        current_state=start_result.next_state,
    )
    if isinstance(bootstrap_result, EngineerExecutionBootstrapFailure):
        return _build_engineer_execution_bootstrap_failure_result(
            start_result=start_result,
            bootstrap_result=bootstrap_result,
        )

    return _build_engineer_execution_success_result(
        start_result=start_result,
        bootstrap_result=bootstrap_result,
    )


def prepare_implementation_pull_request_from_engineer_execution(
    *,
    engineer_execution_result: EngineerExecutionIntegrationResult,
    test_evidence: tuple[str, ...] | None,
    implementation_blocker_result: ImplementationBlockerResult | None,
) -> ImplementationPullRequestOpenResult:
    """Builds the implementation pull request result from engineer execution output.

    Args:
        engineer_execution_result: Application-layer engineer execution output to inspect.
        test_evidence: Local verification evidence collected after implementation completed.
        implementation_blocker_result: Existing blocker result when implementation is blocked.

    Returns:
        A typed result describing whether the implementation pull request can be opened now.

    Example:
        result = prepare_implementation_pull_request_from_engineer_execution(
            engineer_execution_result=engineer_execution_result,
            test_evidence=("make test passed.", "make lint passed."),
            implementation_blocker_result=None,
        )
        if result.status is ImplementationPullRequestOpenStatus.READY:
            assert result.pull_request_create_payload is not None
    """

    if engineer_execution_result.failure is not None:
        if (
            engineer_execution_result.next_state
            is RequirementDiscoverySessionState.IMPLEMENTATION_BLOCKED
        ):
            return build_implementation_pull_request_open_result(
                current_state=engineer_execution_result.next_state,
                work_item_contract=engineer_execution_result.work_item_contract,
                test_evidence=test_evidence,
                implementation_blocker_result=implementation_blocker_result,
            )
        if (
            engineer_execution_result.next_state
            is not RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING
        ):
            return build_implementation_pull_request_open_result(
                current_state=engineer_execution_result.next_state,
                work_item_contract=engineer_execution_result.work_item_contract,
                test_evidence=test_evidence,
                implementation_blocker_result=implementation_blocker_result,
            )

        return ImplementationPullRequestOpenResult(
            status=ImplementationPullRequestOpenStatus.INPUT_REQUIRED,
            summary_message=(
                "A successful engineer execution result is required before opening the "
                "implementation pull request."
            ),
            next_state=engineer_execution_result.next_state,
            missing_information_items=("successful engineer execution result",),
        )

    return build_implementation_pull_request_open_result(
        current_state=engineer_execution_result.next_state,
        work_item_contract=engineer_execution_result.work_item_contract,
        test_evidence=test_evidence,
        implementation_blocker_result=implementation_blocker_result,
    )


def _build_orchestration_failure_result(
    orchestration_result: RequirementDiscoveryOrchestrationFailure,
) -> RequirementDiscoveryIntegrationResult:
    """Builds the application result for a control-plane failure."""

    return RequirementDiscoveryIntegrationResult(
        architect_response_message=None,
        document_update_draft_result=None,
        pull_request_preparation_result=None,
        pull_request_open_result=None,
        updated_session_summary=None,
        failure=RequirementDiscoveryIntegrationFailureDetail(
            stage=RequirementDiscoveryIntegrationFailureStage.CONTROL_PLANE,
            failure_code=orchestration_result.failure_code,
            error_message=orchestration_result.error_message,
            is_retryable=orchestration_result.is_retryable,
        ),
    )


def _build_bootstrap_failure_result(
    bootstrap_result: RequirementDiscoveryBootstrapFailure,
) -> RequirementDiscoveryIntegrationResult:
    """Builds the application result for a worker-runtime failure."""

    return RequirementDiscoveryIntegrationResult(
        architect_response_message=None,
        document_update_draft_result=None,
        pull_request_preparation_result=None,
        pull_request_open_result=None,
        updated_session_summary=None,
        failure=RequirementDiscoveryIntegrationFailureDetail(
            stage=RequirementDiscoveryIntegrationFailureStage.WORKER_RUNTIME,
            failure_code=bootstrap_result.failure_code,
            error_message=bootstrap_result.error_message,
            is_retryable=bootstrap_result.is_retryable,
        ),
    )


def _build_success_result(
    bootstrap_result: RequirementDiscoveryBootstrapSuccess,
) -> RequirementDiscoveryIntegrationResult:
    """Builds the application result for a successful bootstrap."""

    return RequirementDiscoveryIntegrationResult(
        architect_response_message=bootstrap_result.architect_response_message,
        document_update_draft_result=bootstrap_result.document_update_draft_result,
        pull_request_preparation_result=bootstrap_result.pull_request_preparation_result,
        pull_request_open_result=bootstrap_result.pull_request_open_result,
        updated_session_summary=bootstrap_result.updated_session_summary,
        failure=None,
    )


def _build_engineer_execution_start_failure_result(
    start_result: EngineerExecutionStartResult,
) -> EngineerExecutionIntegrationResult:
    """Builds the application result for a control-plane engineer start failure."""

    return EngineerExecutionIntegrationResult(
        start_result=start_result,
        engineer_response_message=None,
        execution_focus=None,
        blocker_reporting_policy=None,
        failure=EngineerExecutionIntegrationFailureDetail(
            stage=EngineerExecutionIntegrationFailureStage.CONTROL_PLANE,
            failure_code=start_result.status,
            error_message=start_result.summary_message,
            is_retryable=False,
        ),
    )


def _build_engineer_execution_bootstrap_failure_result(
    *,
    start_result: EngineerExecutionStartResult,
    bootstrap_result: EngineerExecutionBootstrapFailure,
) -> EngineerExecutionIntegrationResult:
    """Builds the application result for a worker-runtime engineer failure."""

    return EngineerExecutionIntegrationResult(
        start_result=start_result,
        engineer_response_message=None,
        execution_focus=None,
        blocker_reporting_policy=None,
        failure=EngineerExecutionIntegrationFailureDetail(
            stage=EngineerExecutionIntegrationFailureStage.WORKER_RUNTIME,
            failure_code=bootstrap_result.failure_code,
            error_message=bootstrap_result.error_message,
            is_retryable=bootstrap_result.is_retryable,
        ),
    )


def _build_engineer_execution_success_result(
    *,
    start_result: EngineerExecutionStartResult,
    bootstrap_result: EngineerExecutionBootstrapSuccess,
) -> EngineerExecutionIntegrationResult:
    """Builds the application result for a successful engineer bootstrap."""

    return EngineerExecutionIntegrationResult(
        start_result=start_result,
        engineer_response_message=bootstrap_result.engineer_response_message,
        execution_focus=bootstrap_result.execution_focus,
        blocker_reporting_policy=bootstrap_result.blocker_reporting_policy,
        failure=None,
    )
