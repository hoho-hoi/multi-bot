from shared_contracts import (
    ManagerRequirementReviewCycleContext,
    ManagerRequirementReviewCycleTrigger,
    ManagerRequirementReviewDecision,
    ManagerRequirementReviewDecisionFinding,
    ManagerRequirementReviewDecisionFindingType,
    ManagerRequirementReviewExecutionStatus,
    ManagerRequirementReviewFocusArea,
    ManagerRequirementReviewInput,
    ManagerRequirementReviewInputStatus,
    MilestonePlanningStatus,
    RepositoryReference,
    RequirementCommentContract,
    RequirementDiscoverySessionState,
    RequirementDiscoverySessionSummary,
    RequirementDocumentType,
    RequirementDocumentUpdateDraft,
    RequirementDocumentUpdateDraftResult,
    RequirementDocumentUpdateDraftStatus,
    RequirementIssueContract,
    RequirementPullRequestCreatePayload,
    RequirementPullRequestOpenStatus,
    RequirementPullRequestPreparationStatus,
    RequirementRepositoryContract,
    UseCaseIdentifier,
    build_manager_requirement_review_decision_result,
    build_manager_requirement_review_execution_result,
    build_manager_requirement_review_input_result,
    build_milestone_planning_result,
    build_requirement_pull_request_open_result,
    build_requirement_pull_request_preparation_result,
)


def create_requirement_repository_contract() -> RequirementRepositoryContract:
    """Creates a repository contract for requirement discovery tests."""

    return RequirementRepositoryContract(
        repository_identifier="repository-123",
        repository_reference=RepositoryReference(
            owner_name="example-owner",
            repository_name="multi-bot",
        ),
    )


def create_requirement_issue_contract() -> RequirementIssueContract:
    """Creates an issue contract for requirement discovery tests."""

    return RequirementIssueContract(
        repository_contract=create_requirement_repository_contract(),
        issue_identifier="issue-456",
        issue_number=5,
        issue_title="Define shared requirement discovery contracts",
    )


def create_requirement_comment_contract() -> RequirementCommentContract:
    """Creates a comment contract for requirement discovery tests."""

    return RequirementCommentContract(
        issue_contract=create_requirement_issue_contract(),
        comment_identifier="comment-789",
        comment_body="Architect needs more detail about session state ownership.",
    )


def create_manager_requirement_review_cycle_context() -> ManagerRequirementReviewCycleContext:
    """Creates a manager review cycle context for requirement review tests."""

    return ManagerRequirementReviewCycleContext(
        review_round_number=1,
        review_cycle_trigger=ManagerRequirementReviewCycleTrigger.PULL_REQUEST_OPENED,
        review_goal_summary="Initial requirement review for the opened pull request.",
    )


def create_manager_requirement_review_input() -> ManagerRequirementReviewInput:
    """Creates strict manager review input for decision-engine tests."""

    return ManagerRequirementReviewInput(
        pull_request_title="docs: finalize requirements for issue #5",
        pull_request_summary=(
            "Update requirement overview, use cases, and architecture boundaries."
        ),
        updated_documents=(
            RequirementDocumentType.REQUIREMENT,
            RequirementDocumentType.USE_CASES,
            RequirementDocumentType.ARCHITECTURE_DIAGRAM,
        ),
        documents_to_review=(
            RequirementDocumentType.REQUIREMENT,
            RequirementDocumentType.USE_CASES,
            RequirementDocumentType.INTERACTION_FLOW,
            RequirementDocumentType.ARCHITECTURE_DIAGRAM,
        ),
        review_cycle_context=create_manager_requirement_review_cycle_context(),
        review_focus_areas=(
            ManagerRequirementReviewFocusArea.REQUIREMENT_OVERVIEW,
            ManagerRequirementReviewFocusArea.INTERACTION_AND_USE_CASE_ALIGNMENT,
            ManagerRequirementReviewFocusArea.ARCHITECTURE_ALIGNMENT,
            ManagerRequirementReviewFocusArea.DOCUMENT_CROSS_CHECK,
        ),
    )


