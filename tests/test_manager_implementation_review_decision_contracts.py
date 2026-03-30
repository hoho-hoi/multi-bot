from shared_contracts import (
    ManagerImplementationReviewCheckTarget,
    ManagerImplementationReviewDecision,
    ManagerImplementationReviewDecisionFinding,
    ManagerImplementationReviewDecisionStatus,
    ManagerImplementationReviewInput,
    ManagerImplementationReviewOperation,
    ManagerImplementationReviewTransitionContext,
    RequirementDiscoverySessionState,
    build_manager_implementation_review_decision_result,
)


def create_manager_implementation_review_input(
    review_targets: tuple[ManagerImplementationReviewCheckTarget, ...] | None = None,
) -> ManagerImplementationReviewInput:
    """Creates strict manager implementation review input for decision tests."""

    if review_targets is None:
        review_targets = (
            ManagerImplementationReviewCheckTarget.RELATED_ISSUE_TRACEABILITY,
            ManagerImplementationReviewCheckTarget.ACCEPTANCE_CRITERIA,
            ManagerImplementationReviewCheckTarget.SINGLE_PULL_REQUEST_SCOPE,
            ManagerImplementationReviewCheckTarget.BASE_BRANCH_POLICY,
            ManagerImplementationReviewCheckTarget.TEST_EVIDENCE,
            ManagerImplementationReviewCheckTarget.DOCUMENTATION_ALIGNMENT,
        )

    return ManagerImplementationReviewInput(
        pull_request_number=78,
        branch_name="feature/issue-48-manager-implementation-review-decision-result",
        base_branch_name="main",
        pull_request_title="Implement issue #48: Decide manager implementation review outcome",
        pull_request_summary=(
            "Add the typed decision result that determines the manager implementation "
            "review outcome."
        ),
        related_issue_identifier="example-owner/multi-bot#48",
        related_issue_title="Decide manager implementation review outcome for opened PR",
        issue_overview=(
            "Determine whether manager implementation review should approve, request "
            "changes, or escalate for user direction."
        ),
        acceptance_criteria=(
            "Return a typed implementation review decision result.",
            "Expose requested changes and user-decision rationale when required.",
        ),
        single_pull_request_scope=(
            "Limit the work to shared contract models and decision-result unit tests."
        ),
        test_evidence=(
            "make test passed for the manager implementation review decision flow.",
            "make lint passed for the manager implementation review decision flow.",
        ),
        review_targets=review_targets,
        transition_context=ManagerImplementationReviewTransitionContext(
            current_state=RequirementDiscoverySessionState.IMPLEMENTATION_PR_OPEN,
            next_state=RequirementDiscoverySessionState.IMPLEMENTATION_REVIEW_IN_PROGRESS,
            required_operation=ManagerImplementationReviewOperation.REVIEW_ENGINEER_PR,
        ),
    )


def test_build_manager_implementation_review_decision_result_returns_approve() -> None:
    review_input = create_manager_implementation_review_input()

    result = build_manager_implementation_review_decision_result(
        review_input=review_input,
        review_findings=(),
        retry_limit_reason=None,
        escalation_reason=None,
    )

    assert result.status is ManagerImplementationReviewDecisionStatus.READY
    assert result.decision is ManagerImplementationReviewDecision.APPROVE
    assert result.findings == ()
    assert result.requested_changes == ()
    assert result.review_body_draft is not None
    assert "approve" in result.review_body_draft.casefold()
    assert review_input.pull_request_title in result.review_body_draft


def test_build_manager_implementation_review_decision_result_returns_requested_changes() -> None:
    review_input = create_manager_implementation_review_input()

    result = build_manager_implementation_review_decision_result(
        review_input=review_input,
        review_findings=(
            ManagerImplementationReviewDecisionFinding(
                check_target=ManagerImplementationReviewCheckTarget.ACCEPTANCE_CRITERIA,
                summary=(
                    "The pull request does not satisfy the acceptance criterion for explicit "
                    "request-changes handling."
                ),
            ),
            ManagerImplementationReviewDecisionFinding(
                check_target=ManagerImplementationReviewCheckTarget.DOCUMENTATION_ALIGNMENT,
                summary=(
                    "docs/INTERACTION_FLOW.md still describes the old implementation review "
                    "handoff without the user-decision branch."
                ),
            ),
        ),
        retry_limit_reason=None,
        escalation_reason=None,
    )

    assert result.status is ManagerImplementationReviewDecisionStatus.READY
    assert result.decision is ManagerImplementationReviewDecision.REQUEST_CHANGES
    assert result.review_body_draft is not None
    assert "request changes" in result.review_body_draft.casefold()
    assert result.requested_changes == (
        (
            "Address ACCEPTANCE_CRITERIA: The pull request does not satisfy the acceptance "
            "criterion for explicit request-changes handling."
        ),
        (
            "Address DOCUMENTATION_ALIGNMENT: docs/INTERACTION_FLOW.md still describes the "
            "old implementation review handoff without the user-decision branch."
        ),
    )


def test_build_manager_implementation_review_decision_result_returns_user_decision_required() -> (
    None
):
    review_input = create_manager_implementation_review_input()

    result = build_manager_implementation_review_decision_result(
        review_input=review_input,
        review_findings=(
            ManagerImplementationReviewDecisionFinding(
                check_target=ManagerImplementationReviewCheckTarget.ACCEPTANCE_CRITERIA,
                summary="The request-changes path has already been used for the same gap.",
            ),
        ),
        retry_limit_reason=(
            "The manager already requested the same acceptance-criteria fix twice, so another "
            "retry would not add new information."
        ),
        escalation_reason=(
            "The remaining implementation-review gap now requires a product trade-off between "
            "accepting reduced scope and extending the workflow contract."
        ),
    )

    assert result.status is ManagerImplementationReviewDecisionStatus.READY
    assert result.decision is ManagerImplementationReviewDecision.USER_DECISION_REQUIRED
    assert result.review_body_draft is None
    assert result.retry_limit_reason is not None
    assert "twice" in result.retry_limit_reason.casefold()
    assert result.escalation_reason is not None
    assert "product trade-off" in result.escalation_reason.casefold()


def test_build_manager_implementation_review_decision_result_requires_review_input() -> None:
    result = build_manager_implementation_review_decision_result(
        review_input=None,
        review_findings=(),
        retry_limit_reason=None,
        escalation_reason=None,
    )

    assert result.status is ManagerImplementationReviewDecisionStatus.INPUT_REQUIRED
    assert result.decision is None
    assert result.review_body_draft is None
    assert result.missing_information_items == ("manager implementation review input",)


def test_build_manager_implementation_review_decision_result_rejects_unsupported_scope() -> None:
    review_input = create_manager_implementation_review_input(
        review_targets=(ManagerImplementationReviewCheckTarget.ACCEPTANCE_CRITERIA,)
    )

    result = build_manager_implementation_review_decision_result(
        review_input=review_input,
        review_findings=(
            ManagerImplementationReviewDecisionFinding(
                check_target=ManagerImplementationReviewCheckTarget.DOCUMENTATION_ALIGNMENT,
                summary=(
                    "docs/ARCHITECTURE_DIAGRAM.md still omits the user-decision branch after "
                    "review retries."
                ),
            ),
        ),
        retry_limit_reason=None,
        escalation_reason=None,
    )

    assert result.status is ManagerImplementationReviewDecisionStatus.UNSUPPORTED_REVIEW_SCOPE
    assert result.decision is None
    assert result.review_body_draft is None
    assert result.unsupported_check_targets == (
        ManagerImplementationReviewCheckTarget.DOCUMENTATION_ALIGNMENT,
    )
