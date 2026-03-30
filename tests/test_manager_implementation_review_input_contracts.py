from shared_contracts import (
    ImplementationPullRequestCreatePayload,
    ManagerImplementationReviewCheckTarget,
    ManagerImplementationReviewInputStatus,
    ManagerImplementationReviewOperation,
    OpenedImplementationPullRequestMetadata,
    RepositoryReference,
    RequirementDiscoverySessionState,
    RequirementDiscoverySessionSummary,
    RequirementIssueContract,
    RequirementRepositoryContract,
    build_manager_implementation_review_input_result,
)


def create_requirement_repository_contract() -> RequirementRepositoryContract:
    """Creates a repository contract for manager implementation review tests."""

    return RequirementRepositoryContract(
        repository_identifier="repository-123",
        repository_reference=RepositoryReference(
            owner_name="example-owner",
            repository_name="multi-bot",
        ),
    )


def create_requirement_issue_contract() -> RequirementIssueContract:
    """Creates an issue contract for manager implementation review tests."""

    return RequirementIssueContract(
        repository_contract=create_requirement_repository_contract(),
        issue_identifier="issue-456",
        issue_number=45,
        issue_title="Build manager implementation review input from opened implementation PR",
    )


def create_implementation_review_session_summary(
    current_state: RequirementDiscoverySessionState,
) -> RequirementDiscoverySessionSummary:
    """Creates a session summary for manager implementation review tests."""

    return RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=current_state,
        latest_prompt_summary="Manager is ready to review the opened implementation pull request.",
    )


def create_implementation_pull_request_create_payload() -> ImplementationPullRequestCreatePayload:
    """Creates the implementation pull request payload used by review-input tests."""

    return ImplementationPullRequestCreatePayload(
        branch_name="feature/issue-45-manager-implementation-review-input",
        pull_request_title="Implement issue #45: Build manager implementation review input",
        pull_request_body_summary=(
            "Prepare the strict manager input required to review the engineer pull request."
        ),
        test_evidence=(
            "make test passed for the manager implementation review input flow.",
            "make lint passed for the manager implementation review input flow.",
        ),
        related_issue_identifier="example-owner/multi-bot#45",
        related_issue_title=(
            "Build manager implementation review input from opened implementation PR"
        ),
        issue_overview=(
            "Build the strict manager review input model from an opened implementation PR."
        ),
        acceptance_criteria=(
            "Return a strict manager implementation review input model.",
            "Expose review targets and transition context for OP_REVIEW_ENGINEER_PR.",
        ),
        single_pull_request_scope=(
            "Limit the work to strict review input preparation for one implementation PR."
        ),
        target_state=RequirementDiscoverySessionState.IMPLEMENTATION_PR_OPEN,
    )


def create_opened_implementation_pull_request_metadata() -> OpenedImplementationPullRequestMetadata:
    """Creates opened pull request metadata for manager implementation review tests."""

    return OpenedImplementationPullRequestMetadata(
        pull_request_number=77,
        branch_name="feature/issue-45-manager-implementation-review-input",
        pull_request_title="Implement issue #45: Build manager implementation review input",
        pull_request_body_summary=(
            "Prepare the strict manager input required to review the engineer pull request."
        ),
        test_evidence=(
            "make test passed for the manager implementation review input flow.",
            "make lint passed for the manager implementation review input flow.",
        ),
        related_issue_identifier="example-owner/multi-bot#45",
        related_issue_title=(
            "Build manager implementation review input from opened implementation PR"
        ),
        issue_overview=(
            "Build the strict manager review input model from an opened implementation PR."
        ),
        acceptance_criteria=(
            "Return a strict manager implementation review input model.",
            "Expose review targets and transition context for OP_REVIEW_ENGINEER_PR.",
        ),
        single_pull_request_scope=(
            "Limit the work to strict review input preparation for one implementation PR."
        ),
    )


def test_build_manager_implementation_review_input_from_payload_returns_ready() -> None:
    result = build_manager_implementation_review_input_result(
        session_summary=create_implementation_review_session_summary(
            RequirementDiscoverySessionState.IMPLEMENTATION_PR_OPEN
        ),
        pull_request_create_payload=create_implementation_pull_request_create_payload(),
        opened_pull_request_metadata=None,
    )

    assert result.status is ManagerImplementationReviewInputStatus.READY
    assert result.missing_information_items == ()
    assert result.review_input is not None
    assert result.review_input.related_issue_identifier == "example-owner/multi-bot#45"
    assert result.review_input.acceptance_criteria == (
        "Return a strict manager implementation review input model.",
        "Expose review targets and transition context for OP_REVIEW_ENGINEER_PR.",
    )
    assert result.review_input.review_targets == (
        ManagerImplementationReviewCheckTarget.RELATED_ISSUE_TRACEABILITY,
        ManagerImplementationReviewCheckTarget.ACCEPTANCE_CRITERIA,
        ManagerImplementationReviewCheckTarget.SINGLE_PULL_REQUEST_SCOPE,
        ManagerImplementationReviewCheckTarget.TEST_EVIDENCE,
    )
    assert (
        result.review_input.transition_context.required_operation
        is ManagerImplementationReviewOperation.REVIEW_ENGINEER_PR
    )
    assert (
        result.review_input.transition_context.next_state
        is RequirementDiscoverySessionState.IMPLEMENTATION_REVIEW_IN_PROGRESS
    )


def test_build_manager_implementation_review_input_from_opened_metadata_returns_ready() -> None:
    result = build_manager_implementation_review_input_result(
        session_summary=create_implementation_review_session_summary(
            RequirementDiscoverySessionState.IMPLEMENTATION_PR_OPEN
        ),
        pull_request_create_payload=None,
        opened_pull_request_metadata=create_opened_implementation_pull_request_metadata(),
    )

    assert result.status is ManagerImplementationReviewInputStatus.READY
    assert result.review_input is not None
    assert result.review_input.pull_request_number == 77
    assert result.review_input.related_issue_title == (
        "Build manager implementation review input from opened implementation PR"
    )
    assert result.review_input.test_evidence == (
        "make test passed for the manager implementation review input flow.",
        "make lint passed for the manager implementation review input flow.",
    )


def test_build_manager_implementation_review_input_requires_pull_request_source() -> None:
    result = build_manager_implementation_review_input_result(
        session_summary=create_implementation_review_session_summary(
            RequirementDiscoverySessionState.IMPLEMENTATION_PR_OPEN
        ),
        pull_request_create_payload=None,
        opened_pull_request_metadata=None,
    )

    assert result.status is ManagerImplementationReviewInputStatus.INPUT_REQUIRED
    assert result.review_input is None
    assert result.missing_information_items == (
        "implementation pull request payload or opened pull request metadata",
    )


def test_build_manager_implementation_review_input_result_rejects_unsupported_state() -> None:
    result = build_manager_implementation_review_input_result(
        session_summary=create_implementation_review_session_summary(
            RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING
        ),
        pull_request_create_payload=create_implementation_pull_request_create_payload(),
        opened_pull_request_metadata=None,
    )

    assert result.status is ManagerImplementationReviewInputStatus.UNSUPPORTED_STATE
    assert result.review_input is None