def create_requirement_approved_review_execution_result() -> object:
    """Creates an approved manager review execution result for milestone planning tests."""

    review_session_summary = RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=RequirementDiscoverySessionState.MANAGER_REVIEW_IN_PROGRESS,
        latest_comment_contract=create_requirement_comment_contract(),
        latest_prompt_summary="Manager is executing the requirement review decision.",
    )
    review_input = create_manager_requirement_review_input()
    decision_result = build_manager_requirement_review_decision_result(
        review_input=review_input,
        review_findings=(),
    )

    return build_manager_requirement_review_execution_result(
        session_summary=review_session_summary,
        review_input=review_input,
        decision_result=decision_result,
    )


def test_requirement_issue_contract_returns_repository_qualified_issue_identifier() -> None:
    requirement_issue_contract = create_requirement_issue_contract()

    assert requirement_issue_contract.to_issue_identifier() == "example-owner/multi-bot#5"


def test_requirement_repository_contract_rejects_empty_repository_identifier() -> None:
    try:
        RequirementRepositoryContract(
            repository_identifier=" ",
            repository_reference=RepositoryReference(
                owner_name="example-owner",
                repository_name="multi-bot",
            ),
        )
    except ValueError as error:
        assert str(error) == "repository_identifier must not be empty."
    else:
        raise AssertionError("Expected repository_identifier validation to fail.")


def test_repository_reference_rejects_empty_repository_name() -> None:
    try:
        RequirementRepositoryContract(
            repository_identifier="repository-123",
            repository_reference=RepositoryReference(
                owner_name="example-owner",
                repository_name=" ",
            ),
        )
    except ValueError as error:
        assert str(error) == "repository_name must not be empty."
    else:
        raise AssertionError("Expected repository_name validation to fail.")


def test_requirement_issue_contract_rejects_non_positive_issue_number() -> None:
    try:
        RequirementIssueContract(
            repository_contract=create_requirement_repository_contract(),
            issue_identifier="issue-456",
            issue_number=0,
            issue_title="Define shared requirement discovery contracts",
        )
    except ValueError as error:
        assert str(error) == "issue_number must be greater than zero."
    else:
        raise AssertionError("Expected issue_number validation to fail.")


def test_requirement_comment_contract_rejects_empty_comment_body() -> None:
    try:
        RequirementCommentContract(
            issue_contract=create_requirement_issue_contract(),
            comment_identifier="comment-789",
            comment_body=" ",
        )
    except ValueError as error:
        assert str(error) == "comment_body must not be empty."
    else:
        raise AssertionError("Expected comment_body validation to fail.")


def test_requirement_discovery_session_summary_create_initial_sets_ready_state() -> None:
    requirement_issue_contract = create_requirement_issue_contract()

    session_summary = RequirementDiscoverySessionSummary.create_initial(
        issue_contract=requirement_issue_contract,
    )

    assert session_summary.issue_contract == requirement_issue_contract
    assert session_summary.current_state is RequirementDiscoverySessionState.ISSUE_READY
    assert session_summary.latest_comment_contract is None
    assert session_summary.latest_prompt_summary is None


def test_requirement_discovery_session_summary_rejects_blank_latest_prompt_summary() -> None:
    try:
        RequirementDiscoverySessionSummary(
            issue_contract=create_requirement_issue_contract(),
            current_state=RequirementDiscoverySessionState.DISCOVERY_IN_PROGRESS,
            latest_comment_contract=create_requirement_comment_contract(),
            latest_prompt_summary=" ",
        )
    except ValueError as error:
        assert str(error) == "latest_prompt_summary must not be empty when provided."
    else:
        raise AssertionError("Expected latest_prompt_summary validation to fail.")


def test_requirement_discovery_session_summary_rejects_comment_for_different_issue() -> None:
    latest_comment_contract = create_requirement_comment_contract()
    different_issue_contract = RequirementIssueContract(
        repository_contract=create_requirement_repository_contract(),
        issue_identifier="issue-999",
        issue_number=9,
        issue_title="Different issue title",
    )

    try:
        RequirementDiscoverySessionSummary(
            issue_contract=different_issue_contract,
            current_state=RequirementDiscoverySessionState.DISCOVERY_IN_PROGRESS,
            latest_comment_contract=latest_comment_contract,
            latest_prompt_summary="Architect asked for missing edge cases.",
        )
    except ValueError as error:
        assert str(error) == "latest_comment_contract must reference the same issue_contract."
    else:
        raise AssertionError("Expected latest_comment_contract validation to fail.")


