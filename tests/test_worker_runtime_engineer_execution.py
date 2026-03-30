from shared_contracts import (
    EngineerExecutionWorkItemContract,
    EngineerJobInput,
    ProviderName,
    RepositoryReference,
    RequirementDiscoverySessionState,
    UseCaseIdentifier,
)
from shared_contracts.issue_contract import IssueWorkItemContract
from worker_runtime import (
    EngineerExecutionBootstrapFailure,
    EngineerExecutionBootstrapFailureCode,
    EngineerExecutionBootstrapSuccess,
    execute_engineer_execution_work_item,
)


def create_issue_work_item_contract() -> IssueWorkItemContract:
    """Creates an implementation issue contract for engineer bootstrap tests."""

    return IssueWorkItemContract(
        repository_reference=RepositoryReference(
            owner_name="example-owner",
            repository_name="multi-bot",
        ),
        issue_number=36,
        issue_title="Bootstrap engineer execution from work item",
    )


def create_engineer_job_input() -> EngineerJobInput:
    """Creates strict engineer job input for engineer bootstrap tests."""

    return EngineerJobInput(
        issue_title="Bootstrap engineer execution from work item",
        issue_overview="Start the engineer implementation flow from a strict work item.",
        acceptance_criteria=(
            "Return an engineer bootstrap result with execution focus details.",
            "Surface a blocker reporting policy for the running engineer job.",
        ),
        single_pull_request_scope=(
            "Limit the work to the engineer bootstrap result model and entrypoint."
        ),
        related_issue_use_case=UseCaseIdentifier.IMPLEMENT_ISSUE_WITH_ENGINEER,
    )


def create_engineer_execution_work_item_contract(
    *,
    provider_name: ProviderName = ProviderName.CURSOR,
) -> EngineerExecutionWorkItemContract:
    """Creates a worker-runtime engineer execution work item for bootstrap tests."""

    return EngineerExecutionWorkItemContract.create_from_issue_and_job_input(
        issue_work_item_contract=create_issue_work_item_contract(),
        engineer_job_input=create_engineer_job_input(),
        provider_name=provider_name,
    )


def test_execute_engineer_execution_work_item_returns_bootstrap_success() -> None:
    work_item_contract = create_engineer_execution_work_item_contract()

    result = execute_engineer_execution_work_item(
        work_item_contract=work_item_contract,
        current_state=RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING,
    )

    assert isinstance(result, EngineerExecutionBootstrapSuccess)
    assert result.current_state is RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING
    assert result.execution_focus == work_item_contract.execution_focus
    assert result.execution_focus.acceptance_criteria == (
        work_item_contract.engineer_job_input.acceptance_criteria
    )
    assert result.execution_focus.related_issue_use_case is (
        UseCaseIdentifier.IMPLEMENT_ISSUE_WITH_ENGINEER
    )
    assert result.blocker_reporting_policy.current_state is (
        RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING
    )
    assert result.blocker_reporting_policy.next_state_on_blocker is (
        RequirementDiscoverySessionState.IMPLEMENTATION_BLOCKED
    )
    assert result.blocker_reporting_policy.required_information_items == (
        "implementation blocker summary",
    )
    assert "bootstrap engineer execution from work item" in (
        result.engineer_response_message.casefold()
    )


def test_execute_engineer_execution_work_item_rejects_unsupported_state() -> None:
    work_item_contract = create_engineer_execution_work_item_contract()

    result = execute_engineer_execution_work_item(
        work_item_contract=work_item_contract,
        current_state=RequirementDiscoverySessionState.IMPLEMENTATION_BACKLOG_READY,
    )

    assert isinstance(result, EngineerExecutionBootstrapFailure)
    assert result.failure_code is EngineerExecutionBootstrapFailureCode.UNSUPPORTED_STATE
    assert result.current_state is RequirementDiscoverySessionState.IMPLEMENTATION_BACKLOG_READY
    assert result.is_retryable is False
    assert "state_implementation_backlog_ready" in result.error_message.casefold()


def test_execute_engineer_execution_work_item_requires_work_item_input() -> None:
    result = execute_engineer_execution_work_item(
        work_item_contract=None,
        current_state=RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING,
    )

    assert isinstance(result, EngineerExecutionBootstrapFailure)
    assert result.failure_code is EngineerExecutionBootstrapFailureCode.INVALID_INPUT
    assert result.current_state is RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING
    assert result.is_retryable is False
    assert "work_item_contract" in result.error_message
