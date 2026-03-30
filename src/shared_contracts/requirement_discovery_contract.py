from dataclasses import dataclass
from enum import StrEnum

from shared_contracts.issue_contract import IssueWorkItemContract, RepositoryReference


class RequirementDiscoverySessionState(StrEnum):
    """Enumerates the minimal requirement discovery workflow states."""

    ISSUE_READY = "STATE_REQUIREMENT_ISSUE_READY"
    DISCOVERY_IN_PROGRESS = "STATE_REQUIREMENT_DISCOVERY_IN_PROGRESS"
    PR_OPEN = "STATE_REQUIREMENT_PR_OPEN"


class WorkerRoleName(StrEnum):
    """Enumerates worker roles that can consume shared work items."""

    ARCHITECT = "architect"
    MANAGER = "manager"
    ENGINEER = "engineer"


class ProviderName(StrEnum):
    """Enumerates provider adapters available to worker-runtime."""

    CURSOR = "cursor"
    OPENAI = "openai"


class RequirementDocumentType(StrEnum):
    """Enumerates requirement documents that can receive draft updates."""

    REQUIREMENT = "docs/REQUIREMENT.md"
    USE_CASES = "docs/USE_CASES.md"
    DOMAIN_ER = "docs/DOMAIN_ER.md"
    INTERACTION_FLOW = "docs/INTERACTION_FLOW.md"
    ARCHITECTURE_DIAGRAM = "docs/ARCHITECTURE_DIAGRAM.md"


class RequirementDocumentUpdateDraftStatus(StrEnum):
    """Enumerates outcomes for document update draft generation."""

    READY = "READY"
    INPUT_REQUIRED = "INPUT_REQUIRED"
    NO_UPDATES_NEEDED = "NO_UPDATES_NEEDED"
    UNSUPPORTED_STATE = "UNSUPPORTED_STATE"


class RequirementPullRequestPreparationStatus(StrEnum):
    """Enumerates outcomes for requirement pull request preparation."""

    READY = "READY"
    INPUT_REQUIRED = "INPUT_REQUIRED"
    UNSUPPORTED_STATE = "UNSUPPORTED_STATE"


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
class RequirementDocumentUpdateDraft:
    """Represents one document update candidate for requirement discovery.

    Attributes:
        document_type: Strictly typed target document under `docs/`.
        update_focus: Human-readable description of what should change.
        rationale: Why the latest requirement intent maps to this document.
    """

    document_type: RequirementDocumentType
    update_focus: str
    rationale: str

    def __post_init__(self) -> None:
        """Validates the draft fields."""

        if not self.update_focus.strip():
            raise ValueError("update_focus must not be empty.")
        if not self.rationale.strip():
            raise ValueError("rationale must not be empty.")


@dataclass(frozen=True, slots=True)
class RequirementDocumentUpdateDraftResult:
    """Represents a typed summary of requirement document update candidates.

    Attributes:
        status: High-level outcome for draft generation.
        summary_message: Human-readable summary for Architect workflow consumers.
        source_prompt_summary: Latest intent summary used to derive the draft.
        update_drafts: Typed document update candidates when status is `READY`.
    """

    status: RequirementDocumentUpdateDraftStatus
    summary_message: str
    source_prompt_summary: str | None = None
    update_drafts: tuple[RequirementDocumentUpdateDraft, ...] = ()

    def __post_init__(self) -> None:
        """Validates result consistency."""

        if not self.summary_message.strip():
            raise ValueError("summary_message must not be empty.")
        if self.source_prompt_summary is not None and not self.source_prompt_summary.strip():
            raise ValueError("source_prompt_summary must not be empty when provided.")

        if self.status is RequirementDocumentUpdateDraftStatus.READY:
            if self.source_prompt_summary is None:
                raise ValueError("source_prompt_summary must be provided when status is READY.")
            if not self.update_drafts:
                raise ValueError("update_drafts must not be empty when status is READY.")
        elif self.update_drafts:
            raise ValueError("update_drafts must be empty unless status is READY.")

        document_types = tuple(draft.document_type for draft in self.update_drafts)
        if len(set(document_types)) != len(document_types):
            raise ValueError("update_drafts must not contain duplicate document_type values.")