def test_requirement_document_update_draft_result_accepts_ready_status_with_candidates() -> None:
    draft_result = RequirementDocumentUpdateDraftResult(
        status=RequirementDocumentUpdateDraftStatus.READY,
        summary_message="Update the requirement and use-case documents.",
        source_prompt_summary="Clarify project goals and user workflow expectations.",
        update_drafts=(
            RequirementDocumentUpdateDraft(
                document_type=RequirementDocumentType.REQUIREMENT,
                update_focus="Refresh goals, constraints, and success criteria.",
                rationale="The latest prompt clarified project goals.",
            ),
            RequirementDocumentUpdateDraft(
                document_type=RequirementDocumentType.USE_CASES,
                update_focus="Refine the primary actor workflow and edge cases.",
                rationale="The latest prompt described the target user workflow.",
            ),
        ),
    )

    assert draft_result.status is RequirementDocumentUpdateDraftStatus.READY
    assert draft_result.source_prompt_summary is not None
    assert len(draft_result.update_drafts) == 2


def test_requirement_document_update_draft_result_rejects_ready_status_without_candidates() -> None:
    try:
        RequirementDocumentUpdateDraftResult(
            status=RequirementDocumentUpdateDraftStatus.READY,
            summary_message="A summary without candidates is invalid.",
            source_prompt_summary="Clarify the next document updates.",
            update_drafts=(),
        )
    except ValueError as error:
        assert str(error) == "update_drafts must not be empty when status is READY."
    else:
        raise AssertionError("Expected READY draft validation to fail without candidates.")


def test_requirement_document_update_draft_result_rejects_duplicate_document_types() -> None:
    try:
        RequirementDocumentUpdateDraftResult(
            status=RequirementDocumentUpdateDraftStatus.READY,
            summary_message="Duplicate document candidates are not allowed.",
            source_prompt_summary="Clarify requirement updates.",
            update_drafts=(
                RequirementDocumentUpdateDraft(
                    document_type=RequirementDocumentType.REQUIREMENT,
                    update_focus="Refresh the requirement overview.",
                    rationale="The latest prompt changed the goal.",
                ),
                RequirementDocumentUpdateDraft(
                    document_type=RequirementDocumentType.REQUIREMENT,
                    update_focus="Refresh the requirement constraints.",
                    rationale="The latest prompt changed the constraints.",
                ),
            ),
        )
    except ValueError as error:
        assert str(error) == "update_drafts must not contain duplicate document_type values."
    else:
        raise AssertionError("Expected duplicate document_type validation to fail.")


def test_build_requirement_pull_request_preparation_result_returns_ready_draft() -> None:
    session_summary = RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=RequirementDiscoverySessionState.DISCOVERY_IN_PROGRESS,
        latest_comment_contract=create_requirement_comment_contract(),
        latest_prompt_summary=(
            "Clarify the project goal, security constraints, success criteria, "
            "user workflow, and architecture boundaries."
        ),
    )

    result = build_requirement_pull_request_preparation_result(session_summary)

    assert result.status is RequirementPullRequestPreparationStatus.READY
    assert result.source_prompt_summary == session_summary.latest_prompt_summary
    assert result.missing_information_items == ()
    assert result.preparation_draft is not None
    assert (
        str(session_summary.issue_contract.issue_number)
        in result.preparation_draft.pull_request_title
    )
    assert {document_type for document_type in result.preparation_draft.updated_documents} == {
        RequirementDocumentType.REQUIREMENT,
        RequirementDocumentType.USE_CASES,
        RequirementDocumentType.ARCHITECTURE_DIAGRAM,
    }


def test_build_requirement_pull_request_preparation_result_lists_missing_information() -> None:
    session_summary = RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=RequirementDiscoverySessionState.DISCOVERY_IN_PROGRESS,
        latest_comment_contract=create_requirement_comment_contract(),
        latest_prompt_summary="Clarify the user workflow before updating docs.",
    )

    result = build_requirement_pull_request_preparation_result(session_summary)

    assert result.status is RequirementPullRequestPreparationStatus.INPUT_REQUIRED
    assert result.preparation_draft is None
    assert result.missing_information_items == (
        "project goal",
        "constraints",
        "success criteria",
    )


