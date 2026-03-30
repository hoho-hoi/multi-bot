from shared_contracts import (
    ImplementationPostMergeDeliveryRoutingReason,
    ImplementationPostMergeDeliveryRoutingStatus,
    RepositoryReference,
    RequirementDiscoverySessionState,
    RequirementDiscoverySessionSummary,
    RequirementIssueContract,
    RequirementRepositoryContract,
    build_implementation_post_merge_delivery_routing_result,
)


def create_requirement_repository_contract() -> RequirementRepositoryContract:
    """Creates a repository contract for post-merge delivery routing tests."""

    return RequirementRepositoryContract(
        repository_identifier="repository-947",
        repository_reference=RepositoryReference(
            owner_name="example-owner",
            repository_name="multi-bot",
        ),
    )


def create_requirement_issue_contract() -> RequirementIssueContract:
    """Creates an issue contract for post-merge delivery routing tests."""

    return RequirementIssueContract(
        repository_contract=create_requirement_repository_contract(),
        issue_identifier="issue-947",
        issue_number=47,
        issue_title="Decide post-merge delivery routing after implementation PR",
    )


def create_requirement_session_summary(
    current_state: RequirementDiscoverySessionState,
) -> RequirementDiscoverySessionSummary:
    """Creates a session summary for post-merge delivery routing tests."""

    return RequirementDiscoverySessionSummary(
        issue_contract=create_requirement_issue_contract(),
        current_state=current_state,
        latest_prompt_summary="Manager is deciding the next delivery state after merge.",
    )


def test_build_post_merge_delivery_routing_result_returns_backlog_ready_result() -> None:
    result = build_implementation_post_merge_delivery_routing_result(
        session_summary=create_requirement_session_summary(
            RequirementDiscoverySessionState.IMPLEMENTATION_PR_MERGED,
        ),
        remaining_milestone_issue_count=2,
        all_requirements_satisfied=False,
    )

    assert result.status is ImplementationPostMergeDeliveryRoutingStatus.READY
    assert result.next_state is RequirementDiscoverySessionState.IMPLEMENTATION_BACKLOG_READY
    assert (
        result.routing_reason
        is ImplementationPostMergeDeliveryRoutingReason.MORE_ISSUES_NEEDED_FOR_MILESTONE
    )
    assert result.remaining_milestone_issue_count == 2
    assert result.all_requirements_satisfied is False


def test_build_post_merge_delivery_routing_result_returns_milestone_planning_result() -> None:
    result = build_implementation_post_merge_delivery_routing_result(
        session_summary=create_requirement_session_summary(
            RequirementDiscoverySessionState.IMPLEMENTATION_PR_MERGED,
        ),
        remaining_milestone_issue_count=0,
        all_requirements_satisfied=False,
    )

    assert result.status is ImplementationPostMergeDeliveryRoutingStatus.READY
    assert result.next_state is RequirementDiscoverySessionState.MILESTONE_PLANNING
    assert result.routing_reason is ImplementationPostMergeDeliveryRoutingReason.MILESTONE_COMPLETED
    assert result.remaining_milestone_issue_count == 0
    assert result.all_requirements_satisfied is False


def test_build_post_merge_delivery_routing_result_returns_delivery_completed_result() -> None:
    result = build_implementation_post_merge_delivery_routing_result(
        session_summary=create_requirement_session_summary(
            RequirementDiscoverySessionState.IMPLEMENTATION_PR_MERGED,
        ),
        remaining_milestone_issue_count=0,
        all_requirements_satisfied=True,
    )

    assert result.status is ImplementationPostMergeDeliveryRoutingStatus.READY
    assert result.next_state is RequirementDiscoverySessionState.DELIVERY_COMPLETED
    assert (
        result.routing_reason
        is ImplementationPostMergeDeliveryRoutingReason.ALL_REQUIREMENTS_SATISFIED
    )
    assert result.remaining_milestone_issue_count == 0
    assert result.all_requirements_satisfied is True


def test_build_post_merge_delivery_routing_result_requires_remaining_task_information() -> None:
    result = build_implementation_post_merge_delivery_routing_result(
        session_summary=create_requirement_session_summary(
            RequirementDiscoverySessionState.IMPLEMENTATION_PR_MERGED,
        ),
        remaining_milestone_issue_count=None,
        all_requirements_satisfied=None,
    )

    assert result.status is ImplementationPostMergeDeliveryRoutingStatus.INPUT_REQUIRED
    assert result.next_state is RequirementDiscoverySessionState.IMPLEMENTATION_PR_MERGED
    assert result.routing_reason is None
    assert result.missing_information_items == (
        "remaining milestone issue count",
        "all requirements satisfied flag",
    )


def test_build_post_merge_delivery_routing_result_rejects_unsupported_state() -> None:
    result = build_implementation_post_merge_delivery_routing_result(
        session_summary=create_requirement_session_summary(
            RequirementDiscoverySessionState.IMPLEMENTATION_PR_APPROVED,
        ),
        remaining_milestone_issue_count=0,
        all_requirements_satisfied=True,
    )

    assert result.status is ImplementationPostMergeDeliveryRoutingStatus.UNSUPPORTED_STATE
    assert result.next_state is RequirementDiscoverySessionState.IMPLEMENTATION_PR_APPROVED
    assert result.routing_reason is None
