from shared_contracts import (
    RepositoryReference,
    RequirementCommentContract,
    RequirementDiscoverySessionState,
    RequirementDiscoverySessionSummary,
    RequirementIssueContract,
    RequirementRepositoryContract,
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