@dataclass(frozen=True, slots=True)
class RequirementPullRequestPreparationDraft:
    """Represents the minimum payload needed to prepare a requirement pull request.

    Attributes:
        pull_request_title: Suggested pull request title for the requirement update.
        pull_request_summary: Human-readable summary of the proposed pull request.
        updated_documents: Strictly typed list of documents that should be updated.
    """

    pull_request_title: str
    pull_request_summary: str
    updated_documents: tuple[RequirementDocumentType, ...]

    def __post_init__(self) -> None:
        """Validates the pull request preparation payload."""

        if not self.pull_request_title.strip():
            raise ValueError("pull_request_title must not be empty.")
        if not self.pull_request_summary.strip():
            raise ValueError("pull_request_summary must not be empty.")
        if not self.updated_documents:
            raise ValueError("updated_documents must not be empty.")
        if len(set(self.updated_documents)) != len(self.updated_documents):
            raise ValueError("updated_documents must not contain duplicate values.")


@dataclass(frozen=True, slots=True)
class RequirementPullRequestPreparationResult:
    """Represents whether requirement pull request preparation can proceed.

    Attributes:
        status: High-level preparation outcome for caller-side branching.
        summary_message: Human-readable summary for Architect workflow consumers.
        source_prompt_summary: Latest intent summary used to derive the result.
        missing_information_items: Missing inputs that should be clarified next.
        preparation_draft: Suggested pull request payload when status is `READY`.
    """

    status: RequirementPullRequestPreparationStatus
    summary_message: str
    source_prompt_summary: str | None = None
    missing_information_items: tuple[str, ...] = ()
    preparation_draft: RequirementPullRequestPreparationDraft | None = None

    def __post_init__(self) -> None:
        """Validates result consistency."""

        if not self.summary_message.strip():
            raise ValueError("summary_message must not be empty.")
        if self.source_prompt_summary is not None and not self.source_prompt_summary.strip():
            raise ValueError("source_prompt_summary must not be empty when provided.")

        if any(not missing_item.strip() for missing_item in self.missing_information_items):
            raise ValueError("missing_information_items must not contain empty values.")
        if len(set(self.missing_information_items)) != len(self.missing_information_items):
            raise ValueError("missing_information_items must not contain duplicate values.")

        if self.status is RequirementPullRequestPreparationStatus.READY:
            if self.source_prompt_summary is None:
                raise ValueError("source_prompt_summary must be provided when status is READY.")
            if self.preparation_draft is None:
                raise ValueError("preparation_draft must be provided when status is READY.")
            if self.missing_information_items:
                raise ValueError("missing_information_items must be empty when status is READY.")
            return

        if self.preparation_draft is not None:
            raise ValueError("preparation_draft must be empty unless status is READY.")

        if self.status is RequirementPullRequestPreparationStatus.INPUT_REQUIRED:
            if not self.missing_information_items:
                raise ValueError(
                    "missing_information_items must not be empty when status is INPUT_REQUIRED."
                )
            return

        if self.missing_information_items:
            raise ValueError(
                "missing_information_items must be empty when status is UNSUPPORTED_STATE."
            )


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
class _RequirementDocumentUpdateRule:
    """Defines a keyword-based mapping from intent text to a document draft."""

    document_type: RequirementDocumentType
    keywords: tuple[str, ...]
    update_focus: str
    rationale: str


_NO_UPDATES_INDICATORS = (
    "no document updates",
    "no updates are needed",
    "nothing to update",
    "no changes needed",
    "documents are unchanged",
)

