from unittest.mock import patch

from application import (
    EngineerExecutionIntegrationFailureDetail,
    EngineerExecutionIntegrationFailureStage,
    start_engineer_execution_from_backlog_ready_issue,
)
from control_plane import EngineerExecutionStartStatus
from shared_contracts import (
    EngineerJobInput,
    RepositoryReference,
    RequirementDiscoverySessionState,
    RequirementDiscoverySessionSummary,
    RequirementIssueContract,
    RequirementRepositoryContract,
    UseCaseIdentifier,
)
from shared_contracts.issue_contract import IssueWorkItemContract
from worker_runtime import EngineerExecutionBootstrapFailure, EngineerExecutionBootstrapFailureCode


def create_requirement_repository_contract() -> RequirementRepositoryContract:
    """Creates a repository contract for engineer execution integration tests."""

    return RequirementRepositoryContract(
        repository_identifier="repository-789",
        repository_reference=RepositoryReference(
            owner_name="example-owner",
            repository_name="multi-bot",
        ),
    )


def create_requirement_issue_contract() -> RequirementIssueContract:
    """Creates a requirement issue contract for engineer execution integration tests."""

    return RequirementIssueContract(
        repository_contract=create_requirement_repository_contract(),
        issue_identifier="issue-789",
        issue_number=39,
        issue_title="Integrate engineer job start through application entrypoint",
    )


def create_engineer_execution_session_summary(
    current_state: RequirementDiscoverySessionState,
) -> RequirementDiscoverySessionSummary:
    """Creates a session summary for engineer execution integration tests."""

    return RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=current_state,
        latest_prompt_summary="Manager prepared a backlog-ready implementation issue.",
    )


def create_backlog_ready_issue_work_item_contract() -> IssueWorkItemContract:
    """Creates an implementation issue work item for engineer execution integration tests."""

    return IssueWorkItemContract(
        repository_reference=RepositoryReference(
            owner_name="example-owner",
            repository_name="multi-bot",
        ),
        issue_number=39,
        issue_title="Integrate engineer job start through application entrypoint",
    )


def create_engineer_job_input() -> EngineerJobInput:
    """Creates strict engineer job input for engineer execution integration tests."""

    return EngineerJobInput(
        issue_title="Integrate engineer job start through application entrypoint",
        issue_overview=(
            "Connect the control-plane start decision with the worker-runtime engineer bootstrap."
        ),
        acceptance_criteria=(
            "Return a strict integration result for engineer execution start.",
            "Expose the running-state transition, execution focus, and blocker fallback.",
        ),
        single_pull_request_scope=(
            "Limit the work to the application entrypoint that starts engineer execution."
        ),
        related_issue_use_case=UseCaseIdentifier.IMPLEMENT_ISSUE_WITH_ENGINEER,
    )


def test_start_engineer_execution_from_backlog_ready_issue_returns_running_job() -> None:
    session_summary = create_engineer_execution_session_summary(
        RequirementDiscoverySessionState.IMPLEMENTATION_BACKLOG_READY,
    )

    result = start_engineer_execution_from_backlog_ready_issue(
        session_summary=session_summary,
        issue_work_item_contract=create_backlog_ready_issue_work_item_contract(),
        engineer_job_input=create_engineer_job_input(),
    )

    assert result.failure is None
    assert result.is_successful is True
    assert result.current_state is RequirementDiscoverySessionState.IMPLEMENTATION_BACKLOG_READY
    assert result.next_state is RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING
    assert result.work_item_contract is not None
    assert result.execution_focus is not None
    assert result.execution_focus.related_issue_use_case is (
        UseCaseIdentifier.IMPLEMENT_ISSUE_WITH_ENGINEER
    )
    assert result.blocker_reporting_policy is not None
    assert result.blocker_reporting_policy.next_state_on_blocker is (
        RequirementDiscoverySessionState.IMPLEMENTATION_BLOCKED
    )
    assert result.engineer_response_message is not None
    assert "issue #39" in result.engineer_response_message.lower()


def test_start_engineer_execution_from_backlog_ready_issue_returns_orchestration_failure() -> None:
    session_summary = create_engineer_execution_session_summary(
        RequirementDiscoverySessionState.PR_OPEN,
    )

    result = start_engineer_execution_from_backlog_ready_issue(
        session_summary=session_summary,
        issue_work_item_contract=create_backlog_ready_issue_work_item_contract(),
        engineer_job_input=create_engineer_job_input(),
    )

    assert result.engineer_response_message is None
    assert result.execution_focus is None
    assert result.blocker_reporting_policy is None
    assert isinstance(result.failure, EngineerExecutionIntegrationFailureDetail)
    assert result.failure.stage is EngineerExecutionIntegrationFailureStage.CONTROL_PLANE
    assert result.failure.failure_code is EngineerExecutionStartStatus.UNSUPPORTED_STATE
    assert result.failure.is_retryable is False
    assert result.current_state is RequirementDiscoverySessionState.PR_OPEN
    assert result.next_state is RequirementDiscoverySessionState.PR_OPEN
    assert "state_requirement_pr_open" in result.failure.error_message.casefold()


def test_start_engineer_execution_from_backlog_ready_issue_returns_bootstrap_failure() -> None:
    session_summary = create_engineer_execution_session_summary(
        RequirementDiscoverySessionState.IMPLEMENTATION_BACKLOG_READY,
    )
    bootstrap_failure = EngineerExecutionBootstrapFailure(
        current_state=RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING,
        failure_code=EngineerExecutionBootstrapFailureCode.UNSUPPORTED_PROVIDER,
        error_message="provider_name openai is not supported for engineer execution bootstrap.",
        is_retryable=False,
    )

    with patch(
        "application.entrypoint.execute_engineer_execution_work_item",
        return_value=bootstrap_failure,
    ):
        result = start_engineer_execution_from_backlog_ready_issue(
            session_summary=session_summary,
            issue_work_item_contract=create_backlog_ready_issue_work_item_contract(),
            engineer_job_input=create_engineer_job_input(),
        )

    assert result.engineer_response_message is None
    assert result.execution_focus is None
    assert result.blocker_reporting_policy is None
    assert isinstance(result.failure, EngineerExecutionIntegrationFailureDetail)
    assert result.failure.stage is EngineerExecutionIntegrationFailureStage.WORKER_RUNTIME
    assert result.failure.failure_code is (
        EngineerExecutionBootstrapFailureCode.UNSUPPORTED_PROVIDER
    )
    assert result.failure.is_retryable is False
    assert result.current_state is RequirementDiscoverySessionState.IMPLEMENTATION_BACKLOG_READY
    assert result.next_state is RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING
    assert "provider_name openai" in result.failure.error_message
