from shared_contracts import (
    ManagerImplementationReviewCheckTarget,
    ManagerImplementationReviewDecision,
    ManagerImplementationReviewDecisionFinding,
    ManagerImplementationReviewDecisionResult,
    ManagerImplementationReviewDecisionStatus,
    ManagerImplementationReviewInput,
    ManagerImplementationReviewOperation,
    ManagerImplementationReviewTransitionContext,
    RepositoryReference,
    RequirementDiscoverySessionState,
    RequirementDiscoverySessionSummary,
    RequirementIssueContract,
    RequirementRepositoryContract,
    build_manager_implementation_review_decision_result,
    build_manager_implementation_review_execution_result,
)


def create_requirement_repository_contract() -> RequirementRepositoryContract:
    """Creates a repository contract for implementation review execution tests."""

    return RequirementRepositoryContract(
        repository_identifier="repository-123",
        repository_reference=RepositoryReference(
            owner_name="example-owner",
            repository_name="multi-bot",
        ),
    )


def create_requirement_issue_contract() -> RequirementIssueContract:
    """Creates an issue contract for implementation review execution tests."""

    return RequirementIssueContract(
        repository_contract=create_requirement_repository_contract(),
        issue_identifier="issue-456",
        issue_number=46,
        issue_title="Execute implementation review outcome and state transition",
    )


def create_review_session_summary(
    current_state: RequirementDiscoverySessionState,
) -> RequirementDiscoverySessionSummary:
    """Creates a session summary for implementation review execution tests."""

    return RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=current_state,
        latest_prompt_summary="Manager is executing the implementation review outcome.",
    )


def create_manager_implementation_review_input(
    *,
    pull_request_number: int | None = 78,
) -> ManagerImplementationReviewInput:
    """Creates strict manager implementation review input for execution tests."""

    return ManagerImplementationReviewInput(
        pull_request_number=pull_request_number,
        branch_name="feature/issue-46-manager-implementation-review-execution-result",
        base_branch_name="main",
        pull_request_title="Implement issue #46: Execute implementation review outcome",
        pull_request_summary=(
            "Generate the strict execution result for manager implementation review decisions."
        ),
        related_issue_identifier="example-owner/multi-bot#46",
        related_issue_title="Execute implementation review outcome and state transition",
        issue_overview=(
            "Translate the manager implementation review decision into a GitHub review "
            "payload and the next workflow state."
        ),
        acceptance_criteria=(
            "Return a typed implementation review execution result.",
            "Expose review execution payload and next state transitions.",
        ),
        single_pull_request_scope=(
            "Limit the work to shared contract models and execution-result unit tests."
        ),
        test_evidence=(
            "make test passed for the manager implementation review execution flow.",
            "make lint passed for the manager implementation review execution flow.",
        ),
        review_targets=(
            ManagerImplementationReviewCheckTarget.RELATED_ISSUE_TRACEABILITY,
            ManagerImplementationReviewCheckTarget.ACCEPTANCE_CRITERIA,
            ManagerImplementationReviewCheckTarget.SINGLE_PULL_REQUEST_SCOPE,
            ManagerImplementationReviewCheckTarget.BASE_BRANCH_POLICY,
            ManagerImplementationReviewCheckTarget.TEST_EVIDENCE,
            ManagerImplementationReviewCheckTarget.DOCUMENTATION_ALIGNMENT,
        ),
        transition_context=ManagerImplementationReviewTransitionContext(
            current_state=RequirementDiscoverySessionState.IMPLEMENTATION_PR_OPEN,
            next_state=RequirementDiscoverySessionState.IMPLEMENTATION_REVIEW_IN_PROGRESS,
            required_operation=ManagerImplementationReviewOperation.REVIEW_ENGINEER_PR,
        ),
    )


def test_build_manager_implementation_review_execution_result_returns_approve_payload() -> None:
    review_input = create_manager_implementation_review_input()
    decision_result = build_manager_implementation_review_decision_result(
        review_input=review_input,
        review_findings=(),
        retry_limit_reason=None,
        escalation_reason=None,
    )

    result = build_manager_implementation_review_execution_result(
        session_summary=create_review_session_summary(
            RequirementDiscoverySessionState.IMPLEMENTATION_REVIEW_IN_PROGRESS
        ),
        review_input=review_input,
        decision_result=decision_result,
    )

    assert result.status.value == "READY"
    assert result.next_state is RequirementDiscoverySessionState.IMPLEMENTATION_PR_APPROVED
    assert result.review_execution_payload is not None
    assert result.review_execution_payload.pull_request_number == 78
    assert (
        result.review_execution_payload.review_decision
        is ManagerImplementationReviewDecision.APPROVE
    )
    assert result.review_execution_payload.review_body == decision_result.review_body_draft