_REQUIREMENT_PREPARATION_ASPECT_RULES = (
    ("project goal", ("goal", "objective", "outcome", "purpose")),
    (
        "constraints",
        (
            "constraint",
            "security",
            "performance",
            "reliability",
            "rollback",
            "logging",
            "audit",
            "observability",
        ),
    ),
    (
        "success criteria",
        ("success criteria", "success", "acceptance", "done", "completion", "approval"),
    ),
)

_REQUIREMENT_DOCUMENT_UPDATE_RULES = (
    _RequirementDocumentUpdateRule(
        document_type=RequirementDocumentType.REQUIREMENT,
        keywords=(
            "goal",
            "scope",
            "success",
            "criteria",
            "constraint",
            "requirement",
            "reliability",
            "logging",
            "audit",
            "observability",
            "security",
            "rollback",
            "edge case",
            "edge-case",
        ),
        update_focus=(
            "Refresh goals, constraints, and acceptance criteria in the main requirement document."
        ),
        rationale=(
            "The latest intent changes requirement-level expectations that "
            "belong in the main requirement summary."
        ),
    ),
    _RequirementDocumentUpdateRule(
        document_type=RequirementDocumentType.USE_CASES,
        keywords=("use case", "workflow", "actor", "journey", "scenario", "user flow"),
        update_focus="Refine actor goals, workflow steps, and representative error cases.",
        rationale=(
            "The latest intent changes user-facing workflows that belong in the use-case catalog."
        ),
    ),
    _RequirementDocumentUpdateRule(
        document_type=RequirementDocumentType.DOMAIN_ER,
        keywords=("entity", "domain", "relationship", "relation", "data model", "schema"),
        update_focus="Update entities, ownership boundaries, and important relationships.",
        rationale=(
            "The latest intent changes domain concepts that belong in the ER documentation."
        ),
    ),
    _RequirementDocumentUpdateRule(
        document_type=RequirementDocumentType.INTERACTION_FLOW,
        keywords=(
            "state",
            "transition",
            "interaction flow",
            "approval flow",
            "sequence",
            "lifecycle",
        ),
        update_focus="Revise workflow states, transitions, and branching conditions.",
        rationale=(
            "The latest intent changes state progression that belongs in the "
            "interaction flow document."
        ),
    ),
    _RequirementDocumentUpdateRule(
        document_type=RequirementDocumentType.ARCHITECTURE_DIAGRAM,
        keywords=(
            "architecture",
            "component",
            "boundary",
            "integration",
            "adapter",
            "provider",
            "runtime",
        ),
        update_focus="Adjust component boundaries and runtime integration responsibilities.",
        rationale=(
            "The latest intent changes structural boundaries that belong in "
            "the architecture diagram."
        ),
    ),
)