def test_build_requirement_pull_request_open_result_returns_ready_payload() -> None:
    session_summary = RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=RequirementDiscoverySessionState.DISCOVERY_IN_PROGRESS,
        latest_comment_contract=create_requirement_comment_contract(),
        latest_prompt_summary=(
            "Clarify the project goal, security constraints, success criteria, "
            "user workflow, and architecture boundaries."
        ),
    )

    result = build_requirement_pull_request_open_result(session_summary)

    assert result.status is RequirementPullRequestOpenStatus.READY
    assert result.source_prompt_summary == session_summary.latest_prompt_summary
    assert result.next_state is RequirementDiscoverySessionState.PR_OPEN
    assert result.missing_information_items == ()
    assert result.pull_request_create_payload is not None
    assert result.pull_request_create_payload.target_state is (
        RequirementDiscoverySessionState.PR_OPEN
    )
    assert {
        document_type for document_type in result.pull_request_create_payload.updated_documents
    } == {
        RequirementDocumentType.REQUIREMENT,
        RequirementDocumentType.USE_CASES,
        RequirementDocumentType.ARCHITECTURE_DIAGRAM,
    }


def test_build_requirement_pull_request_open_result_returns_additional_question_result() -> None:
    session_summary = RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=RequirementDiscoverySessionState.DISCOVERY_IN_PROGRESS,
        latest_comment_contract=create_requirement_comment_contract(),
        latest_prompt_summary="Clarify the user workflow before updating docs.",
    )

    result = build_requirement_pull_request_open_result(session_summary)

    assert result.status is RequirementPullRequestOpenStatus.INPUT_REQUIRED
    assert result.next_state is RequirementDiscoverySessionState.DISCOVERY_IN_PROGRESS
    assert result.pull_request_create_payload is None
    assert result.missing_information_items == (
        "project goal",
        "constraints",
        "success criteria",
    )


def test_build_manager_requirement_review_input_result_returns_ready_input() -> None:
    session_summary = RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=RequirementDiscoverySessionState.PR_OPEN,
        latest_comment_contract=create_requirement_comment_contract(),
        latest_prompt_summary=(
            "Clarify the project goal, security constraints, success criteria, "
            "user workflow, and architecture boundaries."
        ),
    )

    result = build_manager_requirement_review_input_result(
        session_summary=session_summary,
        pull_request_create_payload=RequirementPullRequestCreatePayload(
            pull_request_title="docs: finalize requirements for issue #5",
            pull_request_body_summary="Update use cases and architecture boundaries.",
            updated_documents=(
                RequirementDocumentType.USE_CASES,
                RequirementDocumentType.ARCHITECTURE_DIAGRAM,
            ),
            target_state=RequirementDiscoverySessionState.PR_OPEN,
        ),
        review_cycle_context=create_manager_requirement_review_cycle_context(),
    )

    assert result.status is ManagerRequirementReviewInputStatus.READY
    assert result.missing_information_items == ()
    assert result.review_input is not None
    assert result.review_input.documents_to_review == (
        RequirementDocumentType.REQUIREMENT,
        RequirementDocumentType.USE_CASES,
        RequirementDocumentType.ARCHITECTURE_DIAGRAM,
    )
    assert result.review_input.review_cycle_context.review_round_number == 1
    assert ManagerRequirementReviewFocusArea.DOCUMENT_CROSS_CHECK in (
        result.review_input.review_focus_areas
    )


def test_build_manager_requirement_review_input_result_requires_updated_documents() -> None:
    session_summary = RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=RequirementDiscoverySessionState.PR_OPEN,
        latest_comment_contract=create_requirement_comment_contract(),
        latest_prompt_summary="Manager is ready to review the opened requirement pull request.",
    )

    result = build_manager_requirement_review_input_result(
        session_summary=session_summary,
        pull_request_create_payload=None,
        review_cycle_context=create_manager_requirement_review_cycle_context(),
    )

    assert result.status is ManagerRequirementReviewInputStatus.INPUT_REQUIRED
    assert result.review_input is None
    assert result.missing_information_items == ("updated requirement documents",)


def test_build_manager_requirement_review_input_result_requires_review_cycle_context() -> None:
    session_summary = RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=RequirementDiscoverySessionState.PR_OPEN,
        latest_comment_contract=create_requirement_comment_contract(),
        latest_prompt_summary="Manager is ready to review the opened requirement pull request.",
    )

    result = build_manager_requirement_review_input_result(
        session_summary=session_summary,
        pull_request_create_payload=RequirementPullRequestCreatePayload(
            pull_request_title="docs: finalize requirements for issue #5",
            pull_request_body_summary="Update the requirement overview and constraints.",
            updated_documents=(RequirementDocumentType.REQUIREMENT,),
            target_state=RequirementDiscoverySessionState.PR_OPEN,
        ),
        review_cycle_context=None,
    )

    assert result.status is ManagerRequirementReviewInputStatus.INPUT_REQUIRED
    assert result.review_input is None
    assert result.missing_information_items == ("review cycle context",)


