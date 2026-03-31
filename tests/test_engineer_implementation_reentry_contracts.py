from shared_contracts import (
    EngineerImplementationReentryInput,
    EngineerImplementationReentryInputStatus,
    EngineerImplementationReentryOperation,
    EngineerImplementationReentryTransitionContext,
    ManagerImplementationReviewCheckTarget,
    ManagerImplementationReviewDecision,
    ManagerImplementationReviewExecutionPayload,
    ManagerImplementationReviewExecutionResult,
    ManagerImplementationReviewExecutionStatus,
    ManagerImplementationReviewInput,
    ManagerImplementationReviewOperation,
    ManagerImplementationReviewTransitionContext,
    RepositoryReference,
    RequirementDiscoverySessionState,
    RequirementDiscoverySessionSummary,
    RequirementIssueContract,
    RequirementRepositoryContract,
    build_engineer_implementation_reentry_input_result,
)


def create_requirement_repository_contract() -> RequirementRepositoryContract:
    """Creates a repository contract for engineer re-entry tests."""

    return RequirementRepositoryContract(
        repository_identifier="repository-123",
        repository_reference=RepositoryReference(
            owner_name="example-owner",
            repository_name="multi-bot",
        ),
    )


def create_requirement_issue_contract() -> RequirementIssueContract:
    """Creates an issue contract for engineer re-entry tests."""

    return RequirementIssueContract(
        repository_contract=create_requirement_repository_contract(),
        issue_identifier="issue-457",
        issue_number=57,
        issue_title="Build engineer re-entry input after manager requests changes",
    )


def create_session_summary(
    current_state: RequirementDiscoverySessionState,
) -> RequirementDiscoverySessionSummary:
    """Creates a session summary for engineer re-entry tests."""

    return RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=current_state,
        latest_prompt_summary=(
            "Manager requested changes on the opened implementation pull request."
        ),
    )


def create_manager_implementation_review_input() -> ManagerImplementationReviewInput:
    """Creates strict manager review input for engineer re-entry tests."""

    return ManagerImplementationReviewInput(
        pull_request_number=91,
        branch_name="feature/issue-57-engineer-reentry-input",
        base_branch_name="main",
        pull_request_title="Implement issue #57: Build engineer re-entry input",
        pull_request_summary=(
            "Build the strict engineer re-entry input after manager requested changes."
        ),
        related_issue_identifier="example-owner/multi-bot#57",
        related_issue_title="Build engineer re-entry input after manager requests changes",
        issue_overview=(
            "Prepare the engineer restart payload from the implementation review outcome."
        ),
        acceptance_criteria=(
            "Return a strict engineer re-entry input model.",
            "Preserve requested changes and workflow transition context for the resumed "
            "pull request.",
        ),
        single_pull_request_scope=(
            "Limit the work to the engineer re-entry input contracts and unit tests."
        ),
        test_evidence=(
            "make test passed for engineer re-entry input contracts.",
            "make lint passed for engineer re-entry input contracts.",
        ),
        review_targets=(
            ManagerImplementationReviewCheckTarget.RELATED_ISSUE_TRACEABILITY,
            ManagerImplementationReviewCheckTarget.ACCEPTANCE_CRITERIA,
        ),
        transition_context=ManagerImplementationReviewTransitionContext(
            current_state=RequirementDiscoverySessionState.IMPLEMENTATION_PR_OPEN,
            next_state=RequirementDiscoverySessionState.IMPLEMENTATION_REVIEW_IN_PROGRESS,
            required_operation=ManagerImplementationReviewOperation.REVIEW_ENGINEER_PR,
        ),
    )


def create_requested_changes_execution_result() -> ManagerImplementationReviewExecutionResult:
    """Creates a review execution result that requested implementation changes."""

    return ManagerImplementationReviewExecutionResult(
        status=ManagerImplementationReviewExecutionStatus.READY,
        summary_message="Manager requested changes on the implementation pull request.",
        next_state=RequirementDiscoverySessionState.ENGINEER_CHANGES_REQUESTED,
        review_execution_payload=ManagerImplementationReviewExecutionPayload(
            pull_request_number=91,
            pull_request_title="Implement issue #57: Build engineer re-entry input",
            review_decision=ManagerImplementationReviewDecision.REQUEST_CHANGES,
            review_body="Please address the missing engineer re-entry contract.",
        ),
    )


def test_build_engineer_implementation_reentry_input_result_returns_ready_input() -> None:
    result = build_engineer_implementation_reentry_input_result(
        session_summary=create_session_summary(
            RequirementDiscoverySessionState.ENGINEER_CHANGES_REQUESTED
        ),
        review_input=create_manager_implementation_review_input(),
        execution_result=create_requested_changes_execution_result(),
        requested_changes=(
            "Preserve the manager requested changes as explicit engineer instructions.",
            "Expose the implementation PR and related issue references in the re-entry input.",
        ),
    )

    assert result.status is EngineerImplementationReentryInputStatus.READY
    assert result.missing_information_items == ()
    assert result.reentry_input is not None
    assert isinstance(result.reentry_input, EngineerImplementationReentryInput)
    assert result.reentry_input.related_issue_identifier == "example-owner/multi-bot#57"
    assert result.reentry_input.pull_request_number == 91
    assert result.reentry_input.requested_changes == (
        "Preserve the manager requested changes as explicit engineer instructions.",
        "Expose the implementation PR and related issue references in the re-entry input.",
    )
    assert result.reentry_input.transition_context == (
        EngineerImplementationReentryTransitionContext(
            current_state=RequirementDiscoverySessionState.ENGINEER_CHANGES_REQUESTED,
            next_state=RequirementDiscoverySessionState.IMPLEMENTATION_PR_OPEN,
            required_operation=(
                EngineerImplementationReentryOperation.UPDATE_IMPLEMENTATION_PULL_REQUEST
            ),
        )
    )


def test_build_engineer_implementation_reentry_input_result_requires_review_metadata() -> None:
    result = build_engineer_implementation_reentry_input_result(
        session_summary=create_session_summary(
            RequirementDiscoverySessionState.ENGINEER_CHANGES_REQUESTED
        ),
        review_input=None,
        execution_result=None,
        requested_changes=(),
    )

    assert result.status is EngineerImplementationReentryInputStatus.INPUT_REQUIRED
    assert result.reentry_input is None
    assert result.missing_information_items == (
        "manager implementation review input",
        "manager implementation review execution result",
        "requested changes",
    )


def test_build_engineer_implementation_reentry_input_result_rejects_unsupported_state() -> None:
    result = build_engineer_implementation_reentry_input_result(
        session_summary=create_session_summary(
            RequirementDiscoverySessionState.IMPLEMENTATION_REVIEW_IN_PROGRESS
        ),
        review_input=create_manager_implementation_review_input(),
        execution_result=create_requested_changes_execution_result(),
        requested_changes=("Preserve the requested changes for engineer restart.",),
    )

    assert result.status is EngineerImplementationReentryInputStatus.UNSUPPORTED_STATE
    assert result.reentry_input is None
