from application import (
    RequirementDiscoveryIntegrationFailureDetail,
    RequirementDiscoveryIntegrationFailureStage,
    generate_requirement_discovery_architect_response,
)
from control_plane import RequirementDiscoveryOrchestrationFailureCode
from shared_contracts import (
    RepositoryReference,
    RequirementCommentContract,
    RequirementDiscoverySessionState,
    RequirementDiscoverySessionSummary,
    RequirementDocumentType,
    RequirementDocumentUpdateDraftStatus,
    RequirementIssueContract,
    RequirementPullRequestPreparationStatus,
    RequirementRepositoryContract,
)


def create_requirement_repository_contract() -> RequirementRepositoryContract:
    """Creates a repository contract for integration tests."""

    return RequirementRepositoryContract(
        repository_identifier="repository-456",
        repository_reference=RepositoryReference(
            owner_name="example-owner",
            repository_name="multi-bot",
        ),
    )


def create_requirement_issue_contract() -> RequirementIssueContract:
    """Creates an issue contract for integration tests."""

    return RequirementIssueContract(
        repository_contract=create_requirement_repository_contract(),
        issue_identifier="issue-654",
        issue_number=12,
        issue_title="Connect control-plane and worker-runtime for requirement discovery replies",
    )


def create_requirement_comment_contract() -> RequirementCommentContract:
    """Creates a comment contract for integration tests."""

    return RequirementCommentContract(
        issue_contract=create_requirement_issue_contract(),
        comment_identifier="comment-987",
        comment_body="Please clarify observability, security, and rollback expectations.",
    )


def test_generate_requirement_discovery_architect_response_returns_initial_bootstrap_message() -> (
    None
):
    session_summary = RequirementDiscoverySessionSummary.create_initial(
        issue_contract=create_requirement_issue_contract(),
    )

    result = generate_requirement_discovery_architect_response(session_summary)

    assert result.failure is None
    assert result.updated_session_summary is not None
    assert result.updated_session_summary.current_state is (
        RequirementDiscoverySessionState.DISCOVERY_IN_PROGRESS
    )
    assert result.architect_response_message is not None
    assert "issue #12" in result.architect_response_message.lower()
    assert "project goal" in result.architect_response_message.lower()
    assert result.document_update_draft_result is not None
    assert result.document_update_draft_result.status is (
        RequirementDocumentUpdateDraftStatus.INPUT_REQUIRED
    )


def test_generate_requirement_discovery_architect_response_returns_follow_up_message() -> None:
    session_summary = RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=RequirementDiscoverySessionState.DISCOVERY_IN_PROGRESS,
        latest_comment_contract=create_requirement_comment_contract(),
        latest_prompt_summary="Clarify audit logging, edge cases, and rollback requirements.",
    )

    result = generate_requirement_discovery_architect_response(session_summary)

    assert result.failure is None
    assert result.updated_session_summary is not None
    assert result.updated_session_summary.current_state is (
        RequirementDiscoverySessionState.DISCOVERY_IN_PROGRESS
    )
    assert (
        result.updated_session_summary.latest_prompt_summary
        == "Clarify audit logging, edge cases, and rollback requirements."
    )
    assert result.architect_response_message is not None
    assert "clarify audit logging, edge cases, and rollback requirements." in (
        result.architect_response_message.lower()
    )
    assert result.document_update_draft_result is not None
    assert result.document_update_draft_result.status is RequirementDocumentUpdateDraftStatus.READY
    assert {draft.document_type for draft in result.document_update_draft_result.update_drafts} == {
        RequirementDocumentType.REQUIREMENT
    }


def test_generate_requirement_discovery_architect_response_returns_ready_preparation() -> None:
    session_summary = RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=RequirementDiscoverySessionState.DISCOVERY_IN_PROGRESS,
        latest_comment_contract=create_requirement_comment_contract(),
        latest_prompt_summary=(
            "Clarify the project goal, security constraints, success criteria, "
            "user workflow, and architecture boundaries."
        ),
    )

    result = generate_requirement_discovery_architect_response(session_summary)

    assert result.failure is None
    assert result.pull_request_preparation_result is not None
    assert result.pull_request_preparation_result.status is (
        RequirementPullRequestPreparationStatus.READY
    )
    assert result.pull_request_preparation_result.preparation_draft is not None
    preparation_draft = result.pull_request_preparation_result.preparation_draft
    assert {document_type for document_type in preparation_draft.updated_documents} == {
        RequirementDocumentType.REQUIREMENT,
        RequirementDocumentType.USE_CASES,
        RequirementDocumentType.ARCHITECTURE_DIAGRAM,
    }


def test_generate_requirement_discovery_architect_response_returns_invalid_input_failure() -> None:
    session_summary = RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=RequirementDiscoverySessionState.DISCOVERY_IN_PROGRESS,
        latest_comment_contract=create_requirement_comment_contract(),
        latest_prompt_summary=None,
    )

    result = generate_requirement_discovery_architect_response(session_summary)

    assert result.architect_response_message is None
    assert result.updated_session_summary is None
    assert result.document_update_draft_result is None
    assert isinstance(result.failure, RequirementDiscoveryIntegrationFailureDetail)
    assert result.failure.stage is RequirementDiscoveryIntegrationFailureStage.CONTROL_PLANE
    assert result.failure.failure_code is RequirementDiscoveryOrchestrationFailureCode.INVALID_INPUT
    assert result.failure.is_retryable is False
    assert "latest_prompt_summary" in result.failure.error_message


def test_generate_requirement_discovery_architect_response_returns_unsupported_state_failure() -> (
    None
):
    session_summary = RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=RequirementDiscoverySessionState.PR_OPEN,
        latest_comment_contract=create_requirement_comment_contract(),
        latest_prompt_summary="Requirement pull request is already open.",
    )

    result = generate_requirement_discovery_architect_response(session_summary)

    assert result.architect_response_message is None
    assert result.updated_session_summary is None
    assert result.document_update_draft_result is None
    assert isinstance(result.failure, RequirementDiscoveryIntegrationFailureDetail)
    assert result.failure.stage is RequirementDiscoveryIntegrationFailureStage.CONTROL_PLANE
    assert (
        result.failure.failure_code
        is RequirementDiscoveryOrchestrationFailureCode.UNSUPPORTED_STATE
    )
    assert result.failure.is_retryable is False
    assert "STATE_REQUIREMENT_PR_OPEN" in result.failure.error_message