def test_build_manager_requirement_review_input_result_rejects_unsupported_state() -> None:
    session_summary = RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=RequirementDiscoverySessionState.DISCOVERY_IN_PROGRESS,
        latest_comment_contract=create_requirement_comment_contract(),
        latest_prompt_summary="Manager is ready to review the opened requirement pull request.",
    )

    result = build_manager_requirement_review_input_result(
        session_summary=session_summary,
        pull_request_create_payload=RequirementPullRequestCreatePayload(
            pull_request_title="docs: finalize requirements for issue #5",
            pull_request_body_summary="Update the requirement overview and constraints.",
            updated_documents=(RequirementDocumentType.REQUIREMENT,),
            target_state=RequirementDiscoverySessionState.PR_OPEN,
        ),
        review_cycle_context=create_manager_requirement_review_cycle_context(),
    )

    assert result.status is ManagerRequirementReviewInputStatus.UNSUPPORTED_STATE
    assert result.review_input is None


def test_build_manager_review_decision_result_returns_approve() -> None:
    review_input = create_manager_requirement_review_input()

    result = build_manager_requirement_review_decision_result(
        review_input=review_input,
        review_findings=(),
    )

    assert result.decision is ManagerRequirementReviewDecision.APPROVE
    assert result.requested_changes == ()
    assert result.findings == ()
    assert "approve" in result.review_body_draft.casefold()
    assert review_input.pull_request_title in result.review_body_draft


def test_build_manager_requirement_review_decision_result_returns_requested_changes() -> None:
    review_input = create_manager_requirement_review_input()

    result = build_manager_requirement_review_decision_result(
        review_input=review_input,
        review_findings=(
            ManagerRequirementReviewDecisionFinding(
                finding_type=ManagerRequirementReviewDecisionFindingType.MISSING_INFORMATION,
                focus_area=ManagerRequirementReviewFocusArea.DOCUMENT_CROSS_CHECK,
                summary=("docs/INTERACTION_FLOW.md does not describe the review-cycle retry path."),
                related_documents=(RequirementDocumentType.INTERACTION_FLOW,),
            ),
            ManagerRequirementReviewDecisionFinding(
                finding_type=ManagerRequirementReviewDecisionFindingType.CONTRADICTION,
                focus_area=ManagerRequirementReviewFocusArea.ARCHITECTURE_ALIGNMENT,
                summary=(
                    "docs/ARCHITECTURE_DIAGRAM.md conflicts with docs/REQUIREMENT.md about "
                    "who executes the manager review workflow."
                ),
                related_documents=(
                    RequirementDocumentType.REQUIREMENT,
                    RequirementDocumentType.ARCHITECTURE_DIAGRAM,
                ),
            ),
        ),
    )

    assert result.decision is ManagerRequirementReviewDecision.REQUEST_CHANGES
    assert result.findings == (
        ManagerRequirementReviewDecisionFinding(
            finding_type=ManagerRequirementReviewDecisionFindingType.MISSING_INFORMATION,
            focus_area=ManagerRequirementReviewFocusArea.DOCUMENT_CROSS_CHECK,
            summary="docs/INTERACTION_FLOW.md does not describe the review-cycle retry path.",
            related_documents=(RequirementDocumentType.INTERACTION_FLOW,),
        ),
        ManagerRequirementReviewDecisionFinding(
            finding_type=ManagerRequirementReviewDecisionFindingType.CONTRADICTION,
            focus_area=ManagerRequirementReviewFocusArea.ARCHITECTURE_ALIGNMENT,
            summary=(
                "docs/ARCHITECTURE_DIAGRAM.md conflicts with docs/REQUIREMENT.md about "
                "who executes the manager review workflow."
            ),
            related_documents=(
                RequirementDocumentType.REQUIREMENT,
                RequirementDocumentType.ARCHITECTURE_DIAGRAM,
            ),
        ),
    )
    assert result.requested_changes == (
        (
            "Address DOCUMENT_CROSS_CHECK: docs/INTERACTION_FLOW.md does not describe "
            "the review-cycle retry path."
        ),
        (
            "Address ARCHITECTURE_ALIGNMENT: docs/ARCHITECTURE_DIAGRAM.md conflicts with "
            "docs/REQUIREMENT.md about who executes the manager review workflow."
        ),
    )
    assert "request changes" in result.review_body_draft.casefold()


