from shared_contracts import (
    EngineerExecutionWorkItemContract,
    EngineerJobInput,
    ImplementationPullRequestOpenStatus,
    RepositoryReference,
    RequirementDiscoverySessionState,
    RequirementDiscoverySessionSummary,
    RequirementIssueContract,
    RequirementRepositoryContract,
    UseCaseIdentifier,
    build_implementation_blocker_result,
    build_implementation_pull_request_open_result,
)
from shared_contracts.issue_contract import IssueWorkItemContract


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


def create_engineer_execution_work_item_contract() -> EngineerExecutionWorkItemContract:
    """Creates an engineer execution work item for implementation pull request tests."""

    issue_work_item_contract = IssueWorkItemContract(
        repository_reference=RepositoryReference(
            owner_name="example-owner",
            repository_name="multi-bot",
        ),
        issue_number=37,
        issue_title="Prepare implementation PR creation payload from engineer execution output",
    )
    return EngineerExecutionWorkItemContract.create_from_issue_and_job_input(
        issue_work_item_contract=issue_work_item_contract,
        engineer_job_input=create_engineer_job_input(),
    )


def create_requirement_session_summary(
    current_state: RequirementDiscoverySessionState,
) -> RequirementDiscoverySessionSummary:
    """Creates a session summary for implementation pull request tests."""

    return RequirementDiscoverySessionSummary(
        issue_contract=RequirementIssueContract(
            repository_contract=RequirementRepositoryContract(
                repository_identifier="repository-837",
                repository_reference=RepositoryReference(
                    owner_name="example-owner",
                    repository_name="multi-bot",
                ),
            ),
            issue_identifier="issue-837",
            issue_number=37,
            issue_title="Prepare implementation PR creation payload from engineer execution output",
        ),
        current_state=current_state,
        latest_prompt_summary="Engineer is preparing the implementation pull request payload.",
    )


def create_test_evidence() -> tuple[str, ...]:
    """Creates stable test evidence for implementation pull request tests."""

    return (
        "make test passed for the implementation pull request payload flow.",
        "make lint passed for the implementation pull request payload flow.",
    )


def test_build_implementation_pull_request_open_result_returns_ready_payload() -> None:
    result = build_implementation_pull_request_open_result(
        current_state=RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING,
        work_item_contract=create_engineer_execution_work_item_contract(),
        test_evidence=create_test_evidence(),
        implementation_blocker_result=None,
    )

    assert result.status is ImplementationPullRequestOpenStatus.READY
    assert result.next_state is RequirementDiscoverySessionState.IMPLEMENTATION_PR_OPEN
    assert result.missing_information_items == ()
    assert result.pull_request_create_payload is not None
    assert result.pull_request_create_payload.branch_name == (
        "feature/issue-37-prepare-implementation-pr-creation-payload-from-engineer-execution-output"
    )
    assert result.pull_request_create_payload.pull_request_title == (
        "Implement issue #37: Prepare implementation PR creation payload from engineer "
        "execution output"
    )
    assert "typed implementation pull request payload" in (
        result.pull_request_create_payload.pull_request_body_summary.casefold()
    )
    assert result.pull_request_create_payload.test_evidence == create_test_evidence()
    assert result.pull_request_create_payload.related_issue_identifier == (
        "example-owner/multi-bot#37"
    )


def test_build_implementation_pull_request_open_result_requires_running_inputs() -> None:
    result = build_implementation_pull_request_open_result(
        current_state=RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING,
        work_item_contract=None,
        test_evidence=(),
        implementation_blocker_result=None,
    )

    assert result.status is ImplementationPullRequestOpenStatus.INPUT_REQUIRED
    assert result.next_state is RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING
    assert result.pull_request_create_payload is None
    assert result.missing_information_items == (
        "engineer execution work item contract",
        "test evidence",
    )


def test_build_implementation_pull_request_open_result_returns_blocked_result() -> None:
    blocker_result = build_implementation_blocker_result(
        session_summary=create_requirement_session_summary(
            RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING,
        ),
        engineer_job_input=create_engineer_job_input(),
        blocker_summary="Engineer cannot push the implementation branch without repository access.",
    )

    result = build_implementation_pull_request_open_result(
        current_state=RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING,
        work_item_contract=create_engineer_execution_work_item_contract(),
        test_evidence=create_test_evidence(),
        implementation_blocker_result=blocker_result,
    )

    assert result.status is ImplementationPullRequestOpenStatus.BLOCKED
    assert result.next_state is RequirementDiscoverySessionState.IMPLEMENTATION_BLOCKED
    assert result.pull_request_create_payload is None
    assert result.blocker_summary == (
        "Engineer cannot push the implementation branch without repository access."
    )


def test_build_implementation_pull_request_open_result_rejects_unsupported_state() -> None:
    result = build_implementation_pull_request_open_result(
        current_state=RequirementDiscoverySessionState.PR_OPEN,
        work_item_contract=create_engineer_execution_work_item_contract(),
        test_evidence=create_test_evidence(),
        implementation_blocker_result=None,
    )

    assert result.status is ImplementationPullRequestOpenStatus.UNSUPPORTED_STATE
    assert result.next_state is RequirementDiscoverySessionState.PR_OPEN
    assert result.pull_request_create_payload is None
    assert result.missing_information_items == ()
