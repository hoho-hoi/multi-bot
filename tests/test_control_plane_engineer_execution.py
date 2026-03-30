from control_plane import EngineerExecutionStartStatus, start_engineer_execution
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


def create_requirement_repository_contract() -> RequirementRepositoryContract:
    """Creates a repository contract for engineer execution control-plane tests."""

    return RequirementRepositoryContract(
        repository_identifier="repository-123",
        repository_reference=RepositoryReference(
            owner_name="example-owner",
            repository_name="multi-bot",
        ),
    )


def create_requirement_issue_contract() -> RequirementIssueContract:
    """Creates a requirement issue contract for engineer execution control-plane tests."""

    return RequirementIssueContract(
        repository_contract=create_requirement_repository_contract(),
        issue_identifier="issue-456",
        issue_number=6,
        issue_title="Prepare engineer execution handoff",
    )


def create_engineer_execution_session_summary(
    current_state: RequirementDiscoverySessionState,
) -> RequirementDiscoverySessionSummary:
    """Creates a session summary for engineer execution control-plane tests."""

    return RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=current_state,
        latest_prompt_summary="Manager prepared the implementation backlog for engineer execution.",
    )


def create_backlog_ready_issue_work_item_contract() -> IssueWorkItemContract:
    """Creates an implementation issue work item for engineer execution tests."""

    return IssueWorkItemContract(
        repository_reference=RepositoryReference(
            owner_name="example-owner",
            repository_name="multi-bot",
        ),
        issue_number=38,
        issue_title="Build engineer execution work item and running-state transition",
    )


def create_engineer_job_input() -> EngineerJobInput:
    """Creates strict engineer job input for engineer execution control-plane tests."""

    return EngineerJobInput(
        issue_title="Build engineer execution work item and running-state transition",
        issue_overview="Prepare the control-plane transition into engineer execution.",
        acceptance_criteria=(
            "Return a strict engineer execution work item.",
            "Transition the workflow to STATE_ENGINEER_JOB_RUNNING when ready.",
        ),
        single_pull_request_scope="Limit the work to engineer execution start orchestration.",
        related_issue_use_case=UseCaseIdentifier.IMPLEMENT_ISSUE_WITH_ENGINEER,
    )


def test_start_engineer_execution_returns_running_work_item_for_backlog_ready_inputs() -> None:
    session_summary = create_engineer_execution_session_summary(
        RequirementDiscoverySessionState.IMPLEMENTATION_BACKLOG_READY,
    )

    result = start_engineer_execution(
        session_summary=session_summary,
        issue_work_item_contract=create_backlog_ready_issue_work_item_contract(),
        engineer_job_input=create_engineer_job_input(),
    )

    assert result.status is EngineerExecutionStartStatus.READY
    assert result.current_state is RequirementDiscoverySessionState.IMPLEMENTATION_BACKLOG_READY
    assert result.next_state is RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING
    assert result.work_item_contract is not None
    assert result.work_item_contract.issue_work_item_contract.to_issue_identifier() == (
        "example-owner/multi-bot#38"
    )
    assert result.work_item_contract.execution_focus.related_issue_use_case is (
        UseCaseIdentifier.IMPLEMENT_ISSUE_WITH_ENGINEER
    )


def test_start_engineer_execution_returns_backlog_ready_when_information_is_missing() -> None:
    session_summary = create_engineer_execution_session_summary(
        RequirementDiscoverySessionState.IMPLEMENTATION_BACKLOG_READY,
    )

    result = start_engineer_execution(
        session_summary=session_summary,
        issue_work_item_contract=None,
        engineer_job_input=None,
    )

    assert result.status is EngineerExecutionStartStatus.INPUT_REQUIRED
    assert result.next_state is RequirementDiscoverySessionState.IMPLEMENTATION_BACKLOG_READY
    assert result.work_item_contract is None
    assert result.missing_information_items == (
        "implementation issue work item contract",
        "engineer job input",
    )


def test_start_engineer_execution_rejects_unsupported_state() -> None:
    session_summary = create_engineer_execution_session_summary(
        RequirementDiscoverySessionState.PR_OPEN,
    )

    result = start_engineer_execution(
        session_summary=session_summary,
        issue_work_item_contract=create_backlog_ready_issue_work_item_contract(),
        engineer_job_input=create_engineer_job_input(),
    )

    assert result.status is EngineerExecutionStartStatus.UNSUPPORTED_STATE
    assert result.current_state is RequirementDiscoverySessionState.PR_OPEN
    assert result.next_state is RequirementDiscoverySessionState.PR_OPEN
    assert result.work_item_contract is None
