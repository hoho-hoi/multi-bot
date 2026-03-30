from application import (
    prepare_implementation_pull_request_from_engineer_execution,
    start_engineer_execution_from_backlog_ready_issue,
)
from shared_contracts import (
    EngineerJobInput,
    ImplementationPullRequestOpenStatus,
    RepositoryReference,
    RequirementDiscoverySessionState,
    RequirementDiscoverySessionSummary,
    RequirementIssueContract,
    RequirementRepositoryContract,
    UseCaseIdentifier,
    build_implementation_blocker_result,
)
from shared_contracts.issue_contract import IssueWorkItemContract


def create_requirement_repository_contract() -> RequirementRepositoryContract:
    """Creates a repository contract for implementation pull request application tests."""

    return RequirementRepositoryContract(
        repository_identifier="repository-937",
        repository_reference=RepositoryReference(
            owner_name="example-owner",
            repository_name="multi-bot",
        ),
    )


def create_requirement_issue_contract() -> RequirementIssueContract:
    """Creates a requirement issue contract for implementation pull request tests."""

    return RequirementIssueContract(
        repository_contract=create_requirement_repository_contract(),
        issue_identifier="issue-937",
        issue_number=37,
        issue_title="Prepare implementation PR creation payload from engineer execution output",
    )


def create_engineer_execution_session_summary(
    current_state: RequirementDiscoverySessionState,
) -> RequirementDiscoverySessionSummary:
    """Creates a session summary for implementation pull request application tests."""

    return RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=current_state,
        latest_prompt_summary="Engineer is preparing the implementation pull request payload.",
    )


def create_issue_work_item_contract() -> IssueWorkItemContract:
    """Creates an implementation issue work item for application tests."""

    return IssueWorkItemContract(
        repository_reference=RepositoryReference(
            owner_name="example-owner",
            repository_name="multi-bot",
        ),
        issue_number=37,
        issue_title="Prepare implementation PR creation payload from engineer execution output",
    )


def create_engineer_job_input() -> EngineerJobInput:
    """Creates strict engineer job input for implementation pull request tests."""

    return EngineerJobInput(
        issue_title="Prepare implementation PR creation payload from engineer execution output",
        issue_overview=(
            "Build the typed implementation pull request payload from the finished engineer "
            "execution context."
        ),
        acceptance_criteria=(
            "Return a strict implementation pull request payload.",
            "Keep the workflow blocked when Engineer reported an implementation blocker.",
        ),
        single_pull_request_scope=(
            "Limit the work to implementation pull request payload preparation."
        ),
        related_issue_use_case=UseCaseIdentifier.IMPLEMENT_ISSUE_WITH_ENGINEER,
    )


def create_test_evidence() -> tuple[str, ...]:
    """Creates stable test evidence for implementation pull request application tests."""

    return (
        "make test passed for the implementation pull request application flow.",
        "make lint passed for the implementation pull request application flow.",
    )


def test_prepare_implementation_pull_request_from_engineer_execution_returns_ready_payload() -> (
    None
):
    engineer_execution_result = start_engineer_execution_from_backlog_ready_issue(
        session_summary=create_engineer_execution_session_summary(
            RequirementDiscoverySessionState.IMPLEMENTATION_BACKLOG_READY,
        ),
        issue_work_item_contract=create_issue_work_item_contract(),
        engineer_job_input=create_engineer_job_input(),
    )

    result = prepare_implementation_pull_request_from_engineer_execution(
        engineer_execution_result=engineer_execution_result,
        test_evidence=create_test_evidence(),
        implementation_blocker_result=None,
    )

    assert result.status is ImplementationPullRequestOpenStatus.READY
    assert result.next_state is RequirementDiscoverySessionState.IMPLEMENTATION_PR_OPEN
    assert result.pull_request_create_payload is not None
    assert result.pull_request_create_payload.base_branch_name == "main"
    assert result.pull_request_create_payload.related_issue_identifier == (
        "example-owner/multi-bot#37"
    )


def test_prepare_implementation_pull_request_from_engineer_execution_returns_blocked_result() -> (
    None
):
    engineer_execution_result = start_engineer_execution_from_backlog_ready_issue(
        session_summary=create_engineer_execution_session_summary(
            RequirementDiscoverySessionState.IMPLEMENTATION_BACKLOG_READY,
        ),
        issue_work_item_contract=create_issue_work_item_contract(),
        engineer_job_input=create_engineer_job_input(),
    )
    blocker_result = build_implementation_blocker_result(
        session_summary=create_engineer_execution_session_summary(
            RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING,
        ),
        engineer_job_input=create_engineer_job_input(),
        blocker_summary="Engineer cannot push the implementation branch without repository access.",
    )

    result = prepare_implementation_pull_request_from_engineer_execution(
        engineer_execution_result=engineer_execution_result,
        test_evidence=create_test_evidence(),
        implementation_blocker_result=blocker_result,
    )

    assert result.status is ImplementationPullRequestOpenStatus.BLOCKED
    assert result.next_state is RequirementDiscoverySessionState.IMPLEMENTATION_BLOCKED
    assert result.pull_request_create_payload is None
    assert result.blocker_summary == (
        "Engineer cannot push the implementation branch without repository access."
    )