def test_build_manager_requirement_review_execution_result_returns_approve_payload() -> None:
    session_summary = RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=RequirementDiscoverySessionState.MANAGER_REVIEW_IN_PROGRESS,
        latest_comment_contract=create_requirement_comment_contract(),
        latest_prompt_summary="Manager is executing the requirement review decision.",
    )
    review_input = create_manager_requirement_review_input()
    decision_result = build_manager_requirement_review_decision_result(
        review_input=review_input,
        review_findings=(),
    )

    result = build_manager_requirement_review_execution_result(
        session_summary=session_summary,
        review_input=review_input,
        decision_result=decision_result,
    )

    assert result.status is ManagerRequirementReviewExecutionStatus.READY
    assert result.missing_information_items == ()
    assert result.next_state is RequirementDiscoverySessionState.REQUIREMENT_APPROVED
    assert result.review_execution_payload is not None
    assert (
        result.review_execution_payload.review_decision is ManagerRequirementReviewDecision.APPROVE
    )
    assert result.review_execution_payload.review_body == decision_result.review_body_draft
    assert result.review_execution_payload.pull_request_title == review_input.pull_request_title


def test_build_manager_requirement_review_execution_result_returns_requested_changes_payload() -> (
    None
):
    session_summary = RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=RequirementDiscoverySessionState.MANAGER_REVIEW_IN_PROGRESS,
        latest_comment_contract=create_requirement_comment_contract(),
        latest_prompt_summary="Manager is executing the requirement review decision.",
    )
    review_input = create_manager_requirement_review_input()
    decision_result = build_manager_requirement_review_decision_result(
        review_input=review_input,
        review_findings=(
            ManagerRequirementReviewDecisionFinding(
                finding_type=ManagerRequirementReviewDecisionFindingType.MISSING_INFORMATION,
                focus_area=ManagerRequirementReviewFocusArea.DOCUMENT_CROSS_CHECK,
                summary="docs/INTERACTION_FLOW.md is missing the retry path.",
                related_documents=(RequirementDocumentType.INTERACTION_FLOW,),
            ),
        ),
    )

    result = build_manager_requirement_review_execution_result(
        session_summary=session_summary,
        review_input=review_input,
        decision_result=decision_result,
    )

    assert result.status is ManagerRequirementReviewExecutionStatus.READY
    assert result.next_state is RequirementDiscoverySessionState.REQUIREMENT_CHANGES_REQUESTED
    assert result.review_execution_payload is not None
    assert (
        result.review_execution_payload.review_decision
        is ManagerRequirementReviewDecision.REQUEST_CHANGES
    )
    assert result.review_execution_payload.review_body == decision_result.review_body_draft


def test_build_manager_requirement_review_execution_result_requires_inputs() -> None:
    session_summary = RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=RequirementDiscoverySessionState.MANAGER_REVIEW_IN_PROGRESS,
        latest_comment_contract=create_requirement_comment_contract(),
        latest_prompt_summary="Manager is executing the requirement review decision.",
    )

    result = build_manager_requirement_review_execution_result(
        session_summary=session_summary,
        review_input=None,
        decision_result=None,
    )

    assert result.status is ManagerRequirementReviewExecutionStatus.INPUT_REQUIRED
    assert result.review_execution_payload is None
    assert result.next_state is RequirementDiscoverySessionState.MANAGER_REVIEW_IN_PROGRESS
    assert result.missing_information_items == (
        "manager requirement review input",
        "manager requirement review decision result",
    )


def test_build_manager_requirement_review_execution_result_rejects_unsupported_state() -> None:
    session_summary = RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=RequirementDiscoverySessionState.PR_OPEN,
        latest_comment_contract=create_requirement_comment_contract(),
        latest_prompt_summary="Manager is executing the requirement review decision.",
    )
    review_input = create_manager_requirement_review_input()
    decision_result = build_manager_requirement_review_decision_result(
        review_input=review_input,
        review_findings=(),
    )

    result = build_manager_requirement_review_execution_result(
        session_summary=session_summary,
        review_input=review_input,
        decision_result=decision_result,
    )

    assert result.status is ManagerRequirementReviewExecutionStatus.UNSUPPORTED_STATE
    assert result.review_execution_payload is None
    assert result.next_state is RequirementDiscoverySessionState.PR_OPEN


