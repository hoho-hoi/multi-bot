from control_plane import (
    RequirementDiscoveryOrchestrationFailure,
    RequirementDiscoveryOrchestrationFailureCode,
    RequirementDiscoveryOrchestrationSuccess,
    orchestrate_requirement_discovery_session,
)
from shared_contracts import (
    RepositoryReference,
    RequirementCommentContract,
    RequirementDiscoverySessionState,
    RequirementDiscoverySessionSummary,
    RequirementIssueContract,
    RequirementRepositoryContract,
)


def create_requirement_repository_contract() -> RequirementRepositoryContract:
    """Creates a repository contract for requirement discovery orchestration tests."""

    return RequirementRepositoryContract(
        repository_identifier="repository-123",
        repository_reference=RepositoryReference(
            owner_name="example-owner",
            repository_name="multi-bot",
        ),
    )


def create_requirement_issue_contract() -> RequirementIssueContract:
    """Creates an issue contract for requirement discovery orchestration tests."""

    return RequirementIssueContract(
        repository_contract=create_requirement_repository_contract(),
        issue_identifier="issue-456",
        issue_number=6,
        issue_title="Implement control-plane requirement discovery orchestration",
    )


def create_requirement_comment_contract() -> RequirementCommentContract:
    """Creates a comment contract for requirement discovery orchestration tests."""

    return RequirementCommentContract(
        issue_contract=create_requirement_issue_contract(),
        comment_identifier="comment-789",
        comment_body="Architect needs explicit error handling and state transitions.",
    )


def test_orchestrate_requirement_discovery_session_builds_worker_runtime_work_item() -> None:
    session_summary = RequirementDiscoverySessionSummary.create_initial(
        issue_contract=create_requirement_issue_contract(),
    )

    result = orchestrate_requirement_discovery_session(session_summary)

    assert isinstance(result, RequirementDiscoveryOrchestrationSuccess)
    assert result.current_state is RequirementDiscoverySessionState.ISSUE_READY
    assert (
        result.work_item_contract.issue_work_item_contract.to_issue_identifier()
        == "example-owner/multi-bot#6"
    )
    assert result.work_item_contract.session_summary == session_summary
    assert "start requirement discovery" in result.next_action_summary.lower()


def test_orchestrate_requirement_discovery_session_summarizes_discovery_in_progress() -> None:
    session_summary = RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=RequirementDiscoverySessionState.DISCOVERY_IN_PROGRESS,
        latest_comment_contract=create_requirement_comment_contract(),
        latest_prompt_summary="Clarify security, error handling, and orchestration ownership.",
    )

    result = orchestrate_requirement_discovery_session(session_summary)

    assert isinstance(result, RequirementDiscoveryOrchestrationSuccess)
    assert result.current_state is RequirementDiscoverySessionState.DISCOVERY_IN_PROGRESS
    assert (
        "Clarify security, error handling, and orchestration ownership."
        in result.next_action_summary
    )


def test_orchestrate_requirement_discovery_session_rejects_missing_prompt_summary() -> None:
    session_summary = RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=RequirementDiscoverySessionState.DISCOVERY_IN_PROGRESS,
        latest_comment_contract=create_requirement_comment_contract(),
        latest_prompt_summary=None,
    )

    result = orchestrate_requirement_discovery_session(session_summary)

    assert isinstance(result, RequirementDiscoveryOrchestrationFailure)
    assert result.current_state is RequirementDiscoverySessionState.DISCOVERY_IN_PROGRESS
    assert result.failure_code is RequirementDiscoveryOrchestrationFailureCode.INVALID_INPUT
    assert result.is_retryable is False
    assert "latest_prompt_summary" in result.error_message


def test_orchestrate_requirement_discovery_session_rejects_unsupported_state() -> None:
    session_summary = RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=RequirementDiscoverySessionState.PR_OPEN,
        latest_comment_contract=create_requirement_comment_contract(),
        latest_prompt_summary="Requirement PR is already open.",
    )

    result = orchestrate_requirement_discovery_session(session_summary)

    assert isinstance(result, RequirementDiscoveryOrchestrationFailure)
    assert result.current_state is RequirementDiscoverySessionState.PR_OPEN
    assert result.failure_code is RequirementDiscoveryOrchestrationFailureCode.UNSUPPORTED_STATE
    assert result.is_retryable is False
    assert "STATE_REQUIREMENT_PR_OPEN" in result.error_message