def build_requirement_document_update_draft_result(
    session_summary: RequirementDiscoverySessionSummary,
) -> RequirementDocumentUpdateDraftResult:
    """Builds a typed draft summary for requirement document updates.

    Args:
        session_summary: Current requirement discovery session snapshot.

    Returns:
        A typed result describing whether document update candidates are ready.

    Example:
        result = build_requirement_document_update_draft_result(session_summary)
        if result.status is RequirementDocumentUpdateDraftStatus.READY:
            assert result.update_drafts
    """

    if session_summary.current_state is RequirementDiscoverySessionState.ISSUE_READY:
        return RequirementDocumentUpdateDraftResult(
            status=RequirementDocumentUpdateDraftStatus.INPUT_REQUIRED,
            summary_message=(
                "Collect a concrete requirement intent before proposing document updates."
            ),
        )

    if session_summary.current_state is not RequirementDiscoverySessionState.DISCOVERY_IN_PROGRESS:
        return RequirementDocumentUpdateDraftResult(
            status=RequirementDocumentUpdateDraftStatus.UNSUPPORTED_STATE,
            summary_message=(
                "Document update drafts are not supported for workflow state "
                f"{session_summary.current_state.value}."
            ),
        )

    latest_prompt_summary = session_summary.latest_prompt_summary
    if latest_prompt_summary is None:
        return RequirementDocumentUpdateDraftResult(
            status=RequirementDocumentUpdateDraftStatus.INPUT_REQUIRED,
            summary_message=(
                "latest_prompt_summary is required before proposing document updates."
            ),
        )

    normalized_prompt_summary = latest_prompt_summary.casefold()
    if any(indicator in normalized_prompt_summary for indicator in _NO_UPDATES_INDICATORS):
        return RequirementDocumentUpdateDraftResult(
            status=RequirementDocumentUpdateDraftStatus.NO_UPDATES_NEEDED,
            summary_message=(
                "The latest requirement intent explicitly reported that no "
                "document updates are needed."
            ),
            source_prompt_summary=latest_prompt_summary,
        )

    update_drafts = _build_requirement_document_update_drafts(normalized_prompt_summary)
    if not update_drafts:
        return RequirementDocumentUpdateDraftResult(
            status=RequirementDocumentUpdateDraftStatus.NO_UPDATES_NEEDED,
            summary_message=(
                "The latest requirement intent did not map to a supported "
                "document update candidate."
            ),
            source_prompt_summary=latest_prompt_summary,
        )

    return RequirementDocumentUpdateDraftResult(
        status=RequirementDocumentUpdateDraftStatus.READY,
        summary_message=(
            f"Prepared {len(update_drafts)} requirement document update draft candidates."
        ),
        source_prompt_summary=latest_prompt_summary,
        update_drafts=update_drafts,
    )


def build_requirement_pull_request_preparation_result(
    session_summary: RequirementDiscoverySessionSummary,
) -> RequirementPullRequestPreparationResult:
    """Builds a typed readiness result for requirement pull request preparation.

    Args:
        session_summary: Current requirement discovery session snapshot.

    Returns:
        A typed result describing whether requirement pull request preparation is ready.
    """

    if session_summary.current_state is RequirementDiscoverySessionState.ISSUE_READY:
        return RequirementPullRequestPreparationResult(
            status=RequirementPullRequestPreparationStatus.INPUT_REQUIRED,
            summary_message=(
                "Collect concrete requirement details before preparing the requirement "
                "pull request."
            ),
            missing_information_items=_collect_missing_requirement_preparation_items(None),
        )

    if session_summary.current_state is not RequirementDiscoverySessionState.DISCOVERY_IN_PROGRESS:
        return RequirementPullRequestPreparationResult(
            status=RequirementPullRequestPreparationStatus.UNSUPPORTED_STATE,
            summary_message=(
                "Requirement pull request preparation is not supported for workflow state "
                f"{session_summary.current_state.value}."
            ),
        )

    latest_prompt_summary = session_summary.latest_prompt_summary
    if latest_prompt_summary is None:
        return RequirementPullRequestPreparationResult(
            status=RequirementPullRequestPreparationStatus.INPUT_REQUIRED,
            summary_message=(
                "latest_prompt_summary is required before preparing the requirement pull request."
            ),
            missing_information_items=_collect_missing_requirement_preparation_items(None),
        )

    missing_information_items = _collect_missing_requirement_preparation_items(
        latest_prompt_summary.casefold()
    )
    if missing_information_items:
        return RequirementPullRequestPreparationResult(
            status=RequirementPullRequestPreparationStatus.INPUT_REQUIRED,
            summary_message=(
                "Additional requirement clarification is needed before preparing the "
                "requirement pull request."
            ),
            source_prompt_summary=latest_prompt_summary,
            missing_information_items=missing_information_items,
        )

    document_update_draft_result = build_requirement_document_update_draft_result(session_summary)
    if document_update_draft_result.status is not RequirementDocumentUpdateDraftStatus.READY:
        return RequirementPullRequestPreparationResult(
            status=RequirementPullRequestPreparationStatus.INPUT_REQUIRED,
            summary_message=(
                "Identify the requirement documents that should change before preparing "
                "the requirement pull request."
            ),
            source_prompt_summary=latest_prompt_summary,
            missing_information_items=("updated requirement documents",),
        )

    updated_documents = tuple(
        draft.document_type for draft in document_update_draft_result.update_drafts
    )
    issue_contract = session_summary.issue_contract
    return RequirementPullRequestPreparationResult(
        status=RequirementPullRequestPreparationStatus.READY,
        summary_message=(
            "Prepared the minimum requirement pull request information for the latest "
            "discovery outcome."
        ),
        source_prompt_summary=latest_prompt_summary,
        preparation_draft=RequirementPullRequestPreparationDraft(
            pull_request_title=(
                "docs: finalize requirements for issue "
                f"#{issue_contract.issue_number} {issue_contract.issue_title}"
            ),
            pull_request_summary=(
                "Finalize the requirement discovery outcome for issue "
                f"#{issue_contract.issue_number} by updating {len(updated_documents)} "
                f"document(s). Latest intent: {latest_prompt_summary}"
            ),
            updated_documents=updated_documents,
        ),
    )


