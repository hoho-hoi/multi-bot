from dataclasses import dataclass
from enum import StrEnum

from control_plane import (
    RequirementDiscoveryOrchestrationFailure,
    RequirementDiscoveryOrchestrationFailureCode,
    orchestrate_requirement_discovery_session,
)
from shared_contracts import (
    RequirementDiscoverySessionSummary,
    RequirementDocumentUpdateDraftResult,
    RequirementPullRequestOpenResult,
    RequirementPullRequestPreparationResult,
)
from worker_runtime import (
    RequirementDiscoveryBootstrapFailure,
    RequirementDiscoveryBootstrapFailureCode,
    RequirementDiscoveryBootstrapSuccess,
    execute_requirement_discovery_work_item,
)


class RequirementDiscoveryIntegrationFailureStage(StrEnum):
    """Enumerates the stage that produced an integration failure."""

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
