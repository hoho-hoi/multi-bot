from shared_contracts import (
    IssueWorkItemContract,
    ProviderName,
    RepositoryReference,
    RequirementCommentContract,
    RequirementDiscoverySessionState,
    RequirementDiscoverySessionSummary,
    RequirementDiscoveryWorkItemContract,
    RequirementDocumentType,
    RequirementDocumentUpdateDraftStatus,
    RequirementIssueContract,
    RequirementPullRequestPreparationStatus,
    RequirementRepositoryContract,
    WorkerRoleName,
)
from worker_runtime import (
    RequirementDiscoveryBootstrapFailure,
    RequirementDiscoveryBootstrapFailureCode,
    RequirementDiscoveryBootstrapSuccess,
    execute_requirement_discovery_work_item,
)


def create_requirement_repository_contract() -> RequirementRepositoryContract:
    """Creates a repository contract for worker-runtime tests."""

    return RequirementRepositoryContract(
        repository_identifier="repository-123",
        repository_reference=RepositoryReference(
            owner_name="example-owner",
            repository_name="multi-bot",
        ),
    )


def create_requirement_issue_contract() -> RequirementIssueContract:
    """Creates an issue contract for worker-runtime tests."""

    return RequirementIssueContract(
        repository_contract=create_requirement_repository_contract(),
        issue_identifier="issue-789",
        issue_number=7,
        issue_title="Implement worker-runtime Architect response bootstrap",
    )


def create_requirement_comment_contract() -> RequirementCommentContract:
    """Creates a comment contract for worker-runtime tests."""

    return RequirementCommentContract(
        issue_contract=create_requirement_issue_contract(),
        comment_identifier="comment-321",
        comment_body="The product owner clarified the security and observability constraints.",
    )


def create_requirement_discovery_work_item_contract(
    *,
    current_state: RequirementDiscoverySessionState,
    role_name: WorkerRoleName = WorkerRoleName.ARCHITECT,
    provider_name: ProviderName = ProviderName.CURSOR,
    latest_prompt_summary: str | None = None,
    latest_comment_contract: RequirementCommentContract | None = None,
) -> RequirementDiscoveryWorkItemContract:
    """Creates a requirement discovery work item for worker-runtime tests."""

    issue_contract = create_requirement_issue_contract()
    session_summary = RequirementDiscoverySessionSummary(
        issue_contract=issue_contract,
        current_state=current_state,
        latest_comment_contract=latest_comment_contract,
        latest_prompt_summary=latest_prompt_summary,
    )
    return RequirementDiscoveryWorkItemContract(
        issue_work_item_contract=IssueWorkItemContract(
            repository_reference=issue_contract.repository_contract.repository_reference,
            issue_number=issue_contract.issue_number,
            issue_title=issue_contract.issue_title,
        ),
        session_summary=session_summary,
        role_name=role_name,
        provider_name=provider_name,
    )


def test_execute_requirement_discovery_work_item_builds_initial_architect_bootstrap() -> None:
    work_item_contract = create_requirement_discovery_work_item_contract(
        current_state=RequirementDiscoverySessionState.ISSUE_READY,
    )

    result = execute_requirement_discovery_work_item(work_item_contract)

    assert isinstance(result, RequirementDiscoveryBootstrapSuccess)
    assert result.updated_session_summary.current_state is (
        RequirementDiscoverySessionState.DISCOVERY_IN_PROGRESS
    )
    assert result.updated_session_summary.latest_prompt_summary is not None
    assert "goal" in result.updated_session_summary.latest_prompt_summary.lower()
    assert "issue #7" in result.architect_response_message.lower()
    assert "implement worker-runtime architect response bootstrap" in (
        result.architect_response_message.lower()
    )
    assert result.document_update_draft_result.status is (
        RequirementDocumentUpdateDraftStatus.INPUT_REQUIRED
    )
    assert result.document_update_draft_result.update_drafts == ()


