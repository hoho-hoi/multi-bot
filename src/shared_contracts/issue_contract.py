from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RepositoryReference:
    """Identifies a GitHub repository.

    Attributes:
        owner_name: GitHub account or organization name.
        repository_name: Repository name.
    """

    owner_name: str
    repository_name: str

    def __post_init__(self) -> None:
        """Validates repository naming fields."""

        if not self.owner_name.strip():
            raise ValueError("owner_name must not be empty.")
        if not self.repository_name.strip():
            raise ValueError("repository_name must not be empty.")

    def to_full_name(self) -> str:
        """Returns the repository full name."""

        return f"{self.owner_name}/{self.repository_name}"


@dataclass(frozen=True, slots=True)
class IssueWorkItemContract:
    """Represents the minimal shared contract for issue-driven work.

    Attributes:
        repository_reference: Repository containing the issue.
        issue_number: Positive GitHub issue number.
        issue_title: Human-readable title describing the work item.
    """

    repository_reference: RepositoryReference
    issue_number: int
    issue_title: str

    def __post_init__(self) -> None:
        """Validates issue metadata."""

        if self.issue_number <= 0:
            raise ValueError("issue_number must be greater than zero.")
        if not self.issue_title.strip():
            raise ValueError("issue_title must not be empty.")

    def to_issue_identifier(self) -> str:
        """Returns a repository-qualified issue identifier."""

        return f"{self.repository_reference.to_full_name()}#{self.issue_number}"
