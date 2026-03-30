from shared_contracts import (
    EngineerJobInput,
    ImplementationBlockerStatus,
    RepositoryReference,
    RequirementDiscoverySessionState,
    RequirementDiscoverySessionSummary,
    RequirementIssueContract,
    RequirementRepositoryContract,
    UseCaseIdentifier,
    UserDecisionEscalationStatus,
    build_implementation_blocker_result,
    build_user_decision_escalation_result,
)


def create_requirement_repository_contract() -> RequirementRepositoryContract:
    """Creates a repository contract for implementation blocker tests."""

    return RequirementRepositoryContract(
        repository_identifier="repository-123",
        repository_reference=RepositoryReference(
            owner_name="example-owner",
            repository_name="multi-bot",
        ),
    )


def create_requirement_issue_contract() -> RequirementIssueContract:
    """Creates an issue contract for implementation blocker tests."""

    return RequirementIssueContract(
        repository_contract=create_requirement_repository_contract(),
        issue_identifier="issue-456",
        issue_number=32,
        issue_title="Add implementation blocker and user-escalation result models",
    )


def create_engineer_job_input() -> EngineerJobInput:
    """Creates a strict engineer job input for blocker reporting tests."""

    return EngineerJobInput(
        issue_title="Implement blocker and escalation result models",
        issue_overview=(
            "Add typed result models for implementation blockers and user escalations."
        ),
        acceptance_criteria=(
            "Return a typed implementation blocker result.",
            "Return a typed user escalation result.",
        ),
        single_pull_request_scope="Limit the work to shared contract models and unit tests.",
        related_issue_use_case=UseCaseIdentifier.IMPLEMENT_ISSUE_WITH_ENGINEER,
    )


def test_build_implementation_blocker_result_returns_ready_draft() -> None:
    session_summary = RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING,
        latest_prompt_summary="Engineer found a dependency mismatch during implementation.",
    )

    result = build_implementation_blocker_result(
        session_summary=session_summary,
        engineer_job_input=create_engineer_job_input(),
        blocker_summary=(
            "The required manager review retry policy is not modeled, so the escalation "
            "branch cannot be implemented safely."
        ),
    )

    assert result.status is ImplementationBlockerStatus.READY
    assert result.next_state is RequirementDiscoverySessionState.IMPLEMENTATION_BLOCKED
    assert result.missing_information_items == ()
    assert result.implementation_blocker_draft is not None
    assert "dependency mismatch" not in result.summary_message.casefold()
    assert "retry policy" in result.implementation_blocker_draft.comment_body_draft.casefold()
    assert (
        result.implementation_blocker_draft.issue_title
        == "Implement blocker and escalation result models"
    )


def test_build_implementation_blocker_result_requires_input_values() -> None:
    session_summary = RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING,
        latest_prompt_summary="Engineer attempted the implementation and found blockers.",
    )

    result = build_implementation_blocker_result(
        session_summary=session_summary,
        engineer_job_input=None,
        blocker_summary=" ",
    )

    assert result.status is ImplementationBlockerStatus.INPUT_REQUIRED
    assert result.next_state is RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING
    assert result.implementation_blocker_draft is None
    assert result.missing_information_items == (
        "engineer job input",
        "implementation blocker summary",
    )


def test_build_implementation_blocker_result_rejects_unsupported_state() -> None:
    session_summary = RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=RequirementDiscoverySessionState.IMPLEMENTATION_BACKLOG_READY,
        latest_prompt_summary="Engineer has not started the implementation job yet.",
    )

    result = build_implementation_blocker_result(
        session_summary=session_summary,
        engineer_job_input=create_engineer_job_input(),
        blocker_summary="The blocker result should not be created before the engineer job runs.",
    )

    assert result.status is ImplementationBlockerStatus.UNSUPPORTED_STATE
    assert result.next_state is RequirementDiscoverySessionState.IMPLEMENTATION_BACKLOG_READY
    assert result.implementation_blocker_draft is None
    assert result.missing_information_items == ()


def test_build_user_decision_escalation_result_returns_ready_draft() -> None:
    implementation_blocker_result = build_implementation_blocker_result(
        session_summary=RequirementDiscoverySessionSummary(
            issue_contract=create_requirement_issue_contract(),
            current_state=RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING,
            latest_prompt_summary="Engineer found a missing workflow state.",
        ),
        engineer_job_input=create_engineer_job_input(),
        blocker_summary=(
            "The current contracts do not include the state required to finalize the manager "
            "handoff after an implementation blocker."
        ),
    )
    session_summary = RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=RequirementDiscoverySessionState.IMPLEMENTATION_BLOCKED,
        latest_prompt_summary="Manager needs user direction after reviewing the blocker.",
    )

    result = build_user_decision_escalation_result(
        session_summary=session_summary,
        implementation_blocker_result=implementation_blocker_result,
        escalation_summary=(
            "Manager cannot decide whether to reduce scope or introduce the missing review "
            "state without product direction."
        ),
        requested_user_input=(
            "Choose whether to add the missing review-state support now or reduce scope to "
            "blocker reporting only."
        ),
    )

    assert result.status is UserDecisionEscalationStatus.READY
    assert result.next_state is RequirementDiscoverySessionState.USER_DECISION_REQUIRED
    assert result.missing_information_items == ()
    assert result.user_decision_escalation_draft is not None
    assert "product direction" in (
        result.user_decision_escalation_draft.comment_body_draft.casefold()
    )
    assert "reduce scope" in result.user_decision_escalation_draft.comment_body_draft.casefold()


def test_build_user_decision_escalation_result_rejects_unsupported_state() -> None:
    implementation_blocker_result = build_implementation_blocker_result(
        session_summary=RequirementDiscoverySessionSummary(
            issue_contract=create_requirement_issue_contract(),
            current_state=RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING,
            latest_prompt_summary="Engineer found a missing workflow state.",
        ),
        engineer_job_input=create_engineer_job_input(),
        blocker_summary=(
            "The current contracts do not include the state required to finalize the manager "
            "handoff after an implementation blocker."
        ),
    )
    session_summary = RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING,
        latest_prompt_summary="Manager has not moved the workflow into blocked state yet.",
    )

    result = build_user_decision_escalation_result(
        session_summary=session_summary,
        implementation_blocker_result=implementation_blocker_result,
        escalation_summary="Manager still needs a blocked workflow state before escalating.",
        requested_user_input="Wait to ask the user until the blocker has been formally reported.",
    )

    assert result.status is UserDecisionEscalationStatus.UNSUPPORTED_STATE
    assert result.next_state is RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING
    assert result.user_decision_escalation_draft is None
    assert result.missing_information_items == ()


def test_build_user_decision_escalation_result_requires_input_values() -> None:
    session_summary = RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=RequirementDiscoverySessionState.IMPLEMENTATION_BLOCKED,
        latest_prompt_summary="Manager needs user direction after reviewing the blocker.",
    )

    result = build_user_decision_escalation_result(
        session_summary=session_summary,
        implementation_blocker_result=None,
        escalation_summary=" ",
        requested_user_input=" ",
    )

    assert result.status is UserDecisionEscalationStatus.INPUT_REQUIRED
    assert result.next_state is RequirementDiscoverySessionState.IMPLEMENTATION_BLOCKED
    assert result.user_decision_escalation_draft is None
    assert result.missing_information_items == (
        "ready implementation blocker result",
        "user escalation summary",
        "requested user input",
    )
