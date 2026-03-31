from application import review_opened_implementation_pull_request
from shared_contracts import (
    ManagerImplementationReviewCheckTarget,
    ManagerImplementationReviewDecision,
    ManagerImplementationReviewDecisionFinding,
    ManagerImplementationReviewDecisionStatus,
    ManagerImplementationReviewExecutionStatus,
    ManagerImplementationReviewInputStatus,
    OpenedImplementationPullRequestMetadata,
    RepositoryReference,
    RequirementDiscoverySessionState,
    RequirementDiscoverySessionSummary,
    RequirementIssueContract,
    RequirementRepositoryContract,
)


def create_requirement_repository_contract() -> RequirementRepositoryContract:
    """Creates a repository contract for implementation review application tests."""

    return RequirementRepositoryContract(
        repository_identifier="repository-789",
        repository_reference=RepositoryReference(
            owner_name="example-owner",
            repository_name="multi-bot",
        ),
    )


def create_requirement_issue_contract() -> RequirementIssueContract:
    """Creates an issue contract for implementation review application tests."""

    return RequirementIssueContract(
        repository_contract=create_requirement_repository_contract(),
        issue_identifier="issue-789",
        issue_number=56,
        issue_title="Integrate manager implementation review flow through application entrypoint",
    )


def create_session_summary(
    current_state: RequirementDiscoverySessionState,
) -> RequirementDiscoverySessionSummary:
    """Creates a session summary for implementation review application tests."""

    return RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=current_state,
        latest_prompt_summary="Manager is reviewing the opened implementation pull request.",
    )


def create_opened_implementation_pull_request_metadata() -> OpenedImplementationPullRequestMetadata:
    """Creates opened implementation pull request metadata for application tests."""

    return OpenedImplementationPullRequestMetadata(
        pull_request_number=91,
        branch_name="feature/issue-56-manager-review-application-entrypoint",
        base_branch_name="main",
        pull_request_title=(
            "Implement issue #56: Integrate manager implementation review application entrypoint"
        ),
        pull_request_body_summary=(
            "Integrate implementation review input, decision, and execution into one "
            "application-layer result."
        ),
        test_evidence=(
            "make test passed for the manager review application flow.",
            "make lint passed for the manager review application flow.",
        ),
        related_issue_identifier="example-owner/multi-bot#56",
        related_issue_title=(
            "Integrate manager implementation review flow through application entrypoint"
        ),
        issue_overview=(
            "Build one strict application entrypoint that connects implementation review "
            "input, decision, and execution."
        ),
        acceptance_criteria=(
            "Return a strict manager implementation review application result.",
            "Expose review payload and workflow state branching from the application result.",
        ),
        single_pull_request_scope=(
            "Limit the work to the manager implementation review application entrypoint."
        ),
    )


def test_review_opened_implementation_pull_request_returns_approve_result() -> None:
    result = review_opened_implementation_pull_request(
        session_summary=create_session_summary(
            RequirementDiscoverySessionState.IMPLEMENTATION_PR_OPEN
        ),
        opened_pull_request_metadata=create_opened_implementation_pull_request_metadata(),
        review_findings=(),
        retry_limit_reason=None,
        escalation_reason=None,
    )

    assert result.is_successful
    assert result.review_input_result.status is ManagerImplementationReviewInputStatus.READY
    assert result.review_in_progress_state is (
        RequirementDiscoverySessionState.IMPLEMENTATION_REVIEW_IN_PROGRESS
    )
    assert result.next_state is RequirementDiscoverySessionState.IMPLEMENTATION_PR_APPROVED
    assert result.review_execution_payload is not None
    assert (
        result.review_execution_payload.review_decision
        is ManagerImplementationReviewDecision.APPROVE
    )