def test_build_implementation_review_execution_returns_requested_changes_payload() -> None:
    review_input = create_manager_implementation_review_input()
    decision_result = build_manager_implementation_review_decision_result(
        review_input=review_input,
        review_findings=(
            ManagerImplementationReviewDecisionFinding(
                check_target=ManagerImplementationReviewCheckTarget.ACCEPTANCE_CRITERIA,
                summary="The request-changes path is missing in the execution result builder.",
            ),
        ),
        retry_limit_reason=None,
        escalation_reason=None,
    )

    result = build_manager_implementation_review_execution_result(
        session_summary=create_review_session_summary(
            RequirementDiscoverySessionState.IMPLEMENTATION_REVIEW_IN_PROGRESS
        ),
        review_input=review_input,
        decision_result=decision_result,
    )

    assert result.status.value == "READY"
    assert result.next_state is RequirementDiscoverySessionState.ENGINEER_CHANGES_REQUESTED
    assert result.review_execution_payload is not None
    assert (
        result.review_execution_payload.review_decision
        is ManagerImplementationReviewDecision.REQUEST_CHANGES
    )
    assert result.review_execution_payload.review_body == decision_result.review_body_draft


def test_build_implementation_review_execution_returns_user_decision_transition() -> None:
    review_input = create_manager_implementation_review_input()
    decision_result = build_manager_implementation_review_decision_result(
        review_input=review_input,
        review_findings=(
            ManagerImplementationReviewDecisionFinding(
                check_target=ManagerImplementationReviewCheckTarget.DOCUMENTATION_ALIGNMENT,
                summary="The remaining gap requires a product trade-off decision.",
            ),
        ),
        retry_limit_reason="The same implementation review gap has already been retried twice.",
        escalation_reason="Manager needs user direction to resolve the remaining trade-off.",
    )

    result = build_manager_implementation_review_execution_result(
        session_summary=create_review_session_summary(
            RequirementDiscoverySessionState.IMPLEMENTATION_REVIEW_IN_PROGRESS
        ),
        review_input=review_input,
        decision_result=decision_result,
    )

    assert result.status.value == "READY"
    assert result.next_state is RequirementDiscoverySessionState.USER_DECISION_REQUIRED
    assert result.review_execution_payload is None


def test_build_manager_implementation_review_execution_result_requires_review_payload_inputs() -> (
    None
):
    review_input = create_manager_implementation_review_input(pull_request_number=None)
    decision_result = build_manager_implementation_review_decision_result(
        review_input=review_input,
        review_findings=(),
        retry_limit_reason=None,
        escalation_reason=None,
    )

    result = build_manager_implementation_review_execution_result(
        session_summary=create_review_session_summary(
            RequirementDiscoverySessionState.IMPLEMENTATION_REVIEW_IN_PROGRESS
        ),
        review_input=review_input,
        decision_result=decision_result,
    )

    assert result.status.value == "INPUT_REQUIRED"
    assert result.next_state is RequirementDiscoverySessionState.IMPLEMENTATION_REVIEW_IN_PROGRESS
    assert result.review_execution_payload is None
    assert result.missing_information_items == ("implementation pull request number",)


def test_build_manager_implementation_review_execution_result_rejects_unsupported_decision() -> (
    None
):
    review_input = create_manager_implementation_review_input()
    decision_result = ManagerImplementationReviewDecisionResult(
        status=ManagerImplementationReviewDecisionStatus.UNSUPPORTED_REVIEW_SCOPE,
        summary_message="The review findings include an unsupported target.",
        unsupported_check_targets=(ManagerImplementationReviewCheckTarget.DOCUMENTATION_ALIGNMENT,),
    )

    result = build_manager_implementation_review_execution_result(
        session_summary=create_review_session_summary(
            RequirementDiscoverySessionState.IMPLEMENTATION_REVIEW_IN_PROGRESS
        ),
        review_input=review_input,
        decision_result=decision_result,
    )

    assert result.status.value == "UNSUPPORTED_DECISION"
    assert result.next_state is RequirementDiscoverySessionState.IMPLEMENTATION_REVIEW_IN_PROGRESS
    assert result.review_execution_payload is None


def test_build_manager_implementation_review_execution_result_rejects_unsupported_state() -> None:
    review_input = create_manager_implementation_review_input()
    decision_result = build_manager_implementation_review_decision_result(
        review_input=review_input,
        review_findings=(),
        retry_limit_reason=None,
        escalation_reason=None,
    )

    result = build_manager_implementation_review_execution_result(
        session_summary=create_review_session_summary(
            RequirementDiscoverySessionState.IMPLEMENTATION_PR_OPEN
        ),
        review_input=review_input,
        decision_result=decision_result,
    )

    assert result.status.value == "UNSUPPORTED_STATE"
    assert result.next_state is RequirementDiscoverySessionState.IMPLEMENTATION_PR_OPEN
    assert result.review_execution_payload is None