def _build_requirement_document_update_drafts(
    normalized_prompt_summary: str,
) -> tuple[RequirementDocumentUpdateDraft, ...]:
    """Builds typed draft candidates from a normalized prompt summary."""

    update_drafts: list[RequirementDocumentUpdateDraft] = []
    for update_rule in _REQUIREMENT_DOCUMENT_UPDATE_RULES:
        if any(keyword in normalized_prompt_summary for keyword in update_rule.keywords):
            update_drafts.append(
                RequirementDocumentUpdateDraft(
                    document_type=update_rule.document_type,
                    update_focus=update_rule.update_focus,
                    rationale=update_rule.rationale,
                )
            )
    return tuple(update_drafts)


def _collect_missing_requirement_preparation_items(
    normalized_prompt_summary: str | None,
) -> tuple[str, ...]:
    """Collects missing clarification items for requirement pull request preparation."""

    if normalized_prompt_summary is None:
        return tuple(
            aspect_name for aspect_name, _keywords in _REQUIREMENT_PREPARATION_ASPECT_RULES
        )

    missing_information_items: list[str] = []
    for aspect_name, keywords in _REQUIREMENT_PREPARATION_ASPECT_RULES:
        if not any(keyword in normalized_prompt_summary for keyword in keywords):
            missing_information_items.append(aspect_name)
    return tuple(missing_information_items)


@dataclass(frozen=True, slots=True)
class RequirementDiscoveryWorkItemContract:
    """Represents worker-runtime input for requirement discovery orchestration.

    Attributes:
        issue_work_item_contract: Minimal issue payload understood by worker-runtime.
        session_summary: Requirement discovery session snapshot to execute from.
        role_name: Worker role selected by the control-plane.
        provider_name: Provider adapter selected by the control-plane.
    """

    issue_work_item_contract: IssueWorkItemContract
    session_summary: RequirementDiscoverySessionSummary
    role_name: WorkerRoleName = WorkerRoleName.ARCHITECT
    provider_name: ProviderName = ProviderName.CURSOR

    def __post_init__(self) -> None:
        """Validates that the work item and session refer to the same issue."""

        work_item_identifier = self.issue_work_item_contract.to_issue_identifier()
        session_issue_identifier = self.session_summary.issue_contract.to_issue_identifier()
        if work_item_identifier != session_issue_identifier:
            raise ValueError(
                "issue_work_item_contract must reference the same issue as session_summary."
            )
        if not isinstance(self.role_name, WorkerRoleName):
            raise ValueError("role_name must be a WorkerRoleName value.")
        if not isinstance(self.provider_name, ProviderName):
            raise ValueError("provider_name must be a ProviderName value.")
