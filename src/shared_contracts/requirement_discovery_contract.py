from dataclasses import dataclass
from enum import StrEnum

from shared_contracts.issue_contract import IssueWorkItemContract, RepositoryReference


class RequirementDiscoverySessionState(StrEnum):
    """Enumerates the minimal requirement discovery workflow states."""

    ISSUE_READY = "STATE_REQUIREMENT_ISSUE_READY"
    DISCOVERY_IN_PROGRESS = "STATE_REQUIREMENT_DISCOVERY_IN_PROGRESS"
    PR_OPEN = "STATE_REQUIREMENT_PR_OPEN"


@dataclass(frozen=True, slots=True)
class RequirementRepositoryContract:
    """Represents repository metadata required for requirement discovery.

    Attributes:
        repository_identifier: Stable GitHub repository identifier.
        repository_reference: Repository owner/name reference.
    """

    repository_identifier: str
    repository_reference: RepositoryReference

    def __post_init__(self) -> None:
        """Validates repository metadata."""

        if not self.repository_identifier.strip():
            raise ValueError("repository_identifier must not be empty.")


@dataclass(frozen=True, slots=True)
class RequirementIssueContract:
    """Represents a requirement discovery issue reference.

    Attributes:
        repository_contract: Repository containing the issue.
        issue_identifier: Stable GitHub issue identifier.
        issue_number: Positive issue number visible in the repository.
        issue_title: Human-readable issue title.
    """

    repository_contract: RequirementRepositoryContract
    issue_identifier: str
    issue_number: int
    issue_title: str

    def __post_init__(self) -> None:
        """Validates issue metadata."""

        if not self.issue_identifier.strip():
            raise ValueError("issue_identifier must not be empty.")
        if self.issue_number <= 0:
            raise ValueError("issue_number must be greater than zero.")
        if not self.issue_title.strip():
            raise ValueError("issue_title must not be empty.")

    def to_issue_identifier(self) -> str:
        """Returns a repository-qualified issue identifier."""

        repository_full_name = self.repository_contract.repository_reference.to_full_name()
        return f"{repository_full_name}#{self.issue_number}"


@dataclass(frozen=True, slots=True)
class RequirementCommentContract:
    """Represents a requirement discovery issue comment.

    Attributes:
        issue_contract: Issue that owns the comment.
        comment_identifier: Stable GitHub comment identifier.
        comment_body: Non-empty comment body.
    """

    issue_contract: RequirementIssueContract
    comment_identifier: str
    comment_body: str

    def __post_init__(self) -> None:
        """Validates comment metadata."""

        if not self.comment_identifier.strip():
            raise ValueError("comment_identifier must not be empty.")
        if not self.comment_body.strip():
            raise ValueError("comment_body must not be empty.")


@dataclass(frozen=True, slots=True)
class RequirementDiscoverySessionSummary:
    """Summarizes the shared requirement discovery session state.

    Attributes:
        issue_contract: Requirement discovery issue being tracked.
        current_state: Current workflow state from INTERACTION_FLOW.
        latest_comment_contract: Latest issue comment when a discussion exists.
        latest_prompt_summary: Short summary of the latest user intent.
    """

    issue_contract: RequirementIssueContract
    current_state: RequirementDiscoverySessionState
    latest_comment_contract: RequirementCommentContract | None = None
    latest_prompt_summary: str | None = None

    def __post_init__(self) -> None:
        """Validates session summary consistency."""

        if not isinstance(self.current_state, RequirementDiscoverySessionState):
            raise ValueError("current_state must be a RequirementDiscoverySessionState value.")
        if self.latest_prompt_summary is not None and not self.latest_prompt_summary.strip():
            raise ValueError("latest_prompt_summary must not be empty when provided.")
        if self.latest_comment_contract is not None:
            session_issue_identifier = self.issue_contract.issue_identifier
            comment_issue_identifier = self.latest_comment_contract.issue_contract.issue_identifier
            if comment_issue_identifier != session_issue_identifier:
                raise ValueError("latest_comment_contract must reference the same issue_contract.")

    @classmethod
    def create_initial(
        cls,
        issue_contract: RequirementIssueContract,
    ) -> "RequirementDiscoverySessionSummary":
        """Creates the initial requirement discovery session summary.

        Args:
            issue_contract: Requirement discovery issue to track.

        Returns:
            A summary positioned at the issue-ready state.
        """

        return cls(
            issue_contract=issue_contract,
            current_state=RequirementDiscoverySessionState.ISSUE_READY,
        )


@dataclass(frozen=True, slots=True)
class RequirementDiscoveryWorkItemContract:
    """Represents worker-runtime input for requirement discovery orchestration.

    Attributes:
        issue_work_item_contract: Minimal issue payload understood by worker-runtime.
        session_summary: Requirement discovery session snapshot to execute from.
    """

    issue_work_item_contract: IssueWorkItemContract
    session_summary: RequirementDiscoverySessionSummary

    def __post_init__(self) -> None:
        """Validates that the work item and session refer to the same issue."""

        work_item_identifier = self.issue_work_item_contract.to_issue_identifier()
        session_issue_identifier = self.session_summary.issue_contract.to_issue_identifier()
        if work_item_identifier != session_issue_identifier:
            raise ValueError(
                "issue_work_item_contract must reference the same issue as session_summary."
            )