def test_execute_requirement_discovery_work_item_continues_architect_bootstrap() -> None:
    work_item_contract = create_requirement_discovery_work_item_contract(
        current_state=RequirementDiscoverySessionState.DISCOVERY_IN_PROGRESS,
        latest_comment_contract=create_requirement_comment_contract(),
        latest_prompt_summary="Clarify reliability, logging, and edge-case expectations.",
    )

    result = execute_requirement_discovery_work_item(work_item_contract)

    assert isinstance(result, RequirementDiscoveryBootstrapSuccess)
    assert result.updated_session_summary.current_state is (
        RequirementDiscoverySessionState.DISCOVERY_IN_PROGRESS
    )
    assert (
        result.updated_session_summary.latest_prompt_summary
        == "Clarify reliability, logging, and edge-case expectations."
    )
    assert "clarify reliability, logging, and edge-case expectations." in (
        result.architect_response_message.lower()
    )
    assert result.document_update_draft_result.status is RequirementDocumentUpdateDraftStatus.READY
    assert result.document_update_draft_result.source_prompt_summary is not None
    assert {draft.document_type for draft in result.document_update_draft_result.update_drafts} == {
        RequirementDocumentType.REQUIREMENT
    }


def test_execute_requirement_discovery_work_item_returns_ready_preparation() -> None:
    work_item_contract = create_requirement_discovery_work_item_contract(
        current_state=RequirementDiscoverySessionState.DISCOVERY_IN_PROGRESS,
        latest_comment_contract=create_requirement_comment_contract(),
        latest_prompt_summary=(
            "Clarify the project goal, security constraints, success criteria, "
            "user workflow, and architecture boundaries."
        ),
    )

    result = execute_requirement_discovery_work_item(work_item_contract)

    assert isinstance(result, RequirementDiscoveryBootstrapSuccess)
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


def test_execute_requirement_discovery_work_item_returns_no_updates_for_no_change_intent() -> None:
    work_item_contract = create_requirement_discovery_work_item_contract(
        current_state=RequirementDiscoverySessionState.DISCOVERY_IN_PROGRESS,
        latest_comment_contract=create_requirement_comment_contract(),
        latest_prompt_summary="No document updates are needed after the latest clarification.",
    )

    result = execute_requirement_discovery_work_item(work_item_contract)

    assert isinstance(result, RequirementDiscoveryBootstrapSuccess)
    assert result.document_update_draft_result.status is (
        RequirementDocumentUpdateDraftStatus.NO_UPDATES_NEEDED
    )
    assert result.document_update_draft_result.update_drafts == ()


def test_execute_requirement_discovery_work_item_rejects_unsupported_role() -> None:
    work_item_contract = create_requirement_discovery_work_item_contract(
        current_state=RequirementDiscoverySessionState.ISSUE_READY,
        role_name=WorkerRoleName.MANAGER,
    )

    result = execute_requirement_discovery_work_item(work_item_contract)

    assert isinstance(result, RequirementDiscoveryBootstrapFailure)
    assert result.failure_code is RequirementDiscoveryBootstrapFailureCode.UNSUPPORTED_ROLE
    assert result.is_retryable is False
    assert "manager" in result.error_message.lower()


def test_execute_requirement_discovery_work_item_rejects_unsupported_provider() -> None:
    work_item_contract = create_requirement_discovery_work_item_contract(
        current_state=RequirementDiscoverySessionState.ISSUE_READY,
        provider_name=ProviderName.OPENAI,
    )

    result = execute_requirement_discovery_work_item(work_item_contract)

    assert isinstance(result, RequirementDiscoveryBootstrapFailure)
    assert result.failure_code is RequirementDiscoveryBootstrapFailureCode.UNSUPPORTED_PROVIDER
    assert result.is_retryable is False
    assert "openai" in result.error_message.lower()


def test_execute_requirement_discovery_work_item_rejects_unsupported_state() -> None:
    work_item_contract = create_requirement_discovery_work_item_contract(
        current_state=RequirementDiscoverySessionState.PR_OPEN,
        latest_comment_contract=create_requirement_comment_contract(),
        latest_prompt_summary="The requirement pull request is already open.",
    )

    result = execute_requirement_discovery_work_item(work_item_contract)

    assert isinstance(result, RequirementDiscoveryBootstrapFailure)
    assert result.failure_code is RequirementDiscoveryBootstrapFailureCode.UNSUPPORTED_STATE
    assert result.is_retryable is False
    assert "state_requirement_pr_open" in result.error_message.lower()