def test_build_milestone_planning_result_returns_first_delivery_milestone() -> None:
    session_summary = RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=RequirementDiscoverySessionState.REQUIREMENT_APPROVED,
        latest_comment_contract=create_requirement_comment_contract(),
        latest_prompt_summary="Requirement approval completed and delivery planning can begin.",
    )

    result = build_milestone_planning_result(
        session_summary=session_summary,
        requirement_review_execution_result=create_requirement_approved_review_execution_result(),
        requirement_documents_summary=(
            "The approved requirements prioritize the manager planning workflow that defines "
            "the first milestone, creates implementation issues, and hands the backlog to "
            "engineer execution and review."
        ),
    )

    assert result.status is MilestonePlanningStatus.READY
    assert result.next_state is RequirementDiscoverySessionState.MILESTONE_PLANNING
    assert result.missing_information_items == ()
    assert result.milestone_planning_model is not None
    assert result.milestone_planning_model.target_use_cases == (
        UseCaseIdentifier.ORCHESTRATE_DELIVERY_WITH_MANAGER,
        UseCaseIdentifier.IMPLEMENT_ISSUE_WITH_ENGINEER,
    )
    assert len(result.milestone_planning_model.completion_criteria) >= 2


def test_milestone_planning_model_selects_manager_focus_after_requirement_completion() -> None:
    session_summary = RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=RequirementDiscoverySessionState.REQUIREMENT_APPROVED,
        latest_comment_contract=create_requirement_comment_contract(),
        latest_prompt_summary="Requirement approval completed and delivery planning can begin.",
    )

    result = build_milestone_planning_result(
        session_summary=session_summary,
        requirement_review_execution_result=create_requirement_approved_review_execution_result(),
        requirement_documents_summary=(
            "The approved requirements prioritize the manager planning workflow that defines "
            "the first milestone, creates implementation issues, and hands the backlog to "
            "engineer execution and review."
        ),
    )

    milestone_planning_model = result.milestone_planning_model
    if milestone_planning_model is None:
        raise AssertionError("Expected milestone_planning_model to be available.")

    implementation_focus = milestone_planning_model.select_next_implementation_focus(
        completed_use_case=UseCaseIdentifier.DEFINE_REQUIREMENTS_WITH_ARCHITECT,
    )

    assert implementation_focus.use_case_identifier is (
        UseCaseIdentifier.ORCHESTRATE_DELIVERY_WITH_MANAGER
    )
    assert "milestone" in implementation_focus.focus_summary.casefold()


def test_build_milestone_planning_result_requires_supported_delivery_summary() -> None:
    session_summary = RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=RequirementDiscoverySessionState.REQUIREMENT_APPROVED,
        latest_comment_contract=create_requirement_comment_contract(),
        latest_prompt_summary="Requirement approval completed and delivery planning can begin.",
    )

    result = build_milestone_planning_result(
        session_summary=session_summary,
        requirement_review_execution_result=create_requirement_approved_review_execution_result(),
        requirement_documents_summary=(
            "The approved documents only restate the architect requirement discussion "
            "without describing the next delivery workflow."
        ),
    )

    assert result.status is MilestonePlanningStatus.INPUT_REQUIRED
    assert result.milestone_planning_model is None
    assert result.next_state is RequirementDiscoverySessionState.REQUIREMENT_APPROVED
    assert result.missing_information_items == ("target use cases for the first milestone",)


def test_build_milestone_planning_result_rejects_unsupported_state() -> None:
    session_summary = RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=RequirementDiscoverySessionState.PR_OPEN,
        latest_comment_contract=create_requirement_comment_contract(),
        latest_prompt_summary="Requirement review is still in progress.",
    )

    result = build_milestone_planning_result(
        session_summary=session_summary,
        requirement_review_execution_result=create_requirement_approved_review_execution_result(),
        requirement_documents_summary=(
            "The approved requirements prioritize the manager planning workflow."
        ),
    )

    assert result.status is MilestonePlanningStatus.UNSUPPORTED_STATE
    assert result.milestone_planning_model is None
    assert result.next_state is RequirementDiscoverySessionState.PR_OPEN