def test_review_opened_implementation_pull_request_returns_requested_changes_result() -> None:
    result = review_opened_implementation_pull_request(
        session_summary=create_session_summary(
            RequirementDiscoverySessionState.IMPLEMENTATION_PR_OPEN
        ),
        opened_pull_request_metadata=create_opened_implementation_pull_request_metadata(),
        review_findings=(
            ManagerImplementationReviewDecisionFinding(
                check_target=ManagerImplementationReviewCheckTarget.ACCEPTANCE_CRITERIA,
                summary=(
                    "The request-changes branch is not exposed from the application-layer result."
                ),
            ),
        ),
        retry_limit_reason=None,
        escalation_reason=None,
    )

    assert result.is_successful
    assert result.decision_result is not None
    assert result.decision_result.decision is ManagerImplementationReviewDecision.REQUEST_CHANGES
    assert result.next_state is RequirementDiscoverySessionState.ENGINEER_CHANGES_REQUESTED
    assert result.review_execution_payload is not None
    assert (
        result.review_execution_payload.review_decision
        is ManagerImplementationReviewDecision.REQUEST_CHANGES
    )


def test_review_opened_implementation_pull_request_returns_input_required_result() -> None:
    result = review_opened_implementation_pull_request(
        session_summary=create_session_summary(
            RequirementDiscoverySessionState.IMPLEMENTATION_PR_OPEN
        ),
        opened_pull_request_metadata=None,
        review_findings=(),
        retry_limit_reason=None,
        escalation_reason=None,
    )

    assert not result.is_successful
    assert (
        result.review_input_result.status is ManagerImplementationReviewInputStatus.INPUT_REQUIRED
    )
    assert result.decision_result is None
    assert result.execution_result is None
    assert result.review_in_progress_state is None
    assert result.next_state is None
    assert result.review_execution_payload is None


def test_review_opened_implementation_pull_request_returns_unsupported_scope_result() -> None:
    result = review_opened_implementation_pull_request(
        session_summary=create_session_summary(
            RequirementDiscoverySessionState.IMPLEMENTATION_PR_OPEN
        ),
        opened_pull_request_metadata=create_opened_implementation_pull_request_metadata(),
        review_findings=(
            ManagerImplementationReviewDecisionFinding(
                check_target=ManagerImplementationReviewCheckTarget.DOCUMENTATION_ALIGNMENT,
                summary="The implementation review scope does not include documentation checks.",
            ),
        ),
        retry_limit_reason=None,
        escalation_reason=None,
        declared_review_targets=(ManagerImplementationReviewCheckTarget.ACCEPTANCE_CRITERIA,),
    )

    assert not result.is_successful
    assert result.decision_result is not None
    assert (
        result.decision_result.status
        is ManagerImplementationReviewDecisionStatus.UNSUPPORTED_REVIEW_SCOPE
    )
    assert result.execution_result is not None
    assert (
        result.execution_result.status
        is ManagerImplementationReviewExecutionStatus.UNSUPPORTED_DECISION
    )
    assert result.review_in_progress_state is (
        RequirementDiscoverySessionState.IMPLEMENTATION_REVIEW_IN_PROGRESS
    )
    assert result.next_state is RequirementDiscoverySessionState.IMPLEMENTATION_REVIEW_IN_PROGRESS
    assert result.review_execution_payload is None


def test_review_opened_implementation_pull_request_returns_user_decision_result() -> None:
    result = review_opened_implementation_pull_request(
        session_summary=create_session_summary(
            RequirementDiscoverySessionState.IMPLEMENTATION_PR_OPEN
        ),
        opened_pull_request_metadata=create_opened_implementation_pull_request_metadata(),
        review_findings=(
            ManagerImplementationReviewDecisionFinding(
                check_target=ManagerImplementationReviewCheckTarget.ACCEPTANCE_CRITERIA,
                summary="The remaining gap needs a product trade-off from the user.",
            ),
        ),
        retry_limit_reason=("The same implementation review gap has already been retried twice."),
        escalation_reason=(
            "Manager needs user direction before finalizing the implementation review."
        ),
    )

    assert result.is_successful
    assert result.decision_result is not None
    assert result.decision_result.decision is (
        ManagerImplementationReviewDecision.USER_DECISION_REQUIRED
    )
    assert result.execution_result is not None
    assert result.execution_result.status is ManagerImplementationReviewExecutionStatus.READY
    assert result.next_state is RequirementDiscoverySessionState.USER_DECISION_REQUIRED
    assert result.review_execution_payload is None
