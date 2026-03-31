import re
from dataclasses import dataclass
from enum import StrEnum

from shared_contracts.issue_contract import IssueWorkItemContract, RepositoryReference


class RequirementDiscoverySessionState(StrEnum):
    """Enumerates the minimal requirement discovery workflow states."""

    ISSUE_READY = "STATE_REQUIREMENT_ISSUE_READY"
    DISCOVERY_IN_PROGRESS = "STATE_REQUIREMENT_DISCOVERY_IN_PROGRESS"
    PR_OPEN = "STATE_REQUIREMENT_PR_OPEN"
    MANAGER_REVIEW_IN_PROGRESS = "STATE_MANAGER_REVIEW_IN_PROGRESS"
    REQUIREMENT_CHANGES_REQUESTED = "STATE_REQUIREMENT_CHANGES_REQUESTED"
    REQUIREMENT_APPROVED = "STATE_REQUIREMENT_APPROVED"
    MILESTONE_PLANNING = "STATE_MILESTONE_PLANNING"
    IMPLEMENTATION_BACKLOG_READY = "STATE_IMPLEMENTATION_BACKLOG_READY"
    ENGINEER_JOB_RUNNING = "STATE_ENGINEER_JOB_RUNNING"
    TEST_FIX_IN_PROGRESS = "STATE_TEST_FIX_IN_PROGRESS"
    IMPLEMENTATION_PR_OPEN = "STATE_IMPLEMENTATION_PR_OPEN"
    IMPLEMENTATION_REVIEW_IN_PROGRESS = "STATE_IMPLEMENTATION_REVIEW_IN_PROGRESS"
    ENGINEER_CHANGES_REQUESTED = "STATE_ENGINEER_CHANGES_REQUESTED"
    IMPLEMENTATION_PR_APPROVED = "STATE_IMPLEMENTATION_PR_APPROVED"
    IMPLEMENTATION_PR_MERGED = "STATE_IMPLEMENTATION_PR_MERGED"
    IMPLEMENTATION_BLOCKED = "STATE_IMPLEMENTATION_BLOCKED"
    USER_DECISION_REQUIRED = "STATE_USER_DECISION_REQUIRED"
    DELIVERY_COMPLETED = "STATE_DELIVERY_COMPLETED"


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


class RequirementPullRequestOpenStatus(StrEnum):
    """Enumerates outcomes for requirement pull request payload creation."""

    READY = "READY"
    INPUT_REQUIRED = "INPUT_REQUIRED"
    UNSUPPORTED_STATE = "UNSUPPORTED_STATE"


class ManagerRequirementReviewInputStatus(StrEnum):
    """Enumerates outcomes for manager requirement review input preparation."""

    READY = "READY"
    INPUT_REQUIRED = "INPUT_REQUIRED"
    UNSUPPORTED_STATE = "UNSUPPORTED_STATE"


class ManagerRequirementReviewExecutionStatus(StrEnum):
    """Enumerates outcomes for manager review execution payload preparation."""

    READY = "READY"
    INPUT_REQUIRED = "INPUT_REQUIRED"
    UNSUPPORTED_STATE = "UNSUPPORTED_STATE"


class MilestonePlanningStatus(StrEnum):
    """Enumerates outcomes for building the first delivery milestone."""

    READY = "READY"
    INPUT_REQUIRED = "INPUT_REQUIRED"
    UNSUPPORTED_STATE = "UNSUPPORTED_STATE"


class ImplementationIssueBatchingStatus(StrEnum):
    """Enumerates outcomes for batching milestone output into implementation issues."""

    READY = "READY"
    INPUT_REQUIRED = "INPUT_REQUIRED"
    UNSUPPORTED_STATE = "UNSUPPORTED_STATE"


class ImplementationIssueCreationStatus(StrEnum):
    """Enumerates outcomes for preparing implementation issue creation payloads."""

    READY = "READY"
    INPUT_REQUIRED = "INPUT_REQUIRED"
    UNSUPPORTED_STATE = "UNSUPPORTED_STATE"


class EngineerJobInputStatus(StrEnum):
    """Enumerates outcomes for preparing the initial engineer job input."""

    READY = "READY"
    INPUT_REQUIRED = "INPUT_REQUIRED"
    UNSUPPORTED_STATE = "UNSUPPORTED_STATE"


class EngineerImplementationReentryInputStatus(StrEnum):
    """Enumerates outcomes for preparing engineer re-entry input."""

    READY = "READY"
    INPUT_REQUIRED = "INPUT_REQUIRED"
    UNSUPPORTED_STATE = "UNSUPPORTED_STATE"


class ImplementationPullRequestOpenStatus(StrEnum):
    """Enumerates outcomes for preparing implementation pull request payloads."""

    READY = "READY"
    INPUT_REQUIRED = "INPUT_REQUIRED"
    BLOCKED = "BLOCKED"
    UNSUPPORTED_STATE = "UNSUPPORTED_STATE"


class ManagerImplementationReviewInputStatus(StrEnum):
    """Enumerates outcomes for manager implementation review input preparation."""

    READY = "READY"
    INPUT_REQUIRED = "INPUT_REQUIRED"
    UNSUPPORTED_STATE = "UNSUPPORTED_STATE"


class ManagerImplementationReviewExecutionStatus(StrEnum):
    """Enumerates outcomes for manager implementation review execution preparation."""

    READY = "READY"
    INPUT_REQUIRED = "INPUT_REQUIRED"
    UNSUPPORTED_DECISION = "UNSUPPORTED_DECISION"
    UNSUPPORTED_STATE = "UNSUPPORTED_STATE"


class ImplementationPostMergeDeliveryRoutingStatus(StrEnum):
    """Enumerates outcomes for post-merge delivery routing preparation."""

    READY = "READY"
    INPUT_REQUIRED = "INPUT_REQUIRED"
    UNSUPPORTED_STATE = "UNSUPPORTED_STATE"


class ManagerImplementationReviewDecisionStatus(StrEnum):
    """Enumerates outcomes for manager implementation review decision building."""

    READY = "READY"
    INPUT_REQUIRED = "INPUT_REQUIRED"
    UNSUPPORTED_REVIEW_SCOPE = "UNSUPPORTED_REVIEW_SCOPE"


class ImplementationBlockerStatus(StrEnum):
    """Enumerates outcomes for preparing an implementation blocker report."""

    READY = "READY"
    INPUT_REQUIRED = "INPUT_REQUIRED"
    UNSUPPORTED_STATE = "UNSUPPORTED_STATE"


class UserDecisionEscalationStatus(StrEnum):
    """Enumerates outcomes for preparing a user decision escalation draft."""

    READY = "READY"
    INPUT_REQUIRED = "INPUT_REQUIRED"
    UNSUPPORTED_STATE = "UNSUPPORTED_STATE"


class ManagerImplementationReviewOperation(StrEnum):
    """Enumerates manager operations supported for implementation pull requests."""

    REVIEW_ENGINEER_PR = "OP_REVIEW_ENGINEER_PR"


class EngineerImplementationReentryOperation(StrEnum):
    """Enumerates engineer operations supported after manager requested changes."""

    UPDATE_IMPLEMENTATION_PULL_REQUEST = "OP_UPDATE_IMPLEMENTATION_PULL_REQUEST"


class ManagerImplementationReviewCheckTarget(StrEnum):
    """Enumerates the minimum targets a manager must verify before review execution."""

    RELATED_ISSUE_TRACEABILITY = "RELATED_ISSUE_TRACEABILITY"
    ACCEPTANCE_CRITERIA = "ACCEPTANCE_CRITERIA"
    SINGLE_PULL_REQUEST_SCOPE = "SINGLE_PULL_REQUEST_SCOPE"
    BASE_BRANCH_POLICY = "BASE_BRANCH_POLICY"
    TEST_EVIDENCE = "TEST_EVIDENCE"
    DOCUMENTATION_ALIGNMENT = "DOCUMENTATION_ALIGNMENT"


class ManagerImplementationReviewDecision(StrEnum):
    """Enumerates the implementation review decisions supported for engineer PRs."""

    APPROVE = "APPROVE"
    REQUEST_CHANGES = "REQUEST_CHANGES"
    USER_DECISION_REQUIRED = "USER_DECISION_REQUIRED"


class ImplementationPostMergeDeliveryRoutingReason(StrEnum):
    """Enumerates the supported post-merge delivery routing reasons."""

    MORE_ISSUES_NEEDED_FOR_MILESTONE = "MORE_ISSUES_NEEDED_FOR_MILESTONE"
    MILESTONE_COMPLETED = "MILESTONE_COMPLETED"
    ALL_REQUIREMENTS_SATISFIED = "ALL_REQUIREMENTS_SATISFIED"


class UseCaseIdentifier(StrEnum):
    """Enumerates supported use-case identifiers from `docs/USE_CASES.md`."""

    DEFINE_REQUIREMENTS_WITH_ARCHITECT = "UC_DEFINE_REQUIREMENTS_WITH_ARCHITECT"
    ORCHESTRATE_DELIVERY_WITH_MANAGER = "UC_ORCHESTRATE_DELIVERY_WITH_MANAGER"
    IMPLEMENT_ISSUE_WITH_ENGINEER = "UC_IMPLEMENT_ISSUE_WITH_ENGINEER"


class ManagerRequirementReviewDecision(StrEnum):
    """Enumerates the manager review decisions supported for requirement PRs."""

    APPROVE = "APPROVE"
    REQUEST_CHANGES = "REQUEST_CHANGES"


class ManagerRequirementReviewCycleTrigger(StrEnum):
    """Enumerates events that can start another manager review cycle."""

    PULL_REQUEST_OPENED = "pull_request_opened"
    PULL_REQUEST_UPDATED = "pull_request_updated"
    CHANGES_PUSHED = "changes_pushed"


class ManagerRequirementReviewFocusArea(StrEnum):
    """Enumerates minimal review viewpoints for requirement document consistency."""

    REQUIREMENT_OVERVIEW = "REQUIREMENT_OVERVIEW"
    DOMAIN_MODEL_ALIGNMENT = "DOMAIN_MODEL_ALIGNMENT"
    INTERACTION_AND_USE_CASE_ALIGNMENT = "INTERACTION_AND_USE_CASE_ALIGNMENT"
    ARCHITECTURE_ALIGNMENT = "ARCHITECTURE_ALIGNMENT"
    OPEN_DECISION_HANDLING = "OPEN_DECISION_HANDLING"
    DOCUMENT_CROSS_CHECK = "DOCUMENT_CROSS_CHECK"


class ManagerRequirementReviewDecisionFindingType(StrEnum):
    """Enumerates supported finding types from document consistency review."""

    MISSING_INFORMATION = "MISSING_INFORMATION"
    CONTRADICTION = "CONTRADICTION"


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
class RequirementPullRequestCreatePayload:
    """Represents the typed payload required to open a requirement pull request.

    Attributes:
        pull_request_title: Suggested title for the requirement pull request.
        pull_request_body_summary: Summary content that should appear in the pull request body.
        updated_documents: Strictly typed list of requirement documents that changed.
        target_state: Workflow state reached once the pull request is opened.
    """

    pull_request_title: str
    pull_request_body_summary: str
    updated_documents: tuple[RequirementDocumentType, ...]
    target_state: RequirementDiscoverySessionState

    def __post_init__(self) -> None:
        """Validates the pull request creation payload."""

        if not self.pull_request_title.strip():
            raise ValueError("pull_request_title must not be empty.")
        if not self.pull_request_body_summary.strip():
            raise ValueError("pull_request_body_summary must not be empty.")
        if not self.updated_documents:
            raise ValueError("updated_documents must not be empty.")
        if len(set(self.updated_documents)) != len(self.updated_documents):
            raise ValueError("updated_documents must not contain duplicate values.")
        if self.target_state is not RequirementDiscoverySessionState.PR_OPEN:
            raise ValueError("target_state must be STATE_REQUIREMENT_PR_OPEN.")


@dataclass(frozen=True, slots=True)
class RequirementPullRequestOpenResult:
    """Represents whether a requirement pull request can be opened next.

    Attributes:
        status: High-level outcome for caller-side branching.
        summary_message: Human-readable summary for the next workflow step.
        next_state: Workflow state to continue with after interpreting the result.
        source_prompt_summary: Latest intent summary used to derive the result.
        missing_information_items: Missing inputs that should be clarified next.
        pull_request_create_payload: Strict payload for pull request creation when ready.
    """

    status: RequirementPullRequestOpenStatus
    summary_message: str
    next_state: RequirementDiscoverySessionState
    source_prompt_summary: str | None = None
    missing_information_items: tuple[str, ...] = ()
    pull_request_create_payload: RequirementPullRequestCreatePayload | None = None

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
        if not isinstance(self.next_state, RequirementDiscoverySessionState):
            raise ValueError("next_state must be a RequirementDiscoverySessionState value.")

        if self.status is RequirementPullRequestOpenStatus.READY:
            if self.source_prompt_summary is None:
                raise ValueError("source_prompt_summary must be provided when status is READY.")
            if self.pull_request_create_payload is None:
                raise ValueError(
                    "pull_request_create_payload must be provided when status is READY."
                )
            if self.missing_information_items:
                raise ValueError("missing_information_items must be empty when status is READY.")
            if self.next_state is not RequirementDiscoverySessionState.PR_OPEN:
                raise ValueError(
                    "next_state must be STATE_REQUIREMENT_PR_OPEN when status is READY."
                )
            return

        if self.pull_request_create_payload is not None:
            raise ValueError("pull_request_create_payload must be empty unless status is READY.")

        if self.status is RequirementPullRequestOpenStatus.INPUT_REQUIRED:
            if not self.missing_information_items:
                raise ValueError(
                    "missing_information_items must not be empty when status is INPUT_REQUIRED."
                )
            if self.next_state is not RequirementDiscoverySessionState.DISCOVERY_IN_PROGRESS:
                raise ValueError(
                    "next_state must be STATE_REQUIREMENT_DISCOVERY_IN_PROGRESS when status "
                    "is INPUT_REQUIRED."
                )
            return

        if self.missing_information_items:
            raise ValueError(
                "missing_information_items must be empty when status is UNSUPPORTED_STATE."
            )


@dataclass(frozen=True, slots=True)
class ManagerRequirementReviewCycleContext:
    """Represents the review-cycle metadata for manager requirement review.

    Attributes:
        review_round_number: Positive review round for the current requirement PR.
        review_cycle_trigger: Event that triggered this review cycle.
        review_goal_summary: Short explanation of what this review pass should confirm.
    """

    review_round_number: int
    review_cycle_trigger: ManagerRequirementReviewCycleTrigger
    review_goal_summary: str

    def __post_init__(self) -> None:
        """Validates the review-cycle metadata."""

        if self.review_round_number <= 0:
            raise ValueError("review_round_number must be greater than zero.")
        if not isinstance(self.review_cycle_trigger, ManagerRequirementReviewCycleTrigger):
            raise ValueError(
                "review_cycle_trigger must be a ManagerRequirementReviewCycleTrigger value."
            )
        if not self.review_goal_summary.strip():
            raise ValueError("review_goal_summary must not be empty.")


@dataclass(frozen=True, slots=True)
class ManagerRequirementReviewInput:
    """Represents the strict manager input required for requirement PR review.

    Attributes:
        pull_request_title: Requirement pull request title under review.
        pull_request_summary: Human-readable pull request summary for the review.
        updated_documents: Strictly typed documents changed by the requirement PR.
        documents_to_review: Minimum document set to check for consistency.
        review_cycle_context: Review-cycle metadata for the current review pass.
        review_focus_areas: Minimal viewpoints required for consistency review.
    """

    pull_request_title: str
    pull_request_summary: str
    updated_documents: tuple[RequirementDocumentType, ...]
    documents_to_review: tuple[RequirementDocumentType, ...]
    review_cycle_context: ManagerRequirementReviewCycleContext
    review_focus_areas: tuple[ManagerRequirementReviewFocusArea, ...]

    def __post_init__(self) -> None:
        """Validates the manager review input fields."""

        if not self.pull_request_title.strip():
            raise ValueError("pull_request_title must not be empty.")
        if not self.pull_request_summary.strip():
            raise ValueError("pull_request_summary must not be empty.")
        if not self.updated_documents:
            raise ValueError("updated_documents must not be empty.")
        if len(set(self.updated_documents)) != len(self.updated_documents):
            raise ValueError("updated_documents must not contain duplicate values.")
        if not self.documents_to_review:
            raise ValueError("documents_to_review must not be empty.")
        if len(set(self.documents_to_review)) != len(self.documents_to_review):
            raise ValueError("documents_to_review must not contain duplicate values.")
        if RequirementDocumentType.REQUIREMENT not in self.documents_to_review:
            raise ValueError("documents_to_review must include docs/REQUIREMENT.md.")
        if not set(self.updated_documents).issubset(set(self.documents_to_review)):
            raise ValueError(
                "documents_to_review must include every document listed in updated_documents."
            )
        if not self.review_focus_areas:
            raise ValueError("review_focus_areas must not be empty.")
        if len(set(self.review_focus_areas)) != len(self.review_focus_areas):
            raise ValueError("review_focus_areas must not contain duplicate values.")


@dataclass(frozen=True, slots=True)
class ManagerRequirementReviewInputResult:
    """Represents whether manager requirement review can start immediately.

    Attributes:
        status: High-level outcome for caller-side branching.
        summary_message: Human-readable status summary for orchestration.
        missing_information_items: Missing inputs that must be supplied next.
        review_input: Strict review input when the status is `READY`.
    """

    status: ManagerRequirementReviewInputStatus
    summary_message: str
    missing_information_items: tuple[str, ...] = ()
    review_input: ManagerRequirementReviewInput | None = None

    def __post_init__(self) -> None:
        """Validates result consistency."""

        if not self.summary_message.strip():
            raise ValueError("summary_message must not be empty.")
        if any(not missing_item.strip() for missing_item in self.missing_information_items):
            raise ValueError("missing_information_items must not contain empty values.")
        if len(set(self.missing_information_items)) != len(self.missing_information_items):
            raise ValueError("missing_information_items must not contain duplicate values.")

        if self.status is ManagerRequirementReviewInputStatus.READY:
            if self.review_input is None:
                raise ValueError("review_input must be provided when status is READY.")
            if self.missing_information_items:
                raise ValueError("missing_information_items must be empty when status is READY.")
            return

        if self.review_input is not None:
            raise ValueError("review_input must be empty unless status is READY.")

        if self.status is ManagerRequirementReviewInputStatus.INPUT_REQUIRED:
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
class ManagerRequirementReviewDecisionFinding:
    """Represents one typed finding from the manager requirement review.

    Attributes:
        finding_type: Classification of the issue found during review.
        focus_area: Review viewpoint where the issue was found.
        summary: Human-readable explanation of the missing or conflicting detail.
        related_documents: Documents that should be updated to resolve the issue.
    """

    finding_type: ManagerRequirementReviewDecisionFindingType
    focus_area: ManagerRequirementReviewFocusArea
    summary: str
    related_documents: tuple[RequirementDocumentType, ...]

    def __post_init__(self) -> None:
        """Validates the review finding fields."""

        if not self.summary.strip():
            raise ValueError("summary must not be empty.")
        if not self.related_documents:
            raise ValueError("related_documents must not be empty.")
        if len(set(self.related_documents)) != len(self.related_documents):
            raise ValueError("related_documents must not contain duplicate values.")


@dataclass(frozen=True, slots=True)
class ManagerRequirementReviewDecisionResult:
    """Represents the typed review decision and draft review message.

    Attributes:
        decision: Review decision to pass to the future PR review adapter.
        summary_message: Human-readable summary of the decision.
        review_body_draft: Draft review body ready for the future GitHub review step.
        findings: Typed review findings when changes are required.
        requested_changes: Human-readable change requests derived from the findings.
    """

    decision: ManagerRequirementReviewDecision
    summary_message: str
    review_body_draft: str
    findings: tuple[ManagerRequirementReviewDecisionFinding, ...] = ()
    requested_changes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Validates decision-result consistency."""

        if not self.summary_message.strip():
            raise ValueError("summary_message must not be empty.")
        if not self.review_body_draft.strip():
            raise ValueError("review_body_draft must not be empty.")
        if len(set(self.findings)) != len(self.findings):
            raise ValueError("findings must not contain duplicate values.")
        if any(not change_item.strip() for change_item in self.requested_changes):
            raise ValueError("requested_changes must not contain empty values.")
        if len(set(self.requested_changes)) != len(self.requested_changes):
            raise ValueError("requested_changes must not contain duplicate values.")

        if self.decision is ManagerRequirementReviewDecision.APPROVE:
            if self.findings:
                raise ValueError("findings must be empty when decision is APPROVE.")
            if self.requested_changes:
                raise ValueError("requested_changes must be empty when decision is APPROVE.")
            return

        if not self.findings:
            raise ValueError("findings must not be empty when decision is REQUEST_CHANGES.")
        if not self.requested_changes:
            raise ValueError(
                "requested_changes must not be empty when decision is REQUEST_CHANGES."
            )


@dataclass(frozen=True, slots=True)
class ManagerRequirementReviewExecutionPayload:
    """Represents the minimum payload needed to execute a requirement review.

    Attributes:
        pull_request_title: Requirement pull request title currently under review.
        review_decision: Review decision to submit to the future GitHub adapter.
        review_body: Review body that should be submitted with the review decision.
    """

    pull_request_title: str
    review_decision: ManagerRequirementReviewDecision
    review_body: str

    def __post_init__(self) -> None:
        """Validates the review execution payload."""

        if not self.pull_request_title.strip():
            raise ValueError("pull_request_title must not be empty.")
        if not self.review_body.strip():
            raise ValueError("review_body must not be empty.")


@dataclass(frozen=True, slots=True)
class ManagerRequirementReviewExecutionResult:
    """Represents whether a manager requirement review can execute now.

    Attributes:
        status: High-level outcome for caller-side branching.
        summary_message: Human-readable summary for the next workflow step.
        next_state: Workflow state to continue with after interpreting the result.
        missing_information_items: Missing inputs that must be supplied next.
        review_execution_payload: Strict review execution payload when status is `READY`.
    """

    status: ManagerRequirementReviewExecutionStatus
    summary_message: str
    next_state: RequirementDiscoverySessionState
    missing_information_items: tuple[str, ...] = ()
    review_execution_payload: ManagerRequirementReviewExecutionPayload | None = None

    def __post_init__(self) -> None:
        """Validates result consistency."""

        if not self.summary_message.strip():
            raise ValueError("summary_message must not be empty.")
        if any(not missing_item.strip() for missing_item in self.missing_information_items):
            raise ValueError("missing_information_items must not contain empty values.")
        if len(set(self.missing_information_items)) != len(self.missing_information_items):
            raise ValueError("missing_information_items must not contain duplicate values.")
        if not isinstance(self.next_state, RequirementDiscoverySessionState):
            raise ValueError("next_state must be a RequirementDiscoverySessionState value.")

        if self.status is ManagerRequirementReviewExecutionStatus.READY:
            if self.review_execution_payload is None:
                raise ValueError("review_execution_payload must be provided when status is READY.")
            if self.missing_information_items:
                raise ValueError("missing_information_items must be empty when status is READY.")
            expected_next_state = _build_manager_requirement_review_next_state(
                self.review_execution_payload.review_decision
            )
            if self.next_state is not expected_next_state:
                raise ValueError(
                    "next_state must match the decision carried by review_execution_payload."
                )
            return

        if self.review_execution_payload is not None:
            raise ValueError("review_execution_payload must be empty unless status is READY.")

        if self.status is ManagerRequirementReviewExecutionStatus.INPUT_REQUIRED:
            if not self.missing_information_items:
                raise ValueError(
                    "missing_information_items must not be empty when status is INPUT_REQUIRED."
                )
            if self.next_state is not RequirementDiscoverySessionState.MANAGER_REVIEW_IN_PROGRESS:
                raise ValueError(
                    "next_state must be STATE_MANAGER_REVIEW_IN_PROGRESS when status "
                    "is INPUT_REQUIRED."
                )
            return

        if self.missing_information_items:
            raise ValueError(
                "missing_information_items must be empty when status is UNSUPPORTED_STATE."
            )


@dataclass(frozen=True, slots=True)
class MilestoneImplementationFocus:
    """Represents one prioritized implementation focus inside a milestone.

    Attributes:
        use_case_identifier: Use case that this focus advances next.
        focus_summary: Human-readable explanation of the next vertical slice.
        rationale: Why this focus should be prioritized now.
    """

    use_case_identifier: UseCaseIdentifier
    focus_summary: str
    rationale: str

    def __post_init__(self) -> None:
        """Validates the focus fields."""

        if not self.focus_summary.strip():
            raise ValueError("focus_summary must not be empty.")
        if not self.rationale.strip():
            raise ValueError("rationale must not be empty.")


@dataclass(frozen=True, slots=True)
class MilestonePlanningModel:
    """Represents the first post-approval milestone in a strict typed form.

    Attributes:
        milestone_goal: Human-readable goal for the first delivery milestone.
        completion_criteria: Verifiable outcomes required to finish the milestone.
        target_use_cases: Use cases intentionally covered by the milestone.
        implementation_focuses: Ordered focus list for immediate execution.

    Example:
        focus = milestone_planning_model.select_next_implementation_focus(
            completed_use_case=UseCaseIdentifier.DEFINE_REQUIREMENTS_WITH_ARCHITECT,
        )
        assert focus.use_case_identifier is UseCaseIdentifier.ORCHESTRATE_DELIVERY_WITH_MANAGER
    """

    milestone_goal: str
    completion_criteria: tuple[str, ...]
    target_use_cases: tuple[UseCaseIdentifier, ...]
    implementation_focuses: tuple[MilestoneImplementationFocus, ...]

    def __post_init__(self) -> None:
        """Validates the milestone planning model."""

        if not self.milestone_goal.strip():
            raise ValueError("milestone_goal must not be empty.")
        if not self.completion_criteria:
            raise ValueError("completion_criteria must not be empty.")
        if any(
            not completion_criterion.strip() for completion_criterion in self.completion_criteria
        ):
            raise ValueError("completion_criteria must not contain empty values.")
        if len(set(self.completion_criteria)) != len(self.completion_criteria):
            raise ValueError("completion_criteria must not contain duplicate values.")
        if not self.target_use_cases:
            raise ValueError("target_use_cases must not be empty.")
        if len(set(self.target_use_cases)) != len(self.target_use_cases):
            raise ValueError("target_use_cases must not contain duplicate values.")
        if not self.implementation_focuses:
            raise ValueError("implementation_focuses must not be empty.")
        focus_use_case_identifiers = tuple(
            implementation_focus.use_case_identifier
            for implementation_focus in self.implementation_focuses
        )
        if len(set(focus_use_case_identifiers)) != len(focus_use_case_identifiers):
            raise ValueError(
                "implementation_focuses must not contain duplicate use_case_identifier values."
            )
        if not set(focus_use_case_identifiers).issubset(set(self.target_use_cases)):
            raise ValueError(
                "implementation_focuses must reference only use cases listed in target_use_cases."
            )

    def select_next_implementation_focus(
        self,
        completed_use_case: UseCaseIdentifier,
    ) -> MilestoneImplementationFocus:
        """Returns the next prioritized implementation focus after a completed use case."""

        for implementation_focus in self.implementation_focuses:
            if implementation_focus.use_case_identifier is not completed_use_case:
                return implementation_focus

        raise ValueError("No remaining implementation focus is available after completed_use_case.")


@dataclass(frozen=True, slots=True)
class MilestonePlanningResult:
    """Represents whether the first delivery milestone can be planned now.

    Attributes:
        status: High-level planning outcome for caller-side branching.
        summary_message: Human-readable status summary for orchestration.
        next_state: Workflow state after interpreting the planning result.
        missing_information_items: Missing inputs required to plan the milestone.
        milestone_planning_model: Strict milestone model when status is `READY`.
    """

    status: MilestonePlanningStatus
    summary_message: str
    next_state: RequirementDiscoverySessionState
    missing_information_items: tuple[str, ...] = ()
    milestone_planning_model: MilestonePlanningModel | None = None

    def __post_init__(self) -> None:
        """Validates result consistency."""

        if not self.summary_message.strip():
            raise ValueError("summary_message must not be empty.")
        if any(not missing_item.strip() for missing_item in self.missing_information_items):
            raise ValueError("missing_information_items must not contain empty values.")
        if len(set(self.missing_information_items)) != len(self.missing_information_items):
            raise ValueError("missing_information_items must not contain duplicate values.")
        if not isinstance(self.next_state, RequirementDiscoverySessionState):
            raise ValueError("next_state must be a RequirementDiscoverySessionState value.")

        if self.status is MilestonePlanningStatus.READY:
            if self.milestone_planning_model is None:
                raise ValueError("milestone_planning_model must be provided when status is READY.")
            if self.missing_information_items:
                raise ValueError("missing_information_items must be empty when status is READY.")
            if self.next_state is not RequirementDiscoverySessionState.MILESTONE_PLANNING:
                raise ValueError(
                    "next_state must be STATE_MILESTONE_PLANNING when status is READY."
                )
            return

        if self.milestone_planning_model is not None:
            raise ValueError("milestone_planning_model must be empty unless status is READY.")

        if self.status is MilestonePlanningStatus.INPUT_REQUIRED:
            if not self.missing_information_items:
                raise ValueError(
                    "missing_information_items must not be empty when status is INPUT_REQUIRED."
                )
            if self.next_state is not RequirementDiscoverySessionState.REQUIREMENT_APPROVED:
                raise ValueError(
                    "next_state must be STATE_REQUIREMENT_APPROVED when status is INPUT_REQUIRED."
                )
            return

        if self.missing_information_items:
            raise ValueError(
                "missing_information_items must be empty when status is UNSUPPORTED_STATE."
            )


@dataclass(frozen=True, slots=True)
class ImplementationIssueDraft:
    """Represents one engineer-sized implementation issue draft.

    Attributes:
        target_use_case: Use case that this draft advances from the milestone plan.
        issue_title: Suggested GitHub issue title for the draft.
        issue_summary: Human-readable issue overview for Manager review and Engineer handoff.
        acceptance_criteria: Verifiable outcomes that keep the work within one pull request.
        single_pull_request_scope: Explicit boundary that defines the intended single-PR slice.

    Example:
        implementation_issue_draft = ImplementationIssueDraft(
            target_use_case=UseCaseIdentifier.ORCHESTRATE_DELIVERY_WITH_MANAGER,
            issue_title="Implement manager milestone backlog drafting",
            issue_summary="Convert the first milestone into engineer-ready issue drafts.",
            acceptance_criteria=("A strict batching result is returned.",),
            single_pull_request_scope="Limit the change to typed batching only.",
        )
        assert implementation_issue_draft.target_use_case is (
            UseCaseIdentifier.ORCHESTRATE_DELIVERY_WITH_MANAGER
        )
    """

    target_use_case: UseCaseIdentifier
    issue_title: str
    issue_summary: str
    acceptance_criteria: tuple[str, ...]
    single_pull_request_scope: str

    def __post_init__(self) -> None:
        """Validates issue-draft consistency."""

        if not self.issue_title.strip():
            raise ValueError("issue_title must not be empty.")
        if not self.issue_summary.strip():
            raise ValueError("issue_summary must not be empty.")
        if not self.acceptance_criteria:
            raise ValueError("acceptance_criteria must not be empty.")
        if any(
            not acceptance_criterion.strip() for acceptance_criterion in self.acceptance_criteria
        ):
            raise ValueError("acceptance_criteria must not contain empty values.")
        if len(set(self.acceptance_criteria)) != len(self.acceptance_criteria):
            raise ValueError("acceptance_criteria must not contain duplicate values.")
        if not self.single_pull_request_scope.strip():
            raise ValueError("single_pull_request_scope must not be empty.")


@dataclass(frozen=True, slots=True)
class ImplementationIssueBatchingResult:
    """Represents whether milestone output can be split into implementation issues.

    Attributes:
        status: High-level batching outcome for caller-side branching.
        summary_message: Human-readable batching summary for orchestration.
        next_state: Workflow state after interpreting the batching result.
        missing_information_items: Missing inputs required before batching can proceed.
        implementation_issue_drafts: Engineer-ready drafts when status is `READY`.
    """

    status: ImplementationIssueBatchingStatus
    summary_message: str
    next_state: RequirementDiscoverySessionState
    missing_information_items: tuple[str, ...] = ()
    implementation_issue_drafts: tuple[ImplementationIssueDraft, ...] = ()

    def __post_init__(self) -> None:
        """Validates batching-result consistency."""

        if not self.summary_message.strip():
            raise ValueError("summary_message must not be empty.")
        if any(not missing_item.strip() for missing_item in self.missing_information_items):
            raise ValueError("missing_information_items must not contain empty values.")
        if len(set(self.missing_information_items)) != len(self.missing_information_items):
            raise ValueError("missing_information_items must not contain duplicate values.")
        if len(set(self.implementation_issue_drafts)) != len(self.implementation_issue_drafts):
            raise ValueError("implementation_issue_drafts must not contain duplicate values.")
        if not isinstance(self.next_state, RequirementDiscoverySessionState):
            raise ValueError("next_state must be a RequirementDiscoverySessionState value.")

        if self.status is ImplementationIssueBatchingStatus.READY:
            if not self.implementation_issue_drafts:
                raise ValueError(
                    "implementation_issue_drafts must not be empty when status is READY."
                )
            if self.missing_information_items:
                raise ValueError("missing_information_items must be empty when status is READY.")
            if self.next_state is not RequirementDiscoverySessionState.MILESTONE_PLANNING:
                raise ValueError(
                    "next_state must be STATE_MILESTONE_PLANNING when status is READY."
                )
            return

        if self.implementation_issue_drafts:
            raise ValueError("implementation_issue_drafts must be empty unless status is READY.")

        if self.status is ImplementationIssueBatchingStatus.INPUT_REQUIRED:
            if not self.missing_information_items:
                raise ValueError(
                    "missing_information_items must not be empty when status is INPUT_REQUIRED."
                )
            if self.next_state is not RequirementDiscoverySessionState.MILESTONE_PLANNING:
                raise ValueError(
                    "next_state must be STATE_MILESTONE_PLANNING when status is INPUT_REQUIRED."
                )
            return

        if self.missing_information_items:
            raise ValueError(
                "missing_information_items must be empty when status is UNSUPPORTED_STATE."
            )


@dataclass(frozen=True, slots=True)
class ImplementationIssueCreatePayload:
    """Represents the typed payload required to create an implementation issue.

    Attributes:
        target_use_case: Use case that the created implementation issue advances.
        issue_title: Suggested GitHub issue title.
        issue_overview: Overview that should appear in the issue body.
        acceptance_criteria: Verifiable outcomes copied into the issue body.
        single_pull_request_scope: Explicit boundary that keeps the work within one pull request.
        target_state: Workflow state reached once the implementation issue batch is ready.
    """

    target_use_case: UseCaseIdentifier
    issue_title: str
    issue_overview: str
    acceptance_criteria: tuple[str, ...]
    single_pull_request_scope: str
    target_state: RequirementDiscoverySessionState

    def __post_init__(self) -> None:
        """Validates the implementation issue creation payload."""

        if not isinstance(self.target_use_case, UseCaseIdentifier):
            raise ValueError("target_use_case must be a UseCaseIdentifier value.")
        if not self.issue_title.strip():
            raise ValueError("issue_title must not be empty.")
        if not self.issue_overview.strip():
            raise ValueError("issue_overview must not be empty.")
        if not self.acceptance_criteria:
            raise ValueError("acceptance_criteria must not be empty.")
        if any(
            not acceptance_criterion.strip() for acceptance_criterion in self.acceptance_criteria
        ):
            raise ValueError("acceptance_criteria must not contain empty values.")
        if len(set(self.acceptance_criteria)) != len(self.acceptance_criteria):
            raise ValueError("acceptance_criteria must not contain duplicate values.")
        if not self.single_pull_request_scope.strip():
            raise ValueError("single_pull_request_scope must not be empty.")
        if self.target_state is not RequirementDiscoverySessionState.IMPLEMENTATION_BACKLOG_READY:
            raise ValueError("target_state must be STATE_IMPLEMENTATION_BACKLOG_READY.")


@dataclass(frozen=True, slots=True)
class ImplementationIssueCreationResult:
    """Represents whether implementation issue creation payloads can be emitted next.

    Attributes:
        status: High-level outcome for caller-side branching.
        summary_message: Human-readable summary for orchestration.
        next_state: Workflow state after interpreting the result.
        missing_information_items: Missing inputs required before payload emission can proceed.
        issue_create_payloads: Strict payloads for GitHub issue creation when ready.
    """

    status: ImplementationIssueCreationStatus
    summary_message: str
    next_state: RequirementDiscoverySessionState
    missing_information_items: tuple[str, ...] = ()
    issue_create_payloads: tuple[ImplementationIssueCreatePayload, ...] = ()

    def __post_init__(self) -> None:
        """Validates creation-result consistency."""

        if not self.summary_message.strip():
            raise ValueError("summary_message must not be empty.")
        if any(not missing_item.strip() for missing_item in self.missing_information_items):
            raise ValueError("missing_information_items must not contain empty values.")
        if len(set(self.missing_information_items)) != len(self.missing_information_items):
            raise ValueError("missing_information_items must not contain duplicate values.")
        if len(set(self.issue_create_payloads)) != len(self.issue_create_payloads):
            raise ValueError("issue_create_payloads must not contain duplicate values.")
        if not isinstance(self.next_state, RequirementDiscoverySessionState):
            raise ValueError("next_state must be a RequirementDiscoverySessionState value.")

        if self.status is ImplementationIssueCreationStatus.READY:
            if not self.issue_create_payloads:
                raise ValueError("issue_create_payloads must not be empty when status is READY.")
            if self.missing_information_items:
                raise ValueError("missing_information_items must be empty when status is READY.")
            if self.next_state is not RequirementDiscoverySessionState.IMPLEMENTATION_BACKLOG_READY:
                raise ValueError(
                    "next_state must be STATE_IMPLEMENTATION_BACKLOG_READY when status is READY."
                )
            return

        if self.issue_create_payloads:
            raise ValueError("issue_create_payloads must be empty unless status is READY.")

        if self.status is ImplementationIssueCreationStatus.INPUT_REQUIRED:
            if not self.missing_information_items:
                raise ValueError(
                    "missing_information_items must not be empty when status is INPUT_REQUIRED."
                )
            if self.next_state is not RequirementDiscoverySessionState.MILESTONE_PLANNING:
                raise ValueError(
                    "next_state must be STATE_MILESTONE_PLANNING when status is INPUT_REQUIRED."
                )
            return

        if self.missing_information_items:
            raise ValueError(
                "missing_information_items must be empty when status is UNSUPPORTED_STATE."
            )


@dataclass(frozen=True, slots=True)
class EngineerExecutionFocus:
    """Represents the initial execution focus for one engineer job.

    Attributes:
        use_case_identifier: Engineer use case that the job must execute.
        related_issue_use_case: Use case advanced by the source implementation issue.
        focus_summary: Human-readable summary of the first implementation objective.
        acceptance_criteria: Acceptance criteria preserved from the implementation issue.
        single_pull_request_scope: Explicit boundary for the first implementation slice.
    """

    use_case_identifier: UseCaseIdentifier
    related_issue_use_case: UseCaseIdentifier
    focus_summary: str
    acceptance_criteria: tuple[str, ...]
    single_pull_request_scope: str

    def __post_init__(self) -> None:
        """Validates the initial engineer execution focus."""

        if self.use_case_identifier is not UseCaseIdentifier.IMPLEMENT_ISSUE_WITH_ENGINEER:
            raise ValueError("use_case_identifier must be UC_IMPLEMENT_ISSUE_WITH_ENGINEER.")
        if not self.focus_summary.strip():
            raise ValueError("focus_summary must not be empty.")
        if not self.acceptance_criteria:
            raise ValueError("acceptance_criteria must not be empty.")
        if any(
            not acceptance_criterion.strip() for acceptance_criterion in self.acceptance_criteria
        ):
            raise ValueError("acceptance_criteria must not contain empty values.")
        if len(set(self.acceptance_criteria)) != len(self.acceptance_criteria):
            raise ValueError("acceptance_criteria must not contain duplicate values.")
        if not self.single_pull_request_scope.strip():
            raise ValueError("single_pull_request_scope must not be empty.")


@dataclass(frozen=True, slots=True)
class EngineerJobInput:
    """Represents the strict input required to start an engineer job.

    Attributes:
        issue_title: Title of the backlog-ready implementation issue.
        issue_overview: Overview that explains the implementation slice.
        acceptance_criteria: Verifiable outcomes that the engineer must satisfy.
        single_pull_request_scope: Explicit boundary that keeps execution within one PR.
        related_issue_use_case: Use case advanced by the source implementation issue.

    Example:
        engineer_job_input = EngineerJobInput(
            issue_title="Implement engineer job input builder",
            issue_overview="Build the strict engineer job input model.",
            acceptance_criteria=("Return a strict engineer job input model.",),
            single_pull_request_scope="Limit the work to one engineer job input model.",
            related_issue_use_case=UseCaseIdentifier.ORCHESTRATE_DELIVERY_WITH_MANAGER,
        )
        execution_focus = engineer_job_input.build_initial_execution_focus()
        assert execution_focus.use_case_identifier is (
            UseCaseIdentifier.IMPLEMENT_ISSUE_WITH_ENGINEER
        )
    """

    issue_title: str
    issue_overview: str
    acceptance_criteria: tuple[str, ...]
    single_pull_request_scope: str
    related_issue_use_case: UseCaseIdentifier

    def __post_init__(self) -> None:
        """Validates the engineer job input."""

        if not self.issue_title.strip():
            raise ValueError("issue_title must not be empty.")
        if not self.issue_overview.strip():
            raise ValueError("issue_overview must not be empty.")
        if not self.acceptance_criteria:
            raise ValueError("acceptance_criteria must not be empty.")
        if any(
            not acceptance_criterion.strip() for acceptance_criterion in self.acceptance_criteria
        ):
            raise ValueError("acceptance_criteria must not contain empty values.")
        if len(set(self.acceptance_criteria)) != len(self.acceptance_criteria):
            raise ValueError("acceptance_criteria must not contain duplicate values.")
        if not self.single_pull_request_scope.strip():
            raise ValueError("single_pull_request_scope must not be empty.")

    def build_initial_execution_focus(self) -> EngineerExecutionFocus:
        """Builds the initial engineer execution focus from this input model."""

        return EngineerExecutionFocus(
            use_case_identifier=UseCaseIdentifier.IMPLEMENT_ISSUE_WITH_ENGINEER,
            related_issue_use_case=self.related_issue_use_case,
            focus_summary=self.issue_overview,
            acceptance_criteria=self.acceptance_criteria,
            single_pull_request_scope=self.single_pull_request_scope,
        )


@dataclass(frozen=True, slots=True)
class EngineerJobInputResult:
    """Represents whether an engineer job can start from one implementation issue payload.

    Attributes:
        status: High-level outcome for caller-side branching.
        summary_message: Human-readable status summary for orchestration.
        missing_information_items: Missing inputs required before the job can start.
        engineer_job_input: Strict engineer job input when status is `READY`.
    """

    status: EngineerJobInputStatus
    summary_message: str
    missing_information_items: tuple[str, ...] = ()
    engineer_job_input: EngineerJobInput | None = None

    def __post_init__(self) -> None:
        """Validates result consistency."""

        if not self.summary_message.strip():
            raise ValueError("summary_message must not be empty.")
        if any(not missing_item.strip() for missing_item in self.missing_information_items):
            raise ValueError("missing_information_items must not contain empty values.")
        if len(set(self.missing_information_items)) != len(self.missing_information_items):
            raise ValueError("missing_information_items must not contain duplicate values.")

        if self.status is EngineerJobInputStatus.READY:
            if self.engineer_job_input is None:
                raise ValueError("engineer_job_input must be provided when status is READY.")
            if self.missing_information_items:
                raise ValueError("missing_information_items must be empty when status is READY.")
            return

        if self.engineer_job_input is not None:
            raise ValueError("engineer_job_input must be empty unless status is READY.")

        if self.status is EngineerJobInputStatus.INPUT_REQUIRED:
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
class EngineerExecutionWorkItemContract:
    """Represents the strict work item required to start engineer execution.

    Attributes:
        issue_work_item_contract: Repository-qualified implementation issue metadata.
        engineer_job_input: Strict engineer job input prepared from the backlog-ready issue.
        execution_focus: Initial execution focus derived from the engineer job input.
        role_name: Worker role selected for execution. Must be `engineer`.
        provider_name: Provider adapter selected by the control-plane.

    Example:
        work_item_contract = EngineerExecutionWorkItemContract.create_from_issue_and_job_input(
            issue_work_item_contract=issue_work_item_contract,
            engineer_job_input=engineer_job_input,
        )
        assert work_item_contract.role_name is WorkerRoleName.ENGINEER
    """

    issue_work_item_contract: IssueWorkItemContract
    engineer_job_input: EngineerJobInput
    execution_focus: EngineerExecutionFocus
    role_name: WorkerRoleName = WorkerRoleName.ENGINEER
    provider_name: ProviderName = ProviderName.CURSOR

    def __post_init__(self) -> None:
        """Validates issue metadata and execution focus consistency."""

        if self.role_name is not WorkerRoleName.ENGINEER:
            raise ValueError("role_name must be engineer for EngineerExecutionWorkItemContract.")
        if not isinstance(self.provider_name, ProviderName):
            raise ValueError("provider_name must be a ProviderName value.")
        if self.issue_work_item_contract.issue_title != self.engineer_job_input.issue_title:
            raise ValueError(
                "issue_work_item_contract.issue_title must match engineer_job_input.issue_title."
            )

        expected_execution_focus = self.engineer_job_input.build_initial_execution_focus()
        if self.execution_focus != expected_execution_focus:
            raise ValueError(
                "execution_focus must match engineer_job_input.build_initial_execution_focus()."
            )

    @classmethod
    def create_from_issue_and_job_input(
        cls,
        *,
        issue_work_item_contract: IssueWorkItemContract,
        engineer_job_input: EngineerJobInput,
        provider_name: ProviderName = ProviderName.CURSOR,
    ) -> "EngineerExecutionWorkItemContract":
        """Builds a validated engineer execution work item from strict input models.

        Args:
            issue_work_item_contract: Backlog-ready implementation issue metadata.
            engineer_job_input: Strict engineer job input prepared for the issue.
            provider_name: Provider adapter selected by the control-plane.

        Returns:
            A validated engineer execution work item contract.
        """

        return cls(
            issue_work_item_contract=issue_work_item_contract,
            engineer_job_input=engineer_job_input,
            execution_focus=engineer_job_input.build_initial_execution_focus(),
            provider_name=provider_name,
        )


@dataclass(frozen=True, slots=True)
class EngineerImplementationReentryTransitionContext:
    """Represents the workflow transition required for engineer re-entry."""

    current_state: RequirementDiscoverySessionState
    next_state: RequirementDiscoverySessionState
    required_operation: EngineerImplementationReentryOperation

    def __post_init__(self) -> None:
        """Validates engineer re-entry transition metadata."""

        if self.current_state is not RequirementDiscoverySessionState.ENGINEER_CHANGES_REQUESTED:
            raise ValueError("current_state must be STATE_ENGINEER_CHANGES_REQUESTED.")
        if self.next_state is not RequirementDiscoverySessionState.IMPLEMENTATION_PR_OPEN:
            raise ValueError("next_state must be STATE_IMPLEMENTATION_PR_OPEN.")
        if (
            self.required_operation
            is not EngineerImplementationReentryOperation.UPDATE_IMPLEMENTATION_PULL_REQUEST
        ):
            raise ValueError("required_operation must be OP_UPDATE_IMPLEMENTATION_PULL_REQUEST.")


@dataclass(frozen=True, slots=True)
class EngineerImplementationReentryInput:
    """Represents the strict input required to resume engineer implementation work.

    Attributes:
        pull_request_number: Existing implementation pull request number that must be updated.
        pull_request_title: Existing implementation pull request title that remains open.
        branch_name: Branch that the engineer must continue updating.
        base_branch_name: Protected base branch targeted by the implementation pull request.
        related_issue_identifier: Repository-qualified issue reference that scopes the work.
        related_issue_title: Title of the implementation issue linked to the pull request.
        issue_overview: Overview that explains the implementation slice being resumed.
        acceptance_criteria: Verifiable outcomes that remain in scope for the resumed work.
        single_pull_request_scope: Explicit boundary that keeps the resumed work in one pull
            request.
        requested_changes: Human-readable change requests that must be addressed next.
        transition_context: Workflow transition metadata for the resumed engineer loop.
    """

    pull_request_number: int
    pull_request_title: str
    branch_name: str
    base_branch_name: str
    related_issue_identifier: str
    related_issue_title: str
    issue_overview: str
    acceptance_criteria: tuple[str, ...]
    single_pull_request_scope: str
    requested_changes: tuple[str, ...]
    transition_context: EngineerImplementationReentryTransitionContext

    def __post_init__(self) -> None:
        """Validates engineer re-entry input."""

        if self.pull_request_number <= 0:
            raise ValueError("pull_request_number must be greater than zero.")
        if not self.pull_request_title.strip():
            raise ValueError("pull_request_title must not be empty.")
        if not self.branch_name.strip():
            raise ValueError("branch_name must not be empty.")
        if not self.base_branch_name.strip():
            raise ValueError("base_branch_name must not be empty.")
        if self.base_branch_name != _IMPLEMENTATION_PULL_REQUEST_BASE_BRANCH:
            raise ValueError(
                f"base_branch_name must be {_IMPLEMENTATION_PULL_REQUEST_BASE_BRANCH}."
            )
        if not self.related_issue_identifier.strip():
            raise ValueError("related_issue_identifier must not be empty.")
        if not self.related_issue_title.strip():
            raise ValueError("related_issue_title must not be empty.")
        if not self.issue_overview.strip():
            raise ValueError("issue_overview must not be empty.")
        if not self.acceptance_criteria:
            raise ValueError("acceptance_criteria must not be empty.")
        if any(
            not acceptance_criterion.strip() for acceptance_criterion in self.acceptance_criteria
        ):
            raise ValueError("acceptance_criteria must not contain empty values.")
        if len(set(self.acceptance_criteria)) != len(self.acceptance_criteria):
            raise ValueError("acceptance_criteria must not contain duplicate values.")
        if not self.single_pull_request_scope.strip():
            raise ValueError("single_pull_request_scope must not be empty.")
        if not self.requested_changes:
            raise ValueError("requested_changes must not be empty.")
        if any(not requested_change.strip() for requested_change in self.requested_changes):
            raise ValueError("requested_changes must not contain empty values.")
        if len(set(self.requested_changes)) != len(self.requested_changes):
            raise ValueError("requested_changes must not contain duplicate values.")


@dataclass(frozen=True, slots=True)
class EngineerImplementationReentryInputResult:
    """Represents whether engineer re-entry can resume from requested changes."""

    status: EngineerImplementationReentryInputStatus
    summary_message: str
    missing_information_items: tuple[str, ...] = ()
    reentry_input: EngineerImplementationReentryInput | None = None

    def __post_init__(self) -> None:
        """Validates engineer re-entry result consistency."""

        if not self.summary_message.strip():
            raise ValueError("summary_message must not be empty.")
        if any(not missing_item.strip() for missing_item in self.missing_information_items):
            raise ValueError("missing_information_items must not contain empty values.")
        if len(set(self.missing_information_items)) != len(self.missing_information_items):
            raise ValueError("missing_information_items must not contain duplicate values.")

        if self.status is EngineerImplementationReentryInputStatus.READY:
            if self.reentry_input is None:
                raise ValueError("reentry_input must be provided when status is READY.")
            if self.missing_information_items:
                raise ValueError("missing_information_items must be empty when status is READY.")
            return

        if self.reentry_input is not None:
            raise ValueError("reentry_input must be empty unless status is READY.")

        if self.status is EngineerImplementationReentryInputStatus.INPUT_REQUIRED:
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
class ImplementationPullRequestCreatePayload:
    """Represents the typed payload required to open an implementation pull request.

    Attributes:
        branch_name: Suggested branch name that should be pushed before opening the pull request.
        base_branch_name: Target branch that the implementation pull request must use.
        pull_request_title: Suggested pull request title for the implementation change.
        pull_request_body_summary: Summary content that should appear in the pull request body.
        test_evidence: Collected local verification evidence for the implementation change.
        related_issue_identifier: Repository-qualified issue reference linked to the pull request.
        related_issue_title: Title of the implementation issue traced by the pull request.
        issue_overview: Human-readable overview of the implementation slice under review.
        acceptance_criteria: Verifiable outcomes preserved from the implementation issue.
        single_pull_request_scope: Explicit boundary that keeps the implementation within one PR.
        target_state: Workflow state reached once the pull request is opened.
    """

    branch_name: str
    base_branch_name: str
    pull_request_title: str
    pull_request_body_summary: str
    test_evidence: tuple[str, ...]
    related_issue_identifier: str
    related_issue_title: str
    issue_overview: str
    acceptance_criteria: tuple[str, ...]
    single_pull_request_scope: str
    target_state: RequirementDiscoverySessionState

    def __post_init__(self) -> None:
        """Validates the implementation pull request payload."""

        if not self.branch_name.strip():
            raise ValueError("branch_name must not be empty.")
        if not self.base_branch_name.strip():
            raise ValueError("base_branch_name must not be empty.")
        if self.base_branch_name != _IMPLEMENTATION_PULL_REQUEST_BASE_BRANCH:
            raise ValueError(
                f"base_branch_name must be {_IMPLEMENTATION_PULL_REQUEST_BASE_BRANCH}."
            )
        if not self.pull_request_title.strip():
            raise ValueError("pull_request_title must not be empty.")
        if not self.pull_request_body_summary.strip():
            raise ValueError("pull_request_body_summary must not be empty.")
        if not self.test_evidence:
            raise ValueError("test_evidence must not be empty.")
        if any(not evidence_item.strip() for evidence_item in self.test_evidence):
            raise ValueError("test_evidence must not contain empty values.")
        if len(set(self.test_evidence)) != len(self.test_evidence):
            raise ValueError("test_evidence must not contain duplicate values.")
        if not self.related_issue_identifier.strip():
            raise ValueError("related_issue_identifier must not be empty.")
        if not self.related_issue_title.strip():
            raise ValueError("related_issue_title must not be empty.")
        if not self.issue_overview.strip():
            raise ValueError("issue_overview must not be empty.")
        if not self.acceptance_criteria:
            raise ValueError("acceptance_criteria must not be empty.")
        if any(
            not acceptance_criterion.strip() for acceptance_criterion in self.acceptance_criteria
        ):
            raise ValueError("acceptance_criteria must not contain empty values.")
        if len(set(self.acceptance_criteria)) != len(self.acceptance_criteria):
            raise ValueError("acceptance_criteria must not contain duplicate values.")
        if not self.single_pull_request_scope.strip():
            raise ValueError("single_pull_request_scope must not be empty.")
        if self.target_state is not RequirementDiscoverySessionState.IMPLEMENTATION_PR_OPEN:
            raise ValueError("target_state must be STATE_IMPLEMENTATION_PR_OPEN.")


@dataclass(frozen=True, slots=True)
class OpenedImplementationPullRequestMetadata:
    """Represents the opened implementation pull request metadata consumed by Manager.

    Attributes:
        pull_request_number: Repository-local pull request number visible on GitHub.
        branch_name: Source branch that carries the implementation change.
        base_branch_name: Target branch that received the implementation pull request.
        pull_request_title: Opened pull request title under review.
        pull_request_body_summary: Human-readable summary of the implementation pull request.
        test_evidence: Collected local verification evidence attached to the pull request.
        related_issue_identifier: Repository-qualified implementation issue reference.
        related_issue_title: Title of the related implementation issue.
        issue_overview: Overview of the implementation slice under review.
        acceptance_criteria: Verifiable outcomes that Manager must check.
        single_pull_request_scope: Explicit boundary that defines the intended single-PR slice.
    """

    pull_request_number: int
    branch_name: str
    base_branch_name: str
    pull_request_title: str
    pull_request_body_summary: str
    test_evidence: tuple[str, ...]
    related_issue_identifier: str
    related_issue_title: str
    issue_overview: str
    acceptance_criteria: tuple[str, ...]
    single_pull_request_scope: str

    def __post_init__(self) -> None:
        """Validates opened implementation pull request metadata."""

        if self.pull_request_number <= 0:
            raise ValueError("pull_request_number must be greater than zero.")
        if not self.branch_name.strip():
            raise ValueError("branch_name must not be empty.")
        if not self.base_branch_name.strip():
            raise ValueError("base_branch_name must not be empty.")
        if self.base_branch_name != _IMPLEMENTATION_PULL_REQUEST_BASE_BRANCH:
            raise ValueError(
                f"base_branch_name must be {_IMPLEMENTATION_PULL_REQUEST_BASE_BRANCH}."
            )
        if not self.pull_request_title.strip():
            raise ValueError("pull_request_title must not be empty.")
        if not self.pull_request_body_summary.strip():
            raise ValueError("pull_request_body_summary must not be empty.")
        if not self.test_evidence:
            raise ValueError("test_evidence must not be empty.")
        if any(not evidence_item.strip() for evidence_item in self.test_evidence):
            raise ValueError("test_evidence must not contain empty values.")
        if len(set(self.test_evidence)) != len(self.test_evidence):
            raise ValueError("test_evidence must not contain duplicate values.")
        if not self.related_issue_identifier.strip():
            raise ValueError("related_issue_identifier must not be empty.")
        if not self.related_issue_title.strip():
            raise ValueError("related_issue_title must not be empty.")
        if not self.issue_overview.strip():
            raise ValueError("issue_overview must not be empty.")
        if not self.acceptance_criteria:
            raise ValueError("acceptance_criteria must not be empty.")
        if any(
            not acceptance_criterion.strip() for acceptance_criterion in self.acceptance_criteria
        ):
            raise ValueError("acceptance_criteria must not contain empty values.")
        if len(set(self.acceptance_criteria)) != len(self.acceptance_criteria):
            raise ValueError("acceptance_criteria must not contain duplicate values.")
        if not self.single_pull_request_scope.strip():
            raise ValueError("single_pull_request_scope must not be empty.")

    @classmethod
    def from_pull_request_create_payload(
        cls,
        *,
        pull_request_create_payload: ImplementationPullRequestCreatePayload,
        pull_request_number: int,
    ) -> "OpenedImplementationPullRequestMetadata":
        """Builds opened pull request metadata from a create payload plus PR number."""

        return cls(
            pull_request_number=pull_request_number,
            branch_name=pull_request_create_payload.branch_name,
            base_branch_name=pull_request_create_payload.base_branch_name,
            pull_request_title=pull_request_create_payload.pull_request_title,
            pull_request_body_summary=pull_request_create_payload.pull_request_body_summary,
            test_evidence=pull_request_create_payload.test_evidence,
            related_issue_identifier=pull_request_create_payload.related_issue_identifier,
            related_issue_title=pull_request_create_payload.related_issue_title,
            issue_overview=pull_request_create_payload.issue_overview,
            acceptance_criteria=pull_request_create_payload.acceptance_criteria,
            single_pull_request_scope=pull_request_create_payload.single_pull_request_scope,
        )


@dataclass(frozen=True, slots=True)
class ImplementationPullRequestOpenResult:
    """Represents whether an implementation pull request can be opened next.

    Attributes:
        status: High-level outcome for caller-side branching.
        summary_message: Human-readable summary for the next workflow step.
        next_state: Workflow state selected after interpreting the result.
        missing_information_items: Missing inputs that should be collected before opening a PR.
        pull_request_create_payload: Strict implementation PR payload when status is `READY`.
        blocker_summary: Existing blocker summary when the workflow remains blocked.
    """

    status: ImplementationPullRequestOpenStatus
    summary_message: str
    next_state: RequirementDiscoverySessionState
    missing_information_items: tuple[str, ...] = ()
    pull_request_create_payload: ImplementationPullRequestCreatePayload | None = None
    blocker_summary: str | None = None

    def __post_init__(self) -> None:
        """Validates implementation pull request result consistency."""

        if not self.summary_message.strip():
            raise ValueError("summary_message must not be empty.")
        if any(not missing_item.strip() for missing_item in self.missing_information_items):
            raise ValueError("missing_information_items must not contain empty values.")
        if len(set(self.missing_information_items)) != len(self.missing_information_items):
            raise ValueError("missing_information_items must not contain duplicate values.")
        if not isinstance(self.next_state, RequirementDiscoverySessionState):
            raise ValueError("next_state must be a RequirementDiscoverySessionState value.")
        if self.blocker_summary is not None and not self.blocker_summary.strip():
            raise ValueError("blocker_summary must not be empty when provided.")

        if self.status is ImplementationPullRequestOpenStatus.READY:
            if self.pull_request_create_payload is None:
                raise ValueError(
                    "pull_request_create_payload must be provided when status is READY."
                )
            if self.missing_information_items:
                raise ValueError("missing_information_items must be empty when status is READY.")
            if self.blocker_summary is not None:
                raise ValueError("blocker_summary must be empty when status is READY.")
            if self.next_state is not RequirementDiscoverySessionState.IMPLEMENTATION_PR_OPEN:
                raise ValueError(
                    "next_state must be STATE_IMPLEMENTATION_PR_OPEN when status is READY."
                )
            return

        if self.pull_request_create_payload is not None:
            raise ValueError("pull_request_create_payload must be empty unless status is READY.")

        if self.status is ImplementationPullRequestOpenStatus.INPUT_REQUIRED:
            if not self.missing_information_items:
                raise ValueError(
                    "missing_information_items must not be empty when status is INPUT_REQUIRED."
                )
            if self.blocker_summary is not None:
                raise ValueError("blocker_summary must be empty when status is INPUT_REQUIRED.")
            if self.next_state not in (
                RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING,
                RequirementDiscoverySessionState.IMPLEMENTATION_BLOCKED,
            ):
                raise ValueError(
                    "next_state must be STATE_ENGINEER_JOB_RUNNING or "
                    "STATE_IMPLEMENTATION_BLOCKED when status is INPUT_REQUIRED."
                )
            return

        if self.status is ImplementationPullRequestOpenStatus.BLOCKED:
            if self.missing_information_items:
                raise ValueError("missing_information_items must be empty when status is BLOCKED.")
            if self.blocker_summary is None:
                raise ValueError("blocker_summary must be provided when status is BLOCKED.")
            if self.next_state is not RequirementDiscoverySessionState.IMPLEMENTATION_BLOCKED:
                raise ValueError("next_state must be STATE_IMPLEMENTATION_BLOCKED when BLOCKED.")
            return

        if self.missing_information_items:
            raise ValueError(
                "missing_information_items must be empty when status is UNSUPPORTED_STATE."
            )
        if self.blocker_summary is not None:
            raise ValueError("blocker_summary must be empty when status is UNSUPPORTED_STATE.")


@dataclass(frozen=True, slots=True)
class ManagerImplementationReviewTransitionContext:
    """Represents the workflow transition metadata required for implementation review."""

    current_state: RequirementDiscoverySessionState
    next_state: RequirementDiscoverySessionState
    required_operation: ManagerImplementationReviewOperation

    def __post_init__(self) -> None:
        """Validates manager implementation review transition metadata."""

        if self.current_state is not RequirementDiscoverySessionState.IMPLEMENTATION_PR_OPEN:
            raise ValueError("current_state must be STATE_IMPLEMENTATION_PR_OPEN.")
        if (
            self.next_state
            is not RequirementDiscoverySessionState.IMPLEMENTATION_REVIEW_IN_PROGRESS
        ):
            raise ValueError("next_state must be STATE_IMPLEMENTATION_REVIEW_IN_PROGRESS.")
        if self.required_operation is not ManagerImplementationReviewOperation.REVIEW_ENGINEER_PR:
            raise ValueError("required_operation must be OP_REVIEW_ENGINEER_PR.")


@dataclass(frozen=True, slots=True)
class ManagerImplementationReviewInput:
    """Represents the strict manager input required for implementation PR review.

    Attributes:
        pull_request_number: Opened pull request number when GitHub metadata is available.
        branch_name: Source branch that carries the implementation change.
        base_branch_name: Target branch that the implementation pull request must use.
        pull_request_title: Opened implementation pull request title under review.
        pull_request_summary: Human-readable summary of the implementation pull request.
        related_issue_identifier: Repository-qualified implementation issue reference.
        related_issue_title: Title of the related implementation issue.
        issue_overview: Overview of the implementation slice under review.
        acceptance_criteria: Verifiable outcomes that Manager must review.
        single_pull_request_scope: Explicit boundary that should remain within one pull request.
        test_evidence: Local verification evidence attached to the implementation change.
        review_targets: Minimum targets that Manager must verify during review.
        transition_context: Workflow transition metadata for `OP_REVIEW_ENGINEER_PR`.
    """

    pull_request_number: int | None
    branch_name: str
    base_branch_name: str
    pull_request_title: str
    pull_request_summary: str
    related_issue_identifier: str
    related_issue_title: str
    issue_overview: str
    acceptance_criteria: tuple[str, ...]
    single_pull_request_scope: str
    test_evidence: tuple[str, ...]
    review_targets: tuple[ManagerImplementationReviewCheckTarget, ...]
    transition_context: ManagerImplementationReviewTransitionContext

    def __post_init__(self) -> None:
        """Validates manager implementation review input fields."""

        if self.pull_request_number is not None and self.pull_request_number <= 0:
            raise ValueError("pull_request_number must be greater than zero when provided.")
        if not self.branch_name.strip():
            raise ValueError("branch_name must not be empty.")
        if not self.base_branch_name.strip():
            raise ValueError("base_branch_name must not be empty.")
        if self.base_branch_name != _IMPLEMENTATION_PULL_REQUEST_BASE_BRANCH:
            raise ValueError(
                f"base_branch_name must be {_IMPLEMENTATION_PULL_REQUEST_BASE_BRANCH}."
            )
        if not self.pull_request_title.strip():
            raise ValueError("pull_request_title must not be empty.")
        if not self.pull_request_summary.strip():
            raise ValueError("pull_request_summary must not be empty.")
        if not self.related_issue_identifier.strip():
            raise ValueError("related_issue_identifier must not be empty.")
        if not self.related_issue_title.strip():
            raise ValueError("related_issue_title must not be empty.")
        if not self.issue_overview.strip():
            raise ValueError("issue_overview must not be empty.")
        if not self.acceptance_criteria:
            raise ValueError("acceptance_criteria must not be empty.")
        if any(
            not acceptance_criterion.strip() for acceptance_criterion in self.acceptance_criteria
        ):
            raise ValueError("acceptance_criteria must not contain empty values.")
        if len(set(self.acceptance_criteria)) != len(self.acceptance_criteria):
            raise ValueError("acceptance_criteria must not contain duplicate values.")
        if not self.single_pull_request_scope.strip():
            raise ValueError("single_pull_request_scope must not be empty.")
        if not self.test_evidence:
            raise ValueError("test_evidence must not be empty.")
        if any(not evidence_item.strip() for evidence_item in self.test_evidence):
            raise ValueError("test_evidence must not contain empty values.")
        if len(set(self.test_evidence)) != len(self.test_evidence):
            raise ValueError("test_evidence must not contain duplicate values.")
        if not self.review_targets:
            raise ValueError("review_targets must not be empty.")
        if len(set(self.review_targets)) != len(self.review_targets):
            raise ValueError("review_targets must not contain duplicate values.")


@dataclass(frozen=True, slots=True)
class ManagerImplementationReviewInputResult:
    """Represents whether manager implementation review can start immediately."""

    status: ManagerImplementationReviewInputStatus
    summary_message: str
    missing_information_items: tuple[str, ...] = ()
    review_input: ManagerImplementationReviewInput | None = None

    def __post_init__(self) -> None:
        """Validates result consistency."""

        if not self.summary_message.strip():
            raise ValueError("summary_message must not be empty.")
        if any(not missing_item.strip() for missing_item in self.missing_information_items):
            raise ValueError("missing_information_items must not contain empty values.")
        if len(set(self.missing_information_items)) != len(self.missing_information_items):
            raise ValueError("missing_information_items must not contain duplicate values.")

        if self.status is ManagerImplementationReviewInputStatus.READY:
            if self.review_input is None:
                raise ValueError("review_input must be provided when status is READY.")
            if self.missing_information_items:
                raise ValueError("missing_information_items must be empty when status is READY.")
            return

        if self.review_input is not None:
            raise ValueError("review_input must be empty unless status is READY.")

        if self.status is ManagerImplementationReviewInputStatus.INPUT_REQUIRED:
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
class ManagerImplementationReviewDecisionFinding:
    """Represents one typed finding from the manager implementation review.

    Attributes:
        check_target: Review target where the implementation gap was observed.
        summary: Human-readable explanation of the review finding.
    """

    check_target: ManagerImplementationReviewCheckTarget
    summary: str

    def __post_init__(self) -> None:
        """Validates implementation review finding fields."""

        if not self.summary.strip():
            raise ValueError("summary must not be empty.")


@dataclass(frozen=True, slots=True)
class ManagerImplementationReviewDecisionResult:
    """Represents the typed implementation review outcome and follow-up rationale.

    Attributes:
        status: High-level outcome for caller-side branching.
        summary_message: Human-readable summary of the decision-building outcome.
        decision: Typed decision when status is `READY`.
        review_body_draft: Draft PR review body for approve or request-changes outcomes.
        findings: Typed implementation review findings that explain the outcome.
        requested_changes: Human-readable changes derived from the findings.
        missing_information_items: Required inputs that are still missing.
        unsupported_check_targets: Review targets that are outside the declared review scope.
        retry_limit_reason: Why another automated review retry should not be attempted.
        escalation_reason: Why user direction is required to continue safely.

    Example:
        result = build_manager_implementation_review_decision_result(
            review_input=review_input,
            review_findings=(),
            retry_limit_reason=None,
            escalation_reason=None,
        )
        assert result.decision is ManagerImplementationReviewDecision.APPROVE
    """

    status: ManagerImplementationReviewDecisionStatus
    summary_message: str
    decision: ManagerImplementationReviewDecision | None = None
    review_body_draft: str | None = None
    findings: tuple[ManagerImplementationReviewDecisionFinding, ...] = ()
    requested_changes: tuple[str, ...] = ()
    missing_information_items: tuple[str, ...] = ()
    unsupported_check_targets: tuple[ManagerImplementationReviewCheckTarget, ...] = ()
    retry_limit_reason: str | None = None
    escalation_reason: str | None = None

    def __post_init__(self) -> None:
        """Validates implementation-review decision result consistency."""

        if not self.summary_message.strip():
            raise ValueError("summary_message must not be empty.")
        if self.review_body_draft is not None and not self.review_body_draft.strip():
            raise ValueError("review_body_draft must not be empty when provided.")
        if any(not change_item.strip() for change_item in self.requested_changes):
            raise ValueError("requested_changes must not contain empty values.")
        if any(not missing_item.strip() for missing_item in self.missing_information_items):
            raise ValueError("missing_information_items must not contain empty values.")
        if len(set(self.findings)) != len(self.findings):
            raise ValueError("findings must not contain duplicate values.")
        if len(set(self.requested_changes)) != len(self.requested_changes):
            raise ValueError("requested_changes must not contain duplicate values.")
        if len(set(self.missing_information_items)) != len(self.missing_information_items):
            raise ValueError("missing_information_items must not contain duplicate values.")
        if len(set(self.unsupported_check_targets)) != len(self.unsupported_check_targets):
            raise ValueError("unsupported_check_targets must not contain duplicate values.")
        if self.retry_limit_reason is not None and not self.retry_limit_reason.strip():
            raise ValueError("retry_limit_reason must not be empty when provided.")
        if self.escalation_reason is not None and not self.escalation_reason.strip():
            raise ValueError("escalation_reason must not be empty when provided.")

        if self.status is ManagerImplementationReviewDecisionStatus.READY:
            if self.decision is None:
                raise ValueError("decision must be provided when status is READY.")
            if self.missing_information_items:
                raise ValueError("missing_information_items must be empty when status is READY.")
            if self.unsupported_check_targets:
                raise ValueError("unsupported_check_targets must be empty when status is READY.")
            if self.decision is ManagerImplementationReviewDecision.APPROVE:
                if self.review_body_draft is None:
                    raise ValueError("review_body_draft must be provided when decision is APPROVE.")
                if self.findings:
                    raise ValueError("findings must be empty when decision is APPROVE.")
                if self.requested_changes:
                    raise ValueError("requested_changes must be empty when decision is APPROVE.")
                if self.retry_limit_reason is not None:
                    raise ValueError("retry_limit_reason must be empty when decision is APPROVE.")
                if self.escalation_reason is not None:
                    raise ValueError("escalation_reason must be empty when decision is APPROVE.")
                return

            if self.decision is ManagerImplementationReviewDecision.REQUEST_CHANGES:
                if self.review_body_draft is None:
                    raise ValueError(
                        "review_body_draft must be provided when decision is REQUEST_CHANGES."
                    )
                if not self.findings:
                    raise ValueError("findings must not be empty when decision is REQUEST_CHANGES.")
                if not self.requested_changes:
                    raise ValueError(
                        "requested_changes must not be empty when decision is REQUEST_CHANGES."
                    )
                if self.retry_limit_reason is not None:
                    raise ValueError(
                        "retry_limit_reason must be empty when decision is REQUEST_CHANGES."
                    )
                if self.escalation_reason is not None:
                    raise ValueError(
                        "escalation_reason must be empty when decision is REQUEST_CHANGES."
                    )
                return

            if self.review_body_draft is not None:
                raise ValueError(
                    "review_body_draft must be empty when decision is USER_DECISION_REQUIRED."
                )
            if not self.retry_limit_reason and not self.escalation_reason:
                raise ValueError(
                    "retry_limit_reason or escalation_reason must be provided when decision "
                    "is USER_DECISION_REQUIRED."
                )
            if self.findings and not self.requested_changes:
                raise ValueError(
                    "requested_changes must be provided when findings are included for "
                    "USER_DECISION_REQUIRED."
                )
            if self.requested_changes and not self.findings:
                raise ValueError(
                    "findings must be provided when requested_changes are included for "
                    "USER_DECISION_REQUIRED."
                )
            return

        if self.decision is not None:
            raise ValueError("decision must be empty unless status is READY.")
        if self.review_body_draft is not None:
            raise ValueError("review_body_draft must be empty unless status is READY.")
        if self.findings:
            raise ValueError("findings must be empty unless status is READY.")
        if self.requested_changes:
            raise ValueError("requested_changes must be empty unless status is READY.")
        if self.retry_limit_reason is not None:
            raise ValueError("retry_limit_reason must be empty unless status is READY.")
        if self.escalation_reason is not None:
            raise ValueError("escalation_reason must be empty unless status is READY.")

        if self.status is ManagerImplementationReviewDecisionStatus.INPUT_REQUIRED:
            if not self.missing_information_items:
                raise ValueError(
                    "missing_information_items must not be empty when status is INPUT_REQUIRED."
                )
            if self.unsupported_check_targets:
                raise ValueError(
                    "unsupported_check_targets must be empty when status is INPUT_REQUIRED."
                )
            return

        if self.missing_information_items:
            raise ValueError(
                "missing_information_items must be empty when status is UNSUPPORTED_REVIEW_SCOPE."
            )
        if not self.unsupported_check_targets:
            raise ValueError(
                "unsupported_check_targets must not be empty when status is "
                "UNSUPPORTED_REVIEW_SCOPE."
            )


@dataclass(frozen=True, slots=True)
class ManagerImplementationReviewExecutionPayload:
    """Represents the minimum payload needed to execute an implementation review.

    Attributes:
        pull_request_number: Repository-local pull request number visible on GitHub.
        pull_request_title: Implementation pull request title currently under review.
        review_decision: Review decision to submit to the future GitHub adapter.
        review_body: Review body that should be submitted with the review decision.
    """

    pull_request_number: int
    pull_request_title: str
    review_decision: ManagerImplementationReviewDecision
    review_body: str

    def __post_init__(self) -> None:
        """Validates the implementation review execution payload."""

        if self.pull_request_number <= 0:
            raise ValueError("pull_request_number must be greater than zero.")
        if not self.pull_request_title.strip():
            raise ValueError("pull_request_title must not be empty.")
        if self.review_decision not in (
            ManagerImplementationReviewDecision.APPROVE,
            ManagerImplementationReviewDecision.REQUEST_CHANGES,
        ):
            raise ValueError(
                "review_decision must be APPROVE or REQUEST_CHANGES for review execution."
            )
        if not self.review_body.strip():
            raise ValueError("review_body must not be empty.")


@dataclass(frozen=True, slots=True)
class ManagerImplementationReviewExecutionResult:
    """Represents whether a manager implementation review can execute now.

    Attributes:
        status: High-level outcome for caller-side branching.
        summary_message: Human-readable summary for the next workflow step.
        next_state: Workflow state to continue with after interpreting the result.
        missing_information_items: Missing inputs that must be supplied next.
        review_execution_payload: Strict review execution payload when status is `READY`
            and a GitHub review should be submitted.
    """

    status: ManagerImplementationReviewExecutionStatus
    summary_message: str
    next_state: RequirementDiscoverySessionState
    missing_information_items: tuple[str, ...] = ()
    review_execution_payload: ManagerImplementationReviewExecutionPayload | None = None

    def __post_init__(self) -> None:
        """Validates implementation review execution result consistency."""

        if not self.summary_message.strip():
            raise ValueError("summary_message must not be empty.")
        if any(not missing_item.strip() for missing_item in self.missing_information_items):
            raise ValueError("missing_information_items must not contain empty values.")
        if len(set(self.missing_information_items)) != len(self.missing_information_items):
            raise ValueError("missing_information_items must not contain duplicate values.")
        if not isinstance(self.next_state, RequirementDiscoverySessionState):
            raise ValueError("next_state must be a RequirementDiscoverySessionState value.")

        if self.status is ManagerImplementationReviewExecutionStatus.READY:
            if self.missing_information_items:
                raise ValueError("missing_information_items must be empty when status is READY.")
            if self.next_state is RequirementDiscoverySessionState.USER_DECISION_REQUIRED:
                if self.review_execution_payload is not None:
                    raise ValueError(
                        "review_execution_payload must be empty when next_state is "
                        "STATE_USER_DECISION_REQUIRED."
                    )
                return
            if self.review_execution_payload is None:
                raise ValueError("review_execution_payload must be provided when status is READY.")
            expected_next_state = _build_manager_implementation_review_next_state(
                self.review_execution_payload.review_decision
            )
            if self.next_state is not expected_next_state:
                raise ValueError(
                    "next_state must match the decision carried by review_execution_payload."
                )
            return

        if self.review_execution_payload is not None:
            raise ValueError("review_execution_payload must be empty unless status is READY.")

        if self.status is ManagerImplementationReviewExecutionStatus.INPUT_REQUIRED:
            if not self.missing_information_items:
                raise ValueError(
                    "missing_information_items must not be empty when status is INPUT_REQUIRED."
                )
            if (
                self.next_state
                is not RequirementDiscoverySessionState.IMPLEMENTATION_REVIEW_IN_PROGRESS
            ):
                raise ValueError(
                    "next_state must be STATE_IMPLEMENTATION_REVIEW_IN_PROGRESS when status "
                    "is INPUT_REQUIRED."
                )
            return

        if self.missing_information_items:
            raise ValueError(
                "missing_information_items must be empty when status is "
                "UNSUPPORTED_DECISION or UNSUPPORTED_STATE."
            )


@dataclass(frozen=True, slots=True)
class ImplementationPostMergeDeliveryRoutingResult:
    """Represents how delivery should proceed after an implementation PR merge.

    Attributes:
        status: High-level outcome for caller-side branching.
        summary_message: Human-readable summary describing the routing decision.
        next_state: Workflow state to continue with after interpreting the result.
        missing_information_items: Missing routing inputs required before continuing.
        routing_reason: Stable reason that explains the selected next state when status
            is `READY`.
        remaining_milestone_issue_count: Number of implementation issues still needed to
            finish the current milestone when status is `READY`.
        all_requirements_satisfied: Whether the full delivery scope is complete when
            status is `READY`.
    """

    status: ImplementationPostMergeDeliveryRoutingStatus
    summary_message: str
    next_state: RequirementDiscoverySessionState
    missing_information_items: tuple[str, ...] = ()
    routing_reason: ImplementationPostMergeDeliveryRoutingReason | None = None
    remaining_milestone_issue_count: int | None = None
    all_requirements_satisfied: bool | None = None

    def __post_init__(self) -> None:
        """Validates post-merge delivery routing result consistency."""

        if not self.summary_message.strip():
            raise ValueError("summary_message must not be empty.")
        if any(not missing_item.strip() for missing_item in self.missing_information_items):
            raise ValueError("missing_information_items must not contain empty values.")
        if len(set(self.missing_information_items)) != len(self.missing_information_items):
            raise ValueError("missing_information_items must not contain duplicate values.")
        if not isinstance(self.next_state, RequirementDiscoverySessionState):
            raise ValueError("next_state must be a RequirementDiscoverySessionState value.")
        if (
            self.remaining_milestone_issue_count is not None
            and self.remaining_milestone_issue_count < 0
        ):
            raise ValueError("remaining_milestone_issue_count must be zero or greater.")

        if self.status is ImplementationPostMergeDeliveryRoutingStatus.READY:
            if self.missing_information_items:
                raise ValueError("missing_information_items must be empty when status is READY.")
            if self.routing_reason is None:
                raise ValueError("routing_reason must be provided when status is READY.")
            if self.remaining_milestone_issue_count is None:
                raise ValueError(
                    "remaining_milestone_issue_count must be provided when status is READY."
                )
            if self.all_requirements_satisfied is None:
                raise ValueError(
                    "all_requirements_satisfied must be provided when status is READY."
                )
            expected_next_state = _build_implementation_post_merge_delivery_next_state(
                self.routing_reason
            )
            if self.next_state is not expected_next_state:
                raise ValueError("next_state must match the provided routing_reason.")
            if (
                self.routing_reason
                is ImplementationPostMergeDeliveryRoutingReason.MORE_ISSUES_NEEDED_FOR_MILESTONE
            ):
                if self.remaining_milestone_issue_count <= 0:
                    raise ValueError(
                        "remaining_milestone_issue_count must be greater than zero when "
                        "routing_reason is MORE_ISSUES_NEEDED_FOR_MILESTONE."
                    )
                if self.all_requirements_satisfied:
                    raise ValueError(
                        "all_requirements_satisfied must be False when routing_reason is "
                        "MORE_ISSUES_NEEDED_FOR_MILESTONE."
                    )
                return
            if self.remaining_milestone_issue_count != 0:
                raise ValueError(
                    "remaining_milestone_issue_count must be zero when routing_reason is "
                    "MILESTONE_COMPLETED or ALL_REQUIREMENTS_SATISFIED."
                )
            if (
                self.routing_reason
                is ImplementationPostMergeDeliveryRoutingReason.MILESTONE_COMPLETED
            ):
                if self.all_requirements_satisfied:
                    raise ValueError(
                        "all_requirements_satisfied must be False when routing_reason is "
                        "MILESTONE_COMPLETED."
                    )
                return
            if not self.all_requirements_satisfied:
                raise ValueError(
                    "all_requirements_satisfied must be True when routing_reason is "
                    "ALL_REQUIREMENTS_SATISFIED."
                )
            return

        if self.routing_reason is not None:
            raise ValueError("routing_reason must be empty unless status is READY.")
        if self.remaining_milestone_issue_count is not None:
            raise ValueError(
                "remaining_milestone_issue_count must be empty unless status is READY."
            )
        if self.all_requirements_satisfied is not None:
            raise ValueError("all_requirements_satisfied must be empty unless status is READY.")

        if self.status is ImplementationPostMergeDeliveryRoutingStatus.INPUT_REQUIRED:
            if not self.missing_information_items:
                raise ValueError(
                    "missing_information_items must not be empty when status is INPUT_REQUIRED."
                )
            if self.next_state is not RequirementDiscoverySessionState.IMPLEMENTATION_PR_MERGED:
                raise ValueError(
                    "next_state must be STATE_IMPLEMENTATION_PR_MERGED when status is "
                    "INPUT_REQUIRED."
                )
            return

        if self.missing_information_items:
            raise ValueError(
                "missing_information_items must be empty when status is UNSUPPORTED_STATE."
            )


@dataclass(frozen=True, slots=True)
class ImplementationBlockerDraft:
    """Represents a typed implementation blocker draft for issue comment creation.

    Attributes:
        issue_title: Implementation issue title currently blocked.
        blocker_summary: Human-readable blocker summary for manager review.
        acceptance_criteria: Acceptance criteria that remain blocked.
        single_pull_request_scope: Scope that Engineer could not complete safely.
        related_issue_use_case: Use case advanced by the blocked implementation issue.
        comment_body_draft: Draft issue comment body describing the blocker.
    """

    issue_title: str
    blocker_summary: str
    acceptance_criteria: tuple[str, ...]
    single_pull_request_scope: str
    related_issue_use_case: UseCaseIdentifier
    comment_body_draft: str

    def __post_init__(self) -> None:
        """Validates the implementation blocker draft."""

        if not self.issue_title.strip():
            raise ValueError("issue_title must not be empty.")
        if not self.blocker_summary.strip():
            raise ValueError("blocker_summary must not be empty.")
        if not self.acceptance_criteria:
            raise ValueError("acceptance_criteria must not be empty.")
        if any(
            not acceptance_criterion.strip() for acceptance_criterion in self.acceptance_criteria
        ):
            raise ValueError("acceptance_criteria must not contain empty values.")
        if len(set(self.acceptance_criteria)) != len(self.acceptance_criteria):
            raise ValueError("acceptance_criteria must not contain duplicate values.")
        if not self.single_pull_request_scope.strip():
            raise ValueError("single_pull_request_scope must not be empty.")
        if not self.comment_body_draft.strip():
            raise ValueError("comment_body_draft must not be empty.")


@dataclass(frozen=True, slots=True)
class ImplementationBlockerResult:
    """Represents whether Engineer can publish an implementation blocker report now.

    Attributes:
        status: High-level outcome for caller-side branching.
        summary_message: Human-readable status summary for orchestration.
        next_state: Workflow state after interpreting the blocker result.
        missing_information_items: Missing inputs required before blocker reporting.
        implementation_blocker_draft: Typed blocker draft when status is `READY`.
    """

    status: ImplementationBlockerStatus
    summary_message: str
    next_state: RequirementDiscoverySessionState
    missing_information_items: tuple[str, ...] = ()
    implementation_blocker_draft: ImplementationBlockerDraft | None = None

    def __post_init__(self) -> None:
        """Validates result consistency."""

        if not self.summary_message.strip():
            raise ValueError("summary_message must not be empty.")
        if any(not missing_item.strip() for missing_item in self.missing_information_items):
            raise ValueError("missing_information_items must not contain empty values.")
        if len(set(self.missing_information_items)) != len(self.missing_information_items):
            raise ValueError("missing_information_items must not contain duplicate values.")
        if not isinstance(self.next_state, RequirementDiscoverySessionState):
            raise ValueError("next_state must be a RequirementDiscoverySessionState value.")

        if self.status is ImplementationBlockerStatus.READY:
            if self.implementation_blocker_draft is None:
                raise ValueError(
                    "implementation_blocker_draft must be provided when status is READY."
                )
            if self.missing_information_items:
                raise ValueError("missing_information_items must be empty when status is READY.")
            if self.next_state is not RequirementDiscoverySessionState.IMPLEMENTATION_BLOCKED:
                raise ValueError("next_state must be STATE_IMPLEMENTATION_BLOCKED when READY.")
            return

        if self.implementation_blocker_draft is not None:
            raise ValueError("implementation_blocker_draft must be empty unless status is READY.")

        if self.status is ImplementationBlockerStatus.INPUT_REQUIRED:
            if not self.missing_information_items:
                raise ValueError(
                    "missing_information_items must not be empty when status is INPUT_REQUIRED."
                )
            if self.next_state is not RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING:
                raise ValueError(
                    "next_state must be STATE_ENGINEER_JOB_RUNNING when status is INPUT_REQUIRED."
                )
            return

        if self.missing_information_items:
            raise ValueError(
                "missing_information_items must be empty when status is UNSUPPORTED_STATE."
            )


@dataclass(frozen=True, slots=True)
class UserDecisionEscalationDraft:
    """Represents a typed manager escalation draft that requests user direction.

    Attributes:
        issue_title: Implementation issue title that remains unresolved.
        blocker_summary: Existing blocker summary that triggered escalation.
        escalation_summary: Manager-side explanation for why user input is required.
        requested_user_input: Specific direction the user must provide.
        comment_body_draft: Draft issue comment body describing the escalation.
    """

    issue_title: str
    blocker_summary: str
    escalation_summary: str
    requested_user_input: str
    comment_body_draft: str

    def __post_init__(self) -> None:
        """Validates the user decision escalation draft."""

        if not self.issue_title.strip():
            raise ValueError("issue_title must not be empty.")
        if not self.blocker_summary.strip():
            raise ValueError("blocker_summary must not be empty.")
        if not self.escalation_summary.strip():
            raise ValueError("escalation_summary must not be empty.")
        if not self.requested_user_input.strip():
            raise ValueError("requested_user_input must not be empty.")
        if not self.comment_body_draft.strip():
            raise ValueError("comment_body_draft must not be empty.")


@dataclass(frozen=True, slots=True)
class UserDecisionEscalationResult:
    """Represents whether Manager can escalate an implementation blocker to the user.

    Attributes:
        status: High-level outcome for caller-side branching.
        summary_message: Human-readable status summary for orchestration.
        next_state: Workflow state after interpreting the escalation result.
        missing_information_items: Missing inputs required before escalation.
        user_decision_escalation_draft: Typed escalation draft when status is `READY`.
    """

    status: UserDecisionEscalationStatus
    summary_message: str
    next_state: RequirementDiscoverySessionState
    missing_information_items: tuple[str, ...] = ()
    user_decision_escalation_draft: UserDecisionEscalationDraft | None = None

    def __post_init__(self) -> None:
        """Validates result consistency."""

        if not self.summary_message.strip():
            raise ValueError("summary_message must not be empty.")
        if any(not missing_item.strip() for missing_item in self.missing_information_items):
            raise ValueError("missing_information_items must not contain empty values.")
        if len(set(self.missing_information_items)) != len(self.missing_information_items):
            raise ValueError("missing_information_items must not contain duplicate values.")
        if not isinstance(self.next_state, RequirementDiscoverySessionState):
            raise ValueError("next_state must be a RequirementDiscoverySessionState value.")

        if self.status is UserDecisionEscalationStatus.READY:
            if self.user_decision_escalation_draft is None:
                raise ValueError(
                    "user_decision_escalation_draft must be provided when status is READY."
                )
            if self.missing_information_items:
                raise ValueError("missing_information_items must be empty when status is READY.")
            if self.next_state is not RequirementDiscoverySessionState.USER_DECISION_REQUIRED:
                raise ValueError("next_state must be STATE_USER_DECISION_REQUIRED when READY.")
            return

        if self.user_decision_escalation_draft is not None:
            raise ValueError("user_decision_escalation_draft must be empty unless status is READY.")

        if self.status is UserDecisionEscalationStatus.INPUT_REQUIRED:
            if not self.missing_information_items:
                raise ValueError(
                    "missing_information_items must not be empty when status is INPUT_REQUIRED."
                )
            if self.next_state is not RequirementDiscoverySessionState.IMPLEMENTATION_BLOCKED:
                raise ValueError(
                    "next_state must be STATE_IMPLEMENTATION_BLOCKED when status is INPUT_REQUIRED."
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

_MANAGER_REQUIREMENT_REVIEW_FOCUS_AREAS = (
    ManagerRequirementReviewFocusArea.REQUIREMENT_OVERVIEW,
    ManagerRequirementReviewFocusArea.DOMAIN_MODEL_ALIGNMENT,
    ManagerRequirementReviewFocusArea.INTERACTION_AND_USE_CASE_ALIGNMENT,
    ManagerRequirementReviewFocusArea.ARCHITECTURE_ALIGNMENT,
    ManagerRequirementReviewFocusArea.OPEN_DECISION_HANDLING,
    ManagerRequirementReviewFocusArea.DOCUMENT_CROSS_CHECK,
)

_IMPLEMENTATION_PULL_REQUEST_BASE_BRANCH = "main"


_MANAGER_IMPLEMENTATION_REVIEW_CHECK_TARGETS = (
    ManagerImplementationReviewCheckTarget.RELATED_ISSUE_TRACEABILITY,
    ManagerImplementationReviewCheckTarget.ACCEPTANCE_CRITERIA,
    ManagerImplementationReviewCheckTarget.SINGLE_PULL_REQUEST_SCOPE,
    ManagerImplementationReviewCheckTarget.BASE_BRANCH_POLICY,
    ManagerImplementationReviewCheckTarget.TEST_EVIDENCE,
    ManagerImplementationReviewCheckTarget.DOCUMENTATION_ALIGNMENT,
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

_MILESTONE_USE_CASE_RULES = (
    (
        UseCaseIdentifier.ORCHESTRATE_DELIVERY_WITH_MANAGER,
        (
            "manager",
            "milestone",
            "planning",
            "backlog",
            "implementation issue",
            "implementation issues",
            "issue split",
            "review workflow",
        ),
    ),
    (
        UseCaseIdentifier.IMPLEMENT_ISSUE_WITH_ENGINEER,
        (
            "engineer",
            "implementation pull request",
            "implementation pr",
            "execute issue",
            "test suite",
            "implementation review",
        ),
    ),
)


@dataclass(frozen=True, slots=True)
class _ImplementationIssueDraftRule:
    """Defines the reusable draft template for one implementation use case."""

    issue_title: str
    issue_summary_prefix: str
    acceptance_criteria: tuple[str, ...]
    single_pull_request_scope: str


_IMPLEMENTATION_ISSUE_DRAFT_RULES = {
    UseCaseIdentifier.ORCHESTRATE_DELIVERY_WITH_MANAGER: _ImplementationIssueDraftRule(
        issue_title="Implement manager milestone planning issue batching",
        issue_summary_prefix=(
            "Enable Manager delivery orchestration to convert the first milestone into "
            "engineer-ready implementation issue drafts."
        ),
        acceptance_criteria=(
            "Return a typed batching result that creates an implementation issue draft for "
            "manager milestone planning from the milestone output.",
            "Include a draft title, overview, and acceptance criteria that an engineer can "
            "complete within one pull request.",
            "Keep the change limited to batching logic and do not call the GitHub issue "
            "creation API.",
        ),
        single_pull_request_scope=(
            "Limit the work to milestone-to-issue batching for manager planning in a single "
            "pull request."
        ),
    ),
    UseCaseIdentifier.IMPLEMENT_ISSUE_WITH_ENGINEER: _ImplementationIssueDraftRule(
        issue_title="Implement engineer handoff for milestone issue drafts",
        issue_summary_prefix=(
            "Prepare the first engineer execution slice so the prioritized milestone draft can "
            "be implemented and reviewed end to end."
        ),
        acceptance_criteria=(
            "Return a typed implementation issue draft for the engineer execution handoff from "
            "the milestone output.",
            "Include acceptance criteria that cover engineer execution, validation, and "
            "implementation pull request handoff.",
            "Keep the issue scope to a single pull request-sized delivery slice.",
        ),
        single_pull_request_scope=(
            "Limit the work to the first engineer execution handoff in a single pull request."
        ),
    ),
}


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


def build_requirement_pull_request_open_result(
    session_summary: RequirementDiscoverySessionSummary,
) -> RequirementPullRequestOpenResult:
    """Builds a typed result for opening the next requirement pull request.

    Args:
        session_summary: Current requirement discovery session snapshot.

    Returns:
        A typed result describing whether pull request creation can proceed now.
    """

    preparation_result = build_requirement_pull_request_preparation_result(session_summary)
    if preparation_result.status is RequirementPullRequestPreparationStatus.READY:
        preparation_draft = preparation_result.preparation_draft
        if preparation_draft is None:
            raise ValueError("preparation_draft must be provided when status is READY.")
        return RequirementPullRequestOpenResult(
            status=RequirementPullRequestOpenStatus.READY,
            summary_message=(
                "Requirement pull request payload is ready and can transition to "
                "STATE_REQUIREMENT_PR_OPEN."
            ),
            next_state=RequirementDiscoverySessionState.PR_OPEN,
            source_prompt_summary=preparation_result.source_prompt_summary,
            pull_request_create_payload=RequirementPullRequestCreatePayload(
                pull_request_title=preparation_draft.pull_request_title,
                pull_request_body_summary=preparation_draft.pull_request_summary,
                updated_documents=preparation_draft.updated_documents,
                target_state=RequirementDiscoverySessionState.PR_OPEN,
            ),
        )

    if preparation_result.status is RequirementPullRequestPreparationStatus.INPUT_REQUIRED:
        return RequirementPullRequestOpenResult(
            status=RequirementPullRequestOpenStatus.INPUT_REQUIRED,
            summary_message=(
                "Continue requirement discovery with additional questions before opening "
                "the requirement pull request."
            ),
            next_state=RequirementDiscoverySessionState.DISCOVERY_IN_PROGRESS,
            source_prompt_summary=preparation_result.source_prompt_summary,
            missing_information_items=preparation_result.missing_information_items,
        )

    return RequirementPullRequestOpenResult(
        status=RequirementPullRequestOpenStatus.UNSUPPORTED_STATE,
        summary_message=(
            "Requirement pull request opening is not supported for workflow state "
            f"{session_summary.current_state.value}."
        ),
        next_state=session_summary.current_state,
    )


def build_manager_requirement_review_input_result(
    session_summary: RequirementDiscoverySessionSummary,
    pull_request_create_payload: RequirementPullRequestCreatePayload | None,
    review_cycle_context: ManagerRequirementReviewCycleContext | None,
) -> ManagerRequirementReviewInputResult:
    """Builds the strict manager input required to review a requirement PR.

    Args:
        session_summary: Current requirement discovery session snapshot.
        pull_request_create_payload: Requirement PR payload created for the opened PR.
        review_cycle_context: Review-cycle metadata for the current manager review pass.

    Returns:
        A typed result describing whether manager review can start immediately.

    Example:
        result = build_manager_requirement_review_input_result(
            session_summary=session_summary,
            pull_request_create_payload=pull_request_create_payload,
            review_cycle_context=review_cycle_context,
        )
        if result.status is ManagerRequirementReviewInputStatus.READY:
            assert result.review_input is not None
    """

    if session_summary.current_state is not RequirementDiscoverySessionState.PR_OPEN:
        return ManagerRequirementReviewInputResult(
            status=ManagerRequirementReviewInputStatus.UNSUPPORTED_STATE,
            summary_message=(
                "Manager requirement review input is not supported for workflow state "
                f"{session_summary.current_state.value}."
            ),
        )

    missing_information_items: list[str] = []
    if pull_request_create_payload is None:
        missing_information_items.append("updated requirement documents")
    if review_cycle_context is None:
        missing_information_items.append("review cycle context")

    if missing_information_items:
        return ManagerRequirementReviewInputResult(
            status=ManagerRequirementReviewInputStatus.INPUT_REQUIRED,
            summary_message=(
                "Additional pull request metadata is required before manager review can start."
            ),
            missing_information_items=tuple(missing_information_items),
        )

    if pull_request_create_payload is None or review_cycle_context is None:
        raise ValueError("Required manager review inputs must be available after validation.")

    documents_to_review = _build_manager_requirement_review_documents(
        pull_request_create_payload.updated_documents
    )
    return ManagerRequirementReviewInputResult(
        status=ManagerRequirementReviewInputStatus.READY,
        summary_message=(
            "Prepared the manager requirement review input for the opened pull request."
        ),
        review_input=ManagerRequirementReviewInput(
            pull_request_title=pull_request_create_payload.pull_request_title,
            pull_request_summary=pull_request_create_payload.pull_request_body_summary,
            updated_documents=pull_request_create_payload.updated_documents,
            documents_to_review=documents_to_review,
            review_cycle_context=review_cycle_context,
            review_focus_areas=_MANAGER_REQUIREMENT_REVIEW_FOCUS_AREAS,
        ),
    )


def build_manager_requirement_review_decision_result(
    review_input: ManagerRequirementReviewInput,
    review_findings: tuple[ManagerRequirementReviewDecisionFinding, ...],
) -> ManagerRequirementReviewDecisionResult:
    """Builds the minimum manager decision result for a requirement review.

    Args:
        review_input: Strict manager review input for the opened requirement PR.
        review_findings: Typed findings from the document consistency review.

    Returns:
        A typed decision result that can later feed the PR review adapter.

    Example:
        result = build_manager_requirement_review_decision_result(
            review_input=review_input,
            review_findings=(),
        )
        assert result.decision is ManagerRequirementReviewDecision.APPROVE
    """

    _validate_manager_requirement_review_findings(review_input, review_findings)
    if not review_findings:
        return ManagerRequirementReviewDecisionResult(
            decision=ManagerRequirementReviewDecision.APPROVE,
            summary_message=("Requirement review passed the minimum document consistency checks."),
            review_body_draft=_build_manager_requirement_review_approve_body_draft(review_input),
        )

    requested_changes = tuple(
        _format_manager_requirement_requested_change(review_finding)
        for review_finding in review_findings
    )
    return ManagerRequirementReviewDecisionResult(
        decision=ManagerRequirementReviewDecision.REQUEST_CHANGES,
        summary_message=(
            "Requirement review found document consistency issues that require updates."
        ),
        review_body_draft=_build_manager_requirement_review_requested_changes_body_draft(
            review_input=review_input,
            requested_changes=requested_changes,
        ),
        findings=review_findings,
        requested_changes=requested_changes,
    )


def build_manager_requirement_review_execution_result(
    session_summary: RequirementDiscoverySessionSummary,
    review_input: ManagerRequirementReviewInput | None,
    decision_result: ManagerRequirementReviewDecisionResult | None,
) -> ManagerRequirementReviewExecutionResult:
    """Builds the minimum execution result for a manager requirement review.

    Args:
        session_summary: Current requirement discovery session snapshot.
        review_input: Strict manager review input for the current review cycle.
        decision_result: Typed decision result created from the review findings.

    Returns:
        A typed result describing whether the manager review can execute immediately.
    """

    if (
        session_summary.current_state
        is not RequirementDiscoverySessionState.MANAGER_REVIEW_IN_PROGRESS
    ):
        return ManagerRequirementReviewExecutionResult(
            status=ManagerRequirementReviewExecutionStatus.UNSUPPORTED_STATE,
            summary_message=(
                "Manager requirement review execution is not supported for workflow state "
                f"{session_summary.current_state.value}."
            ),
            next_state=session_summary.current_state,
        )

    missing_information_items: list[str] = []
    if review_input is None:
        missing_information_items.append("manager requirement review input")
    if decision_result is None:
        missing_information_items.append("manager requirement review decision result")

    if missing_information_items:
        return ManagerRequirementReviewExecutionResult(
            status=ManagerRequirementReviewExecutionStatus.INPUT_REQUIRED,
            summary_message=(
                "Additional review metadata is required before manager review execution "
                "can proceed."
            ),
            next_state=RequirementDiscoverySessionState.MANAGER_REVIEW_IN_PROGRESS,
            missing_information_items=tuple(missing_information_items),
        )

    if review_input is None or decision_result is None:
        raise ValueError("Required manager review execution inputs must be available.")

    return ManagerRequirementReviewExecutionResult(
        status=ManagerRequirementReviewExecutionStatus.READY,
        summary_message=(
            "Prepared the manager requirement review execution payload and next workflow state."
        ),
        next_state=_build_manager_requirement_review_next_state(decision_result.decision),
        review_execution_payload=ManagerRequirementReviewExecutionPayload(
            pull_request_title=review_input.pull_request_title,
            review_decision=decision_result.decision,
            review_body=decision_result.review_body_draft,
        ),
    )


def build_milestone_planning_result(
    session_summary: RequirementDiscoverySessionSummary,
    requirement_review_execution_result: ManagerRequirementReviewExecutionResult | None,
    requirement_documents_summary: str | None,
) -> MilestonePlanningResult:
    """Builds the first strict milestone planning model after requirement approval.

    Args:
        session_summary: Current requirement discovery session snapshot.
        requirement_review_execution_result: Approved manager review execution result.
        requirement_documents_summary: Summary of approved requirement and use-case documents.

    Returns:
        A typed result describing whether milestone planning can proceed now.

    Example:
        result = build_milestone_planning_result(
            session_summary=session_summary,
            requirement_review_execution_result=requirement_review_execution_result,
            requirement_documents_summary=requirement_documents_summary,
        )
        if result.status is MilestonePlanningStatus.READY:
            assert result.milestone_planning_model is not None
    """

    if session_summary.current_state is not RequirementDiscoverySessionState.REQUIREMENT_APPROVED:
        return MilestonePlanningResult(
            status=MilestonePlanningStatus.UNSUPPORTED_STATE,
            summary_message=(
                "Milestone planning is not supported for workflow state "
                f"{session_summary.current_state.value}."
            ),
            next_state=session_summary.current_state,
        )

    missing_information_items: list[str] = []
    if not _is_requirement_review_approved(requirement_review_execution_result):
        missing_information_items.append("approved requirement review result")
    if requirement_documents_summary is None or not requirement_documents_summary.strip():
        missing_information_items.append("requirement documents summary")

    if missing_information_items:
        return MilestonePlanningResult(
            status=MilestonePlanningStatus.INPUT_REQUIRED,
            summary_message=(
                "Approved requirement review output and document summaries are required "
                "before milestone planning can begin."
            ),
            next_state=RequirementDiscoverySessionState.REQUIREMENT_APPROVED,
            missing_information_items=tuple(missing_information_items),
        )

    if requirement_documents_summary is None:
        raise ValueError("requirement_documents_summary must be available after validation.")

    normalized_requirement_documents_summary = requirement_documents_summary.casefold()
    target_use_cases = _build_milestone_target_use_cases(normalized_requirement_documents_summary)
    if not target_use_cases:
        return MilestonePlanningResult(
            status=MilestonePlanningStatus.INPUT_REQUIRED,
            summary_message=(
                "The approved requirement summary does not yet identify the first delivery "
                "use cases for milestone planning."
            ),
            next_state=RequirementDiscoverySessionState.REQUIREMENT_APPROVED,
            missing_information_items=("target use cases for the first milestone",),
        )

    return MilestonePlanningResult(
        status=MilestonePlanningStatus.READY,
        summary_message=(
            "Prepared the first delivery milestone from the approved requirement summary."
        ),
        next_state=RequirementDiscoverySessionState.MILESTONE_PLANNING,
        milestone_planning_model=MilestonePlanningModel(
            milestone_goal=_build_milestone_goal(target_use_cases),
            completion_criteria=_build_milestone_completion_criteria(target_use_cases),
            target_use_cases=target_use_cases,
            implementation_focuses=_build_milestone_implementation_focuses(target_use_cases),
        ),
    )


def build_implementation_issue_batching_result(
    session_summary: RequirementDiscoverySessionSummary,
    milestone_planning_result: MilestonePlanningResult | None,
) -> ImplementationIssueBatchingResult:
    """Builds engineer-ready implementation issue drafts from milestone planning output.

    Args:
        session_summary: Current requirement discovery session snapshot.
        milestone_planning_result: Strict milestone planning result produced by the previous step.

    Returns:
        A typed result describing whether implementation issue drafting can proceed now.

    Example:
        result = build_implementation_issue_batching_result(
            session_summary=session_summary,
            milestone_planning_result=milestone_planning_result,
        )
        if result.status is ImplementationIssueBatchingStatus.READY:
            assert result.implementation_issue_drafts
    """

    if session_summary.current_state is not RequirementDiscoverySessionState.MILESTONE_PLANNING:
        return ImplementationIssueBatchingResult(
            status=ImplementationIssueBatchingStatus.UNSUPPORTED_STATE,
            summary_message=(
                "Implementation issue batching is not supported for workflow state "
                f"{session_summary.current_state.value}."
            ),
            next_state=session_summary.current_state,
        )

    if (
        milestone_planning_result is None
        or milestone_planning_result.status is not MilestonePlanningStatus.READY
    ):
        return ImplementationIssueBatchingResult(
            status=ImplementationIssueBatchingStatus.INPUT_REQUIRED,
            summary_message=(
                "A ready milestone planning model is required before implementation issue "
                "drafting can begin."
            ),
            next_state=RequirementDiscoverySessionState.MILESTONE_PLANNING,
            missing_information_items=("milestone planning model",),
        )

    milestone_planning_model = milestone_planning_result.milestone_planning_model
    if milestone_planning_model is None:
        raise ValueError("milestone_planning_model must be provided when status is READY.")

    implementation_issue_drafts = _build_implementation_issue_drafts(milestone_planning_model)
    if not implementation_issue_drafts:
        return ImplementationIssueBatchingResult(
            status=ImplementationIssueBatchingStatus.INPUT_REQUIRED,
            summary_message=(
                "The milestone planning output does not yet contain supported engineer-sized "
                "implementation issue drafts."
            ),
            next_state=RequirementDiscoverySessionState.MILESTONE_PLANNING,
            missing_information_items=("supported implementation issue drafts",),
        )

    return ImplementationIssueBatchingResult(
        status=ImplementationIssueBatchingStatus.READY,
        summary_message=(
            f"Prepared {len(implementation_issue_drafts)} implementation issue drafts from "
            "the milestone plan."
        ),
        next_state=RequirementDiscoverySessionState.MILESTONE_PLANNING,
        implementation_issue_drafts=implementation_issue_drafts,
    )


def build_implementation_issue_creation_result(
    session_summary: RequirementDiscoverySessionSummary,
    batching_result: ImplementationIssueBatchingResult | None,
) -> ImplementationIssueCreationResult:
    """Builds typed GitHub issue creation payloads from batched implementation drafts.

    Args:
        session_summary: Current requirement discovery session snapshot.
        batching_result: Strict batching result produced by the previous milestone step.

    Returns:
        A typed result describing whether implementation issue creation can proceed now.

    Example:
        result = build_implementation_issue_creation_result(
            session_summary=session_summary,
            batching_result=batching_result,
        )
        if result.status is ImplementationIssueCreationStatus.READY:
            assert result.issue_create_payloads
    """

    if session_summary.current_state is not RequirementDiscoverySessionState.MILESTONE_PLANNING:
        return ImplementationIssueCreationResult(
            status=ImplementationIssueCreationStatus.UNSUPPORTED_STATE,
            summary_message=(
                "Implementation issue creation payload emission is not supported for workflow "
                f"state {session_summary.current_state.value}."
            ),
            next_state=session_summary.current_state,
        )

    if (
        batching_result is None
        or batching_result.status is not ImplementationIssueBatchingStatus.READY
    ):
        missing_information_items = (
            ("implementation issue drafts",)
            if batching_result is None
            else batching_result.missing_information_items or ("implementation issue drafts",)
        )
        return ImplementationIssueCreationResult(
            status=ImplementationIssueCreationStatus.INPUT_REQUIRED,
            summary_message=(
                "Implementation issue drafts are required before GitHub issue creation payloads "
                "can be emitted."
            ),
            next_state=RequirementDiscoverySessionState.MILESTONE_PLANNING,
            missing_information_items=missing_information_items,
        )

    issue_create_payloads = tuple(
        ImplementationIssueCreatePayload(
            target_use_case=implementation_issue_draft.target_use_case,
            issue_title=implementation_issue_draft.issue_title,
            issue_overview=implementation_issue_draft.issue_summary,
            acceptance_criteria=implementation_issue_draft.acceptance_criteria,
            single_pull_request_scope=implementation_issue_draft.single_pull_request_scope,
            target_state=RequirementDiscoverySessionState.IMPLEMENTATION_BACKLOG_READY,
        )
        for implementation_issue_draft in batching_result.implementation_issue_drafts
    )
    return ImplementationIssueCreationResult(
        status=ImplementationIssueCreationStatus.READY,
        summary_message=(
            f"Prepared {len(issue_create_payloads)} implementation issue creation payloads and "
            "transitioned the workflow to STATE_IMPLEMENTATION_BACKLOG_READY."
        ),
        next_state=RequirementDiscoverySessionState.IMPLEMENTATION_BACKLOG_READY,
        issue_create_payloads=issue_create_payloads,
    )


def build_engineer_job_input_result(
    issue_create_payload: ImplementationIssueCreatePayload | None,
) -> EngineerJobInputResult:
    """Builds the strict engineer job input from one backlog-ready issue payload.

    Args:
        issue_create_payload: One implementation issue payload prepared for backlog-ready state.

    Returns:
        A typed result describing whether an engineer job can start immediately.

    Example:
        result = build_engineer_job_input_result(issue_create_payload)
        if result.status is EngineerJobInputStatus.READY:
            assert result.engineer_job_input is not None
    """

    if issue_create_payload is None:
        return EngineerJobInputResult(
            status=EngineerJobInputStatus.INPUT_REQUIRED,
            summary_message=(
                "An implementation issue creation payload is required before the engineer "
                "job can start."
            ),
            missing_information_items=("implementation issue create payload",),
        )

    if issue_create_payload.target_use_case not in {
        UseCaseIdentifier.ORCHESTRATE_DELIVERY_WITH_MANAGER,
        UseCaseIdentifier.IMPLEMENT_ISSUE_WITH_ENGINEER,
    }:
        return EngineerJobInputResult(
            status=EngineerJobInputStatus.UNSUPPORTED_STATE,
            summary_message=(
                "Engineer job input is not supported for use case "
                f"{issue_create_payload.target_use_case.value}."
            ),
        )

    return EngineerJobInputResult(
        status=EngineerJobInputStatus.READY,
        summary_message=(
            "Prepared the strict engineer job input for the backlog-ready implementation issue."
        ),
        engineer_job_input=EngineerJobInput(
            issue_title=issue_create_payload.issue_title,
            issue_overview=issue_create_payload.issue_overview,
            acceptance_criteria=issue_create_payload.acceptance_criteria,
            single_pull_request_scope=issue_create_payload.single_pull_request_scope,
            related_issue_use_case=issue_create_payload.target_use_case,
        ),
    )


def build_implementation_pull_request_open_result(
    *,
    current_state: RequirementDiscoverySessionState,
    work_item_contract: EngineerExecutionWorkItemContract | None,
    test_evidence: tuple[str, ...] | None,
    implementation_blocker_result: ImplementationBlockerResult | None,
) -> ImplementationPullRequestOpenResult:
    """Builds the strict result for opening the next implementation pull request.

    Args:
        current_state: Workflow state observed before preparing the implementation pull request.
        work_item_contract: Validated engineer execution work item for the running implementation.
        test_evidence: Local verification evidence collected after implementation completed.
        implementation_blocker_result: Existing blocker result when implementation is blocked.

    Returns:
        A typed result describing whether implementation pull request creation can proceed now.

    Example:
        result = build_implementation_pull_request_open_result(
            current_state=RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING,
            work_item_contract=work_item_contract,
            test_evidence=("make test passed.", "make lint passed."),
            implementation_blocker_result=None,
        )
        if result.status is ImplementationPullRequestOpenStatus.READY:
            assert result.pull_request_create_payload is not None
    """

    if current_state not in (
        RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING,
        RequirementDiscoverySessionState.IMPLEMENTATION_BLOCKED,
    ):
        return ImplementationPullRequestOpenResult(
            status=ImplementationPullRequestOpenStatus.UNSUPPORTED_STATE,
            summary_message=(
                "Implementation pull request opening is not supported for workflow state "
                f"{current_state.value}."
            ),
            next_state=current_state,
        )

    if current_state is RequirementDiscoverySessionState.IMPLEMENTATION_BLOCKED:
        if (
            implementation_blocker_result is not None
            and implementation_blocker_result.status is ImplementationBlockerStatus.READY
        ):
            implementation_blocker_draft = (
                implementation_blocker_result.implementation_blocker_draft
            )
            if implementation_blocker_draft is None:
                raise ValueError(
                    "implementation_blocker_draft must be available when blocker result is READY."
                )
            return ImplementationPullRequestOpenResult(
                status=ImplementationPullRequestOpenStatus.BLOCKED,
                summary_message=(
                    "Implementation remains blocked, so no implementation pull request payload "
                    "will be created."
                ),
                next_state=RequirementDiscoverySessionState.IMPLEMENTATION_BLOCKED,
                blocker_summary=implementation_blocker_draft.blocker_summary,
            )

        return ImplementationPullRequestOpenResult(
            status=ImplementationPullRequestOpenStatus.INPUT_REQUIRED,
            summary_message=(
                "The workflow is already blocked, so a ready implementation blocker result is "
                "required instead of an implementation pull request payload."
            ),
            next_state=RequirementDiscoverySessionState.IMPLEMENTATION_BLOCKED,
            missing_information_items=("ready implementation blocker result",),
        )

    if (
        implementation_blocker_result is not None
        and implementation_blocker_result.status is ImplementationBlockerStatus.READY
    ):
        implementation_blocker_draft = implementation_blocker_result.implementation_blocker_draft
        if implementation_blocker_draft is None:
            raise ValueError(
                "implementation_blocker_draft must be available when blocker result is READY."
            )
        return ImplementationPullRequestOpenResult(
            status=ImplementationPullRequestOpenStatus.BLOCKED,
            summary_message=(
                "Implementation reported a blocker, so no implementation pull request payload "
                "will be created."
            ),
            next_state=RequirementDiscoverySessionState.IMPLEMENTATION_BLOCKED,
            blocker_summary=implementation_blocker_draft.blocker_summary,
        )

    normalized_test_evidence = _normalize_test_evidence(test_evidence)
    missing_information_items: list[str] = []
    if work_item_contract is None:
        missing_information_items.append("engineer execution work item contract")
    if normalized_test_evidence is None:
        missing_information_items.append("test evidence")

    if missing_information_items:
        return ImplementationPullRequestOpenResult(
            status=ImplementationPullRequestOpenStatus.INPUT_REQUIRED,
            summary_message=(
                "Engineer needs a validated execution work item and local test evidence before "
                "opening the implementation pull request."
            ),
            next_state=RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING,
            missing_information_items=tuple(missing_information_items),
        )

    if work_item_contract is None or normalized_test_evidence is None:
        raise ValueError("Implementation pull request inputs must be available after validation.")

    issue_work_item_contract = work_item_contract.issue_work_item_contract
    engineer_job_input = work_item_contract.engineer_job_input
    related_issue_identifier = issue_work_item_contract.to_issue_identifier()
    return ImplementationPullRequestOpenResult(
        status=ImplementationPullRequestOpenStatus.READY,
        summary_message=(
            "Implementation pull request payload is ready and can transition to "
            "STATE_IMPLEMENTATION_PR_OPEN."
        ),
        next_state=RequirementDiscoverySessionState.IMPLEMENTATION_PR_OPEN,
        pull_request_create_payload=ImplementationPullRequestCreatePayload(
            branch_name=_build_implementation_pull_request_branch_name(
                issue_number=issue_work_item_contract.issue_number,
                issue_title=issue_work_item_contract.issue_title,
            ),
            base_branch_name=_IMPLEMENTATION_PULL_REQUEST_BASE_BRANCH,
            pull_request_title=(
                f"Implement issue #{issue_work_item_contract.issue_number}: "
                f"{issue_work_item_contract.issue_title}"
            ),
            pull_request_body_summary=_build_implementation_pull_request_body_summary(
                related_issue_identifier=related_issue_identifier,
                engineer_job_input=engineer_job_input,
            ),
            test_evidence=normalized_test_evidence,
            related_issue_identifier=related_issue_identifier,
            related_issue_title=issue_work_item_contract.issue_title,
            issue_overview=engineer_job_input.issue_overview,
            acceptance_criteria=engineer_job_input.acceptance_criteria,
            single_pull_request_scope=engineer_job_input.single_pull_request_scope,
            target_state=RequirementDiscoverySessionState.IMPLEMENTATION_PR_OPEN,
        ),
    )


def build_manager_implementation_review_input_result(
    session_summary: RequirementDiscoverySessionSummary,
    pull_request_create_payload: ImplementationPullRequestCreatePayload | None,
    opened_pull_request_metadata: OpenedImplementationPullRequestMetadata | None,
) -> ManagerImplementationReviewInputResult:
    """Builds the strict manager input required to review an implementation PR.

    Args:
        session_summary: Current requirement discovery session snapshot.
        pull_request_create_payload: Implementation PR payload prepared before the PR opened.
        opened_pull_request_metadata: Opened PR metadata captured after GitHub created the PR.

    Returns:
        A typed result describing whether manager implementation review can start immediately.
    """

    if session_summary.current_state is not RequirementDiscoverySessionState.IMPLEMENTATION_PR_OPEN:
        return ManagerImplementationReviewInputResult(
            status=ManagerImplementationReviewInputStatus.UNSUPPORTED_STATE,
            summary_message=(
                "Manager implementation review input is not supported for workflow state "
                f"{session_summary.current_state.value}."
            ),
        )

    if pull_request_create_payload is None and opened_pull_request_metadata is None:
        return ManagerImplementationReviewInputResult(
            status=ManagerImplementationReviewInputStatus.INPUT_REQUIRED,
            summary_message=(
                "Opened implementation pull request metadata is required before manager "
                "review can start."
            ),
            missing_information_items=(
                "implementation pull request payload or opened pull request metadata",
            ),
        )

    if opened_pull_request_metadata is not None:
        pull_request_number: int | None = opened_pull_request_metadata.pull_request_number
        branch_name = opened_pull_request_metadata.branch_name
        base_branch_name = opened_pull_request_metadata.base_branch_name
        pull_request_title = opened_pull_request_metadata.pull_request_title
        pull_request_summary = opened_pull_request_metadata.pull_request_body_summary
        test_evidence = opened_pull_request_metadata.test_evidence
        related_issue_identifier = opened_pull_request_metadata.related_issue_identifier
        related_issue_title = opened_pull_request_metadata.related_issue_title
        issue_overview = opened_pull_request_metadata.issue_overview
        acceptance_criteria = opened_pull_request_metadata.acceptance_criteria
        single_pull_request_scope = opened_pull_request_metadata.single_pull_request_scope
    else:
        if pull_request_create_payload is None:
            raise ValueError("Implementation review source must be available after validation.")
        pull_request_number = None
        branch_name = pull_request_create_payload.branch_name
        base_branch_name = pull_request_create_payload.base_branch_name
        pull_request_title = pull_request_create_payload.pull_request_title
        pull_request_summary = pull_request_create_payload.pull_request_body_summary
        test_evidence = pull_request_create_payload.test_evidence
        related_issue_identifier = pull_request_create_payload.related_issue_identifier
        related_issue_title = pull_request_create_payload.related_issue_title
        issue_overview = pull_request_create_payload.issue_overview
        acceptance_criteria = pull_request_create_payload.acceptance_criteria
        single_pull_request_scope = pull_request_create_payload.single_pull_request_scope

    return ManagerImplementationReviewInputResult(
        status=ManagerImplementationReviewInputStatus.READY,
        summary_message=(
            "Prepared the manager implementation review input for the opened pull request."
        ),
        review_input=ManagerImplementationReviewInput(
            pull_request_number=pull_request_number,
            branch_name=branch_name,
            base_branch_name=base_branch_name,
            pull_request_title=pull_request_title,
            pull_request_summary=pull_request_summary,
            related_issue_identifier=related_issue_identifier,
            related_issue_title=related_issue_title,
            issue_overview=issue_overview,
            acceptance_criteria=acceptance_criteria,
            single_pull_request_scope=single_pull_request_scope,
            test_evidence=test_evidence,
            review_targets=_MANAGER_IMPLEMENTATION_REVIEW_CHECK_TARGETS,
            transition_context=ManagerImplementationReviewTransitionContext(
                current_state=RequirementDiscoverySessionState.IMPLEMENTATION_PR_OPEN,
                next_state=RequirementDiscoverySessionState.IMPLEMENTATION_REVIEW_IN_PROGRESS,
                required_operation=ManagerImplementationReviewOperation.REVIEW_ENGINEER_PR,
            ),
        ),
    )


def build_manager_implementation_review_decision_result(
    review_input: ManagerImplementationReviewInput | None,
    review_findings: tuple[ManagerImplementationReviewDecisionFinding, ...],
    retry_limit_reason: str | None,
    escalation_reason: str | None,
) -> ManagerImplementationReviewDecisionResult:
    """Builds the strict manager decision result for an implementation review.

    Args:
        review_input: Strict manager review input for the opened implementation pull request.
        review_findings: Typed findings collected during the implementation review.
        retry_limit_reason: Rationale for stopping automated review retries when applicable.
        escalation_reason: Rationale for escalating to the user when applicable.

    Returns:
        A typed decision result that can later feed review execution or user escalation.

    Example:
        result = build_manager_implementation_review_decision_result(
            review_input=review_input,
            review_findings=(),
            retry_limit_reason=None,
            escalation_reason=None,
        )
        assert result.decision is ManagerImplementationReviewDecision.APPROVE
    """

    if review_input is None:
        return ManagerImplementationReviewDecisionResult(
            status=ManagerImplementationReviewDecisionStatus.INPUT_REQUIRED,
            summary_message=(
                "Manager implementation review input is required before the review decision "
                "can be determined."
            ),
            missing_information_items=("manager implementation review input",),
        )

    unsupported_check_targets = _collect_unsupported_implementation_review_check_targets(
        review_input=review_input,
        review_findings=review_findings,
    )
    if unsupported_check_targets:
        return ManagerImplementationReviewDecisionResult(
            status=ManagerImplementationReviewDecisionStatus.UNSUPPORTED_REVIEW_SCOPE,
            summary_message=(
                "The provided implementation review findings include check targets outside "
                "the declared review scope."
            ),
            unsupported_check_targets=unsupported_check_targets,
        )

    normalized_retry_limit_reason = _normalize_optional_reason(retry_limit_reason)
    normalized_escalation_reason = _normalize_optional_reason(escalation_reason)
    requested_changes = tuple(
        _format_manager_implementation_requested_change(review_finding)
        for review_finding in review_findings
    )

    if normalized_retry_limit_reason is not None or normalized_escalation_reason is not None:
        return ManagerImplementationReviewDecisionResult(
            status=ManagerImplementationReviewDecisionStatus.READY,
            summary_message=(
                "Implementation review requires user direction before Manager can finalize "
                "the outcome."
            ),
            decision=ManagerImplementationReviewDecision.USER_DECISION_REQUIRED,
            findings=review_findings,
            requested_changes=requested_changes,
            retry_limit_reason=normalized_retry_limit_reason,
            escalation_reason=normalized_escalation_reason,
        )

    if not review_findings:
        return ManagerImplementationReviewDecisionResult(
            status=ManagerImplementationReviewDecisionStatus.READY,
            summary_message=(
                "Implementation review passed the minimum manager checks for approval."
            ),
            decision=ManagerImplementationReviewDecision.APPROVE,
            review_body_draft=_build_manager_implementation_review_approve_body_draft(review_input),
        )

    return ManagerImplementationReviewDecisionResult(
        status=ManagerImplementationReviewDecisionStatus.READY,
        summary_message=(
            "Implementation review found changes that Engineer must address before approval."
        ),
        decision=ManagerImplementationReviewDecision.REQUEST_CHANGES,
        review_body_draft=_build_manager_implementation_review_requested_changes_body_draft(
            review_input=review_input,
            requested_changes=requested_changes,
        ),
        findings=review_findings,
        requested_changes=requested_changes,
    )


def build_manager_implementation_review_execution_result(
    session_summary: RequirementDiscoverySessionSummary,
    review_input: ManagerImplementationReviewInput | None,
    decision_result: ManagerImplementationReviewDecisionResult | None,
) -> ManagerImplementationReviewExecutionResult:
    """Builds the minimum execution result for a manager implementation review.

    Args:
        session_summary: Current requirement discovery session snapshot.
        review_input: Strict manager review input for the current implementation review.
        decision_result: Typed decision result created from the review findings.

    Returns:
        A typed result describing whether the manager review can execute immediately.
    """

    if (
        session_summary.current_state
        is not RequirementDiscoverySessionState.IMPLEMENTATION_REVIEW_IN_PROGRESS
    ):
        return ManagerImplementationReviewExecutionResult(
            status=ManagerImplementationReviewExecutionStatus.UNSUPPORTED_STATE,
            summary_message=(
                "Manager implementation review execution is not supported for workflow state "
                f"{session_summary.current_state.value}."
            ),
            next_state=session_summary.current_state,
        )

    missing_information_items: list[str] = []
    if review_input is None:
        missing_information_items.append("manager implementation review input")
    if decision_result is None:
        missing_information_items.append("manager implementation review decision result")

    if missing_information_items:
        return ManagerImplementationReviewExecutionResult(
            status=ManagerImplementationReviewExecutionStatus.INPUT_REQUIRED,
            summary_message=(
                "Additional review metadata is required before manager implementation review "
                "execution can proceed."
            ),
            next_state=RequirementDiscoverySessionState.IMPLEMENTATION_REVIEW_IN_PROGRESS,
            missing_information_items=tuple(missing_information_items),
        )

    if review_input is None or decision_result is None:
        raise ValueError("Required manager implementation review inputs must be available.")

    if decision_result.status is not ManagerImplementationReviewDecisionStatus.READY:
        return ManagerImplementationReviewExecutionResult(
            status=ManagerImplementationReviewExecutionStatus.UNSUPPORTED_DECISION,
            summary_message=(
                "Manager implementation review execution only supports READY decision results."
            ),
            next_state=RequirementDiscoverySessionState.IMPLEMENTATION_REVIEW_IN_PROGRESS,
        )

    if decision_result.decision is None:
        raise ValueError("decision_result.decision must be available when status is READY.")

    next_state = _build_manager_implementation_review_next_state(decision_result.decision)
    if decision_result.decision is ManagerImplementationReviewDecision.USER_DECISION_REQUIRED:
        return ManagerImplementationReviewExecutionResult(
            status=ManagerImplementationReviewExecutionStatus.READY,
            summary_message=(
                "Implementation review requires user direction before Manager can execute a "
                "GitHub review."
            ),
            next_state=next_state,
        )

    if review_input.pull_request_number is None:
        return ManagerImplementationReviewExecutionResult(
            status=ManagerImplementationReviewExecutionStatus.INPUT_REQUIRED,
            summary_message=(
                "An implementation pull request number is required before manager review "
                "execution can proceed."
            ),
            next_state=RequirementDiscoverySessionState.IMPLEMENTATION_REVIEW_IN_PROGRESS,
            missing_information_items=("implementation pull request number",),
        )

    if decision_result.review_body_draft is None:
        raise ValueError(
            "decision_result.review_body_draft must be available for executable review decisions."
        )

    return ManagerImplementationReviewExecutionResult(
        status=ManagerImplementationReviewExecutionStatus.READY,
        summary_message=(
            "Prepared the manager implementation review execution payload and next workflow state."
        ),
        next_state=next_state,
        review_execution_payload=ManagerImplementationReviewExecutionPayload(
            pull_request_number=review_input.pull_request_number,
            pull_request_title=review_input.pull_request_title,
            review_decision=decision_result.decision,
            review_body=decision_result.review_body_draft,
        ),
    )


def build_engineer_implementation_reentry_input_result(
    *,
    session_summary: RequirementDiscoverySessionSummary,
    review_input: ManagerImplementationReviewInput | None,
    execution_result: ManagerImplementationReviewExecutionResult | None,
    requested_changes: tuple[str, ...],
) -> EngineerImplementationReentryInputResult:
    """Builds the strict engineer re-entry input after manager requested changes.

    Args:
        session_summary: Current delivery workflow session snapshot.
        review_input: Strict manager review input captured for the implementation pull request.
        execution_result: Execution result produced from the manager implementation review.
        requested_changes: Requested changes that the engineer must address before updating the
            pull request.

    Returns:
        A typed result describing whether engineer re-entry can resume immediately.
    """

    if (
        session_summary.current_state
        is not RequirementDiscoverySessionState.ENGINEER_CHANGES_REQUESTED
    ):
        return EngineerImplementationReentryInputResult(
            status=EngineerImplementationReentryInputStatus.UNSUPPORTED_STATE,
            summary_message=(
                "Engineer re-entry input is not supported for workflow state "
                f"{session_summary.current_state.value}."
            ),
        )

    missing_information_items: list[str] = []
    if review_input is None:
        missing_information_items.append("manager implementation review input")
    if execution_result is None:
        missing_information_items.append("manager implementation review execution result")
    if not requested_changes:
        missing_information_items.append("requested changes")

    if missing_information_items:
        return EngineerImplementationReentryInputResult(
            status=EngineerImplementationReentryInputStatus.INPUT_REQUIRED,
            summary_message=(
                "Manager review metadata and requested changes are required before engineer "
                "re-entry can resume."
            ),
            missing_information_items=tuple(missing_information_items),
        )

    if review_input is None or execution_result is None:
        raise ValueError("Engineer re-entry inputs must be available after validation.")

    if execution_result.status is not ManagerImplementationReviewExecutionStatus.READY:
        return EngineerImplementationReentryInputResult(
            status=EngineerImplementationReentryInputStatus.UNSUPPORTED_STATE,
            summary_message=(
                "Engineer re-entry input requires a READY manager implementation review "
                "execution result."
            ),
        )

    if (
        execution_result.next_state
        is not RequirementDiscoverySessionState.ENGINEER_CHANGES_REQUESTED
    ):
        return EngineerImplementationReentryInputResult(
            status=EngineerImplementationReentryInputStatus.UNSUPPORTED_STATE,
            summary_message=(
                "Engineer re-entry input only supports manager review execution results that "
                "transition to STATE_ENGINEER_CHANGES_REQUESTED."
            ),
        )

    review_execution_payload = execution_result.review_execution_payload
    if review_execution_payload is None:
        return EngineerImplementationReentryInputResult(
            status=EngineerImplementationReentryInputStatus.INPUT_REQUIRED,
            summary_message=(
                "A review execution payload is required to resume engineer work from requested "
                "changes."
            ),
            missing_information_items=("manager implementation review execution payload",),
        )

    if (
        review_execution_payload.review_decision
        is not ManagerImplementationReviewDecision.REQUEST_CHANGES
    ):
        return EngineerImplementationReentryInputResult(
            status=EngineerImplementationReentryInputStatus.UNSUPPORTED_STATE,
            summary_message=(
                "Engineer re-entry input only supports implementation reviews that requested "
                "changes."
            ),
        )

    return EngineerImplementationReentryInputResult(
        status=EngineerImplementationReentryInputStatus.READY,
        summary_message=(
            "Prepared the strict engineer re-entry input for the implementation pull request."
        ),
        reentry_input=EngineerImplementationReentryInput(
            pull_request_number=review_execution_payload.pull_request_number,
            pull_request_title=review_execution_payload.pull_request_title,
            branch_name=review_input.branch_name,
            base_branch_name=review_input.base_branch_name,
            related_issue_identifier=review_input.related_issue_identifier,
            related_issue_title=review_input.related_issue_title,
            issue_overview=review_input.issue_overview,
            acceptance_criteria=review_input.acceptance_criteria,
            single_pull_request_scope=review_input.single_pull_request_scope,
            requested_changes=requested_changes,
            transition_context=EngineerImplementationReentryTransitionContext(
                current_state=RequirementDiscoverySessionState.ENGINEER_CHANGES_REQUESTED,
                next_state=RequirementDiscoverySessionState.IMPLEMENTATION_PR_OPEN,
                required_operation=(
                    EngineerImplementationReentryOperation.UPDATE_IMPLEMENTATION_PULL_REQUEST
                ),
            ),
        ),
    )


def build_implementation_post_merge_delivery_routing_result(
    *,
    session_summary: RequirementDiscoverySessionSummary,
    remaining_milestone_issue_count: int | None,
    all_requirements_satisfied: bool | None,
) -> ImplementationPostMergeDeliveryRoutingResult:
    """Builds the strict delivery routing result after an implementation PR merge.

    Args:
        session_summary: Current requirement discovery session snapshot.
        remaining_milestone_issue_count: Count of implementation issues still needed to
            complete the current milestone.
        all_requirements_satisfied: Whether the overall delivery scope is now complete.

    Returns:
        A typed result describing whether delivery should return to the implementation
        backlog, the next milestone planning step, or delivery completion.

    Example:
        result = build_implementation_post_merge_delivery_routing_result(
            session_summary=session_summary,
            remaining_milestone_issue_count=0,
            all_requirements_satisfied=False,
        )
        if result.status is ImplementationPostMergeDeliveryRoutingStatus.READY:
            assert result.routing_reason is not None
    """

    if (
        session_summary.current_state
        is not RequirementDiscoverySessionState.IMPLEMENTATION_PR_MERGED
    ):
        return ImplementationPostMergeDeliveryRoutingResult(
            status=ImplementationPostMergeDeliveryRoutingStatus.UNSUPPORTED_STATE,
            summary_message=(
                "Post-merge delivery routing is not supported for workflow state "
                f"{session_summary.current_state.value}."
            ),
            next_state=session_summary.current_state,
        )

    missing_information_items: list[str] = []
    if remaining_milestone_issue_count is None:
        missing_information_items.append("remaining milestone issue count")
    if all_requirements_satisfied is None:
        missing_information_items.append("all requirements satisfied flag")

    if missing_information_items:
        return ImplementationPostMergeDeliveryRoutingResult(
            status=ImplementationPostMergeDeliveryRoutingStatus.INPUT_REQUIRED,
            summary_message=(
                "Remaining milestone issue tracking and requirement completion status are "
                "required before post-merge delivery routing can continue."
            ),
            next_state=RequirementDiscoverySessionState.IMPLEMENTATION_PR_MERGED,
            missing_information_items=tuple(missing_information_items),
        )

    if remaining_milestone_issue_count is None or all_requirements_satisfied is None:
        raise ValueError("Routing inputs must be available after validation.")

    if remaining_milestone_issue_count < 0:
        raise ValueError("remaining_milestone_issue_count must be zero or greater.")
    if all_requirements_satisfied and remaining_milestone_issue_count > 0:
        raise ValueError(
            "remaining_milestone_issue_count must be zero when all_requirements_satisfied is True."
        )

    if remaining_milestone_issue_count > 0:
        return ImplementationPostMergeDeliveryRoutingResult(
            status=ImplementationPostMergeDeliveryRoutingStatus.READY,
            summary_message=(
                "Implementation backlog still contains milestone work, so delivery returns "
                "to STATE_IMPLEMENTATION_BACKLOG_READY."
            ),
            next_state=RequirementDiscoverySessionState.IMPLEMENTATION_BACKLOG_READY,
            routing_reason=(
                ImplementationPostMergeDeliveryRoutingReason.MORE_ISSUES_NEEDED_FOR_MILESTONE
            ),
            remaining_milestone_issue_count=remaining_milestone_issue_count,
            all_requirements_satisfied=all_requirements_satisfied,
        )

    if all_requirements_satisfied:
        return ImplementationPostMergeDeliveryRoutingResult(
            status=ImplementationPostMergeDeliveryRoutingStatus.READY,
            summary_message=(
                "All tracked requirements are satisfied, so delivery can transition to "
                "STATE_DELIVERY_COMPLETED."
            ),
            next_state=RequirementDiscoverySessionState.DELIVERY_COMPLETED,
            routing_reason=(
                ImplementationPostMergeDeliveryRoutingReason.ALL_REQUIREMENTS_SATISFIED
            ),
            remaining_milestone_issue_count=remaining_milestone_issue_count,
            all_requirements_satisfied=all_requirements_satisfied,
        )

    return ImplementationPostMergeDeliveryRoutingResult(
        status=ImplementationPostMergeDeliveryRoutingStatus.READY,
        summary_message=(
            "The current milestone is complete, so delivery returns to STATE_MILESTONE_PLANNING."
        ),
        next_state=RequirementDiscoverySessionState.MILESTONE_PLANNING,
        routing_reason=ImplementationPostMergeDeliveryRoutingReason.MILESTONE_COMPLETED,
        remaining_milestone_issue_count=remaining_milestone_issue_count,
        all_requirements_satisfied=all_requirements_satisfied,
    )


def build_implementation_blocker_result(
    session_summary: RequirementDiscoverySessionSummary,
    engineer_job_input: EngineerJobInput | None,
    blocker_summary: str | None,
) -> ImplementationBlockerResult:
    """Builds the strict implementation blocker result from an active engineer job.

    Args:
        session_summary: Current requirement discovery session snapshot.
        engineer_job_input: Typed engineer job input for the blocked work item.
        blocker_summary: Human-readable explanation of why implementation cannot proceed.

    Returns:
        A typed result describing whether Engineer can report the blocker immediately.

    Example:
        result = build_implementation_blocker_result(
            session_summary=session_summary,
            engineer_job_input=engineer_job_input,
            blocker_summary="The required retry policy is missing from the shared contracts.",
        )
        if result.status is ImplementationBlockerStatus.READY:
            assert result.implementation_blocker_draft is not None
    """

    if session_summary.current_state is not RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING:
        return ImplementationBlockerResult(
            status=ImplementationBlockerStatus.UNSUPPORTED_STATE,
            summary_message=(
                "Implementation blocker reporting is not supported for workflow state "
                f"{session_summary.current_state.value}."
            ),
            next_state=session_summary.current_state,
        )

    missing_information_items: list[str] = []
    if engineer_job_input is None:
        missing_information_items.append("engineer job input")
    if blocker_summary is None or not blocker_summary.strip():
        missing_information_items.append("implementation blocker summary")

    if missing_information_items:
        return ImplementationBlockerResult(
            status=ImplementationBlockerStatus.INPUT_REQUIRED,
            summary_message=(
                "Engineer needs a strict job input and blocker summary before reporting an "
                "implementation blocker."
            ),
            next_state=RequirementDiscoverySessionState.ENGINEER_JOB_RUNNING,
            missing_information_items=tuple(missing_information_items),
        )

    if engineer_job_input is None or blocker_summary is None:
        raise ValueError("Implementation blocker inputs must be available after validation.")

    normalized_blocker_summary = blocker_summary.strip()
    implementation_blocker_draft = ImplementationBlockerDraft(
        issue_title=engineer_job_input.issue_title,
        blocker_summary=normalized_blocker_summary,
        acceptance_criteria=engineer_job_input.acceptance_criteria,
        single_pull_request_scope=engineer_job_input.single_pull_request_scope,
        related_issue_use_case=engineer_job_input.related_issue_use_case,
        comment_body_draft=_build_implementation_blocker_comment_body_draft(
            engineer_job_input=engineer_job_input,
            blocker_summary=normalized_blocker_summary,
        ),
    )
    return ImplementationBlockerResult(
        status=ImplementationBlockerStatus.READY,
        summary_message=(
            "Prepared the implementation blocker draft and transitioned the workflow to "
            "STATE_IMPLEMENTATION_BLOCKED."
        ),
        next_state=RequirementDiscoverySessionState.IMPLEMENTATION_BLOCKED,
        implementation_blocker_draft=implementation_blocker_draft,
    )


def build_user_decision_escalation_result(
    session_summary: RequirementDiscoverySessionSummary,
    implementation_blocker_result: ImplementationBlockerResult | None,
    escalation_summary: str | None,
    requested_user_input: str | None,
) -> UserDecisionEscalationResult:
    """Builds the strict user decision escalation result from a reported blocker.

    Args:
        session_summary: Current requirement discovery session snapshot.
        implementation_blocker_result: Ready blocker result that Manager reviewed.
        escalation_summary: Manager explanation of why user direction is required.
        requested_user_input: Specific product or scope decision requested from the user.

    Returns:
        A typed result describing whether Manager can escalate to the user immediately.

    Example:
        result = build_user_decision_escalation_result(
            session_summary=session_summary,
            implementation_blocker_result=implementation_blocker_result,
            escalation_summary="Manager cannot choose the product trade-off alone.",
            requested_user_input="Decide whether to add the missing state or reduce scope.",
        )
        if result.status is UserDecisionEscalationStatus.READY:
            assert result.user_decision_escalation_draft is not None
    """

    if session_summary.current_state is not RequirementDiscoverySessionState.IMPLEMENTATION_BLOCKED:
        return UserDecisionEscalationResult(
            status=UserDecisionEscalationStatus.UNSUPPORTED_STATE,
            summary_message=(
                "User decision escalation is not supported for workflow state "
                f"{session_summary.current_state.value}."
            ),
            next_state=session_summary.current_state,
        )

    missing_information_items: list[str] = []
    if (
        implementation_blocker_result is None
        or implementation_blocker_result.status is not ImplementationBlockerStatus.READY
    ):
        missing_information_items.append("ready implementation blocker result")
    if escalation_summary is None or not escalation_summary.strip():
        missing_information_items.append("user escalation summary")
    if requested_user_input is None or not requested_user_input.strip():
        missing_information_items.append("requested user input")

    if missing_information_items:
        return UserDecisionEscalationResult(
            status=UserDecisionEscalationStatus.INPUT_REQUIRED,
            summary_message=(
                "Manager needs the blocker result and a clear escalation request before "
                "asking the user for direction."
            ),
            next_state=RequirementDiscoverySessionState.IMPLEMENTATION_BLOCKED,
            missing_information_items=tuple(missing_information_items),
        )

    if (
        implementation_blocker_result is None
        or escalation_summary is None
        or requested_user_input is None
    ):
        raise ValueError("User escalation inputs must be available after validation.")

    implementation_blocker_draft = implementation_blocker_result.implementation_blocker_draft
    if implementation_blocker_draft is None:
        raise ValueError(
            "implementation_blocker_draft must be available when blocker result is READY."
        )

    normalized_escalation_summary = escalation_summary.strip()
    normalized_requested_user_input = requested_user_input.strip()
    return UserDecisionEscalationResult(
        status=UserDecisionEscalationStatus.READY,
        summary_message=(
            "Prepared the user decision escalation draft and transitioned the workflow to "
            "STATE_USER_DECISION_REQUIRED."
        ),
        next_state=RequirementDiscoverySessionState.USER_DECISION_REQUIRED,
        user_decision_escalation_draft=UserDecisionEscalationDraft(
            issue_title=implementation_blocker_draft.issue_title,
            blocker_summary=implementation_blocker_draft.blocker_summary,
            escalation_summary=normalized_escalation_summary,
            requested_user_input=normalized_requested_user_input,
            comment_body_draft=_build_user_decision_escalation_comment_body_draft(
                implementation_blocker_draft=implementation_blocker_draft,
                escalation_summary=normalized_escalation_summary,
                requested_user_input=normalized_requested_user_input,
            ),
        ),
    )


def _build_implementation_pull_request_branch_name(*, issue_number: int, issue_title: str) -> str:
    """Builds a deterministic branch name for an implementation pull request."""

    normalized_issue_title = re.sub(r"^\[[^\]]+\]\s*", "", issue_title.strip())
    issue_slug = re.sub(r"[^a-z0-9]+", "-", normalized_issue_title.casefold()).strip("-")
    if not issue_slug:
        raise ValueError("issue_title must produce a non-empty branch slug.")
    return f"feature/issue-{issue_number}-{issue_slug}"


def _build_implementation_pull_request_body_summary(
    *,
    related_issue_identifier: str,
    engineer_job_input: EngineerJobInput,
) -> str:
    """Builds the summary text for an implementation pull request body."""

    return "\n".join(
        (
            f"Implement `{related_issue_identifier}`.",
            "",
            "## Summary",
            engineer_job_input.issue_overview,
            "",
            "## Scope",
            engineer_job_input.single_pull_request_scope,
            "",
            "## Acceptance Criteria",
            _format_bullet_lines(engineer_job_input.acceptance_criteria),
        )
    )


def _build_implementation_blocker_comment_body_draft(
    engineer_job_input: EngineerJobInput,
    blocker_summary: str,
) -> str:
    """Builds the issue comment body draft for an implementation blocker report."""

    return "\n".join(
        (
            "## Implementation blocker report",
            f"Issue: {engineer_job_input.issue_title}",
            f"Related use case: {engineer_job_input.related_issue_use_case.value}",
            "",
            "### Blocker summary",
            blocker_summary,
            "",
            "### Blocked acceptance criteria",
            _format_bullet_lines(engineer_job_input.acceptance_criteria),
            "",
            "### Current single pull request scope",
            engineer_job_input.single_pull_request_scope,
            "",
            "### Requested manager action",
            (
                "Review the blocker, confirm the missing prerequisite, and decide whether to "
                "unblock the work or escalate to the user."
            ),
        )
    )


def _build_user_decision_escalation_comment_body_draft(
    implementation_blocker_draft: ImplementationBlockerDraft,
    escalation_summary: str,
    requested_user_input: str,
) -> str:
    """Builds the issue comment body draft for a manager user-decision escalation."""

    return "\n".join(
        (
            "## User decision required",
            f"Issue: {implementation_blocker_draft.issue_title}",
            "",
            "### Escalation summary",
            escalation_summary,
            "",
            "### Existing blocker summary",
            implementation_blocker_draft.blocker_summary,
            "",
            "### Requested user input",
            requested_user_input,
            "",
            "### Current single pull request scope",
            implementation_blocker_draft.single_pull_request_scope,
            "",
            "### Blocked acceptance criteria",
            _format_bullet_lines(implementation_blocker_draft.acceptance_criteria),
        )
    )


def _build_manager_implementation_review_approve_body_draft(
    review_input: ManagerImplementationReviewInput,
) -> str:
    """Builds the draft review body for an approved implementation review."""

    reviewed_check_targets = ", ".join(
        check_target.value for check_target in review_input.review_targets
    )
    return (
        f"Approve implementation review for `{review_input.pull_request_title}`.\n\n"
        "The minimum implementation review checks passed for this review round.\n"
        f"Reviewed check targets: {reviewed_check_targets}."
    )


def _build_manager_implementation_review_requested_changes_body_draft(
    review_input: ManagerImplementationReviewInput,
    requested_changes: tuple[str, ...],
) -> str:
    """Builds the draft review body for a request-changes implementation outcome."""

    requested_change_lines = "\n".join(
        f"- {requested_change}" for requested_change in requested_changes
    )
    return (
        f"Request changes for `{review_input.pull_request_title}`.\n\n"
        "Please resolve the following implementation review issues before approval:\n"
        f"{requested_change_lines}"
    )


def _format_manager_implementation_requested_change(
    review_finding: ManagerImplementationReviewDecisionFinding,
) -> str:
    """Formats one implementation review finding into a requested-change item."""

    return f"Address {review_finding.check_target.value}: {review_finding.summary}"


def _format_bullet_lines(lines: tuple[str, ...]) -> str:
    """Formats string values as Markdown bullet lines."""

    return "\n".join(f"- {line}" for line in lines)


def _normalize_optional_reason(reason: str | None) -> str | None:
    """Normalizes optional user-decision rationale text."""

    if reason is None:
        return None

    normalized_reason = reason.strip()
    if not normalized_reason:
        return None
    return normalized_reason


def _normalize_test_evidence(test_evidence: tuple[str, ...] | None) -> tuple[str, ...] | None:
    """Normalizes and validates implementation pull request test evidence."""

    if test_evidence is None:
        return None
    if not test_evidence:
        return None
    if any(not evidence_item.strip() for evidence_item in test_evidence):
        raise ValueError("test_evidence must not contain empty values.")
    if len(set(test_evidence)) != len(test_evidence):
        raise ValueError("test_evidence must not contain duplicate values.")
    return test_evidence


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


def _build_manager_requirement_review_documents(
    updated_documents: tuple[RequirementDocumentType, ...],
) -> tuple[RequirementDocumentType, ...]:
    """Builds the minimum document scope needed for manager requirement review."""

    ordered_documents = [RequirementDocumentType.REQUIREMENT]
    for updated_document in updated_documents:
        if updated_document not in ordered_documents:
            ordered_documents.append(updated_document)
    return tuple(ordered_documents)


def _build_manager_requirement_review_next_state(
    review_decision: ManagerRequirementReviewDecision,
) -> RequirementDiscoverySessionState:
    """Builds the next requirement workflow state for the review decision."""

    if review_decision is ManagerRequirementReviewDecision.APPROVE:
        return RequirementDiscoverySessionState.REQUIREMENT_APPROVED
    return RequirementDiscoverySessionState.REQUIREMENT_CHANGES_REQUESTED


def _build_manager_implementation_review_next_state(
    review_decision: ManagerImplementationReviewDecision,
) -> RequirementDiscoverySessionState:
    """Builds the next implementation workflow state for the review decision."""

    if review_decision is ManagerImplementationReviewDecision.APPROVE:
        return RequirementDiscoverySessionState.IMPLEMENTATION_PR_APPROVED
    if review_decision is ManagerImplementationReviewDecision.REQUEST_CHANGES:
        return RequirementDiscoverySessionState.ENGINEER_CHANGES_REQUESTED
    return RequirementDiscoverySessionState.USER_DECISION_REQUIRED


def _build_implementation_post_merge_delivery_next_state(
    routing_reason: ImplementationPostMergeDeliveryRoutingReason,
) -> RequirementDiscoverySessionState:
    """Builds the next delivery workflow state for the post-merge routing reason."""

    if (
        routing_reason
        is ImplementationPostMergeDeliveryRoutingReason.MORE_ISSUES_NEEDED_FOR_MILESTONE
    ):
        return RequirementDiscoverySessionState.IMPLEMENTATION_BACKLOG_READY
    if routing_reason is ImplementationPostMergeDeliveryRoutingReason.MILESTONE_COMPLETED:
        return RequirementDiscoverySessionState.MILESTONE_PLANNING
    return RequirementDiscoverySessionState.DELIVERY_COMPLETED


def _collect_unsupported_implementation_review_check_targets(
    review_input: ManagerImplementationReviewInput,
    review_findings: tuple[ManagerImplementationReviewDecisionFinding, ...],
) -> tuple[ManagerImplementationReviewCheckTarget, ...]:
    """Collects implementation review targets that are outside the declared scope."""

    supported_check_targets = set(review_input.review_targets)
    unsupported_check_targets: list[ManagerImplementationReviewCheckTarget] = []
    for review_finding in review_findings:
        if (
            review_finding.check_target not in supported_check_targets
            and review_finding.check_target not in unsupported_check_targets
        ):
            unsupported_check_targets.append(review_finding.check_target)
    return tuple(unsupported_check_targets)


def _is_requirement_review_approved(
    requirement_review_execution_result: ManagerRequirementReviewExecutionResult | None,
) -> bool:
    """Returns whether the manager review execution result represents an approval."""

    if requirement_review_execution_result is None:
        return False
    if (
        requirement_review_execution_result.status
        is not ManagerRequirementReviewExecutionStatus.READY
    ):
        return False
    if (
        requirement_review_execution_result.next_state
        is not RequirementDiscoverySessionState.REQUIREMENT_APPROVED
    ):
        return False

    review_execution_payload = requirement_review_execution_result.review_execution_payload
    if review_execution_payload is None:
        return False
    return review_execution_payload.review_decision is ManagerRequirementReviewDecision.APPROVE


def _build_milestone_target_use_cases(
    normalized_requirement_documents_summary: str,
) -> tuple[UseCaseIdentifier, ...]:
    """Builds the ordered target use cases for the first delivery milestone."""

    ordered_target_use_cases: list[UseCaseIdentifier] = []
    for use_case_identifier, keywords in _MILESTONE_USE_CASE_RULES:
        if any(keyword in normalized_requirement_documents_summary for keyword in keywords):
            ordered_target_use_cases.append(use_case_identifier)
    return tuple(ordered_target_use_cases)


def _build_milestone_goal(target_use_cases: tuple[UseCaseIdentifier, ...]) -> str:
    """Builds the first milestone goal from the selected use cases."""

    if target_use_cases == (
        UseCaseIdentifier.ORCHESTRATE_DELIVERY_WITH_MANAGER,
        UseCaseIdentifier.IMPLEMENT_ISSUE_WITH_ENGINEER,
    ):
        return (
            "Establish the first post-requirement delivery slice from milestone planning "
            "through engineer execution."
        )
    if target_use_cases == (UseCaseIdentifier.ORCHESTRATE_DELIVERY_WITH_MANAGER,):
        return "Turn approved requirements into the first milestone and implementation backlog."
    return "Validate the first engineer execution loop from an approved implementation issue."


def _build_milestone_completion_criteria(
    target_use_cases: tuple[UseCaseIdentifier, ...],
) -> tuple[str, ...]:
    """Builds completion criteria for the first delivery milestone."""

    completion_criteria: list[str] = []
    if UseCaseIdentifier.ORCHESTRATE_DELIVERY_WITH_MANAGER in target_use_cases:
        completion_criteria.extend(
            (
                "Manager can define the first milestone from the approved requirements.",
                "Manager can create prioritized implementation issues for the milestone backlog.",
            )
        )
    if UseCaseIdentifier.IMPLEMENT_ISSUE_WITH_ENGINEER in target_use_cases:
        completion_criteria.append(
            "Engineer can complete the first prioritized implementation issue and open an "
            "implementation pull request."
        )
    return tuple(completion_criteria)


def _build_milestone_implementation_focuses(
    target_use_cases: tuple[UseCaseIdentifier, ...],
) -> tuple[MilestoneImplementationFocus, ...]:
    """Builds ordered implementation focuses for the first delivery milestone."""

    implementation_focuses: list[MilestoneImplementationFocus] = []
    if UseCaseIdentifier.ORCHESTRATE_DELIVERY_WITH_MANAGER in target_use_cases:
        implementation_focuses.append(
            MilestoneImplementationFocus(
                use_case_identifier=UseCaseIdentifier.ORCHESTRATE_DELIVERY_WITH_MANAGER,
                focus_summary=(
                    "Implement manager milestone planning and implementation issue creation "
                    "from approved requirements."
                ),
                rationale=(
                    "UC_ORCHESTRATE_DELIVERY_WITH_MANAGER is the first delivery step after "
                    "requirement approval."
                ),
            )
        )
    if UseCaseIdentifier.IMPLEMENT_ISSUE_WITH_ENGINEER in target_use_cases:
        implementation_focuses.append(
            MilestoneImplementationFocus(
                use_case_identifier=UseCaseIdentifier.IMPLEMENT_ISSUE_WITH_ENGINEER,
                focus_summary=(
                    "Implement the first engineer issue execution loop and implementation "
                    "pull request handoff."
                ),
                rationale=(
                    "UC_IMPLEMENT_ISSUE_WITH_ENGINEER proves that the planned backlog can "
                    "be executed end to end."
                ),
            )
        )
    return tuple(implementation_focuses)


def _build_implementation_issue_drafts(
    milestone_planning_model: MilestonePlanningModel,
) -> tuple[ImplementationIssueDraft, ...]:
    """Builds engineer-ready implementation issue drafts from milestone focuses."""

    implementation_issue_drafts: list[ImplementationIssueDraft] = []
    for implementation_focus in milestone_planning_model.implementation_focuses:
        draft_rule = _IMPLEMENTATION_ISSUE_DRAFT_RULES.get(implementation_focus.use_case_identifier)
        if draft_rule is None:
            continue
        implementation_issue_drafts.append(
            ImplementationIssueDraft(
                target_use_case=implementation_focus.use_case_identifier,
                issue_title=draft_rule.issue_title,
                issue_summary=(
                    f"{draft_rule.issue_summary_prefix} "
                    f"Milestone focus: {implementation_focus.focus_summary} "
                    f"Prioritization rationale: {implementation_focus.rationale}"
                ),
                acceptance_criteria=draft_rule.acceptance_criteria,
                single_pull_request_scope=draft_rule.single_pull_request_scope,
            )
        )
    return tuple(implementation_issue_drafts)


def _validate_manager_requirement_review_findings(
    review_input: ManagerRequirementReviewInput,
    review_findings: tuple[ManagerRequirementReviewDecisionFinding, ...],
) -> None:
    """Validates that review findings fit the declared review scope."""

    supported_focus_areas = set(review_input.review_focus_areas)
    review_documents = set(review_input.documents_to_review)
    for review_finding in review_findings:
        if review_finding.focus_area not in supported_focus_areas:
            raise ValueError(
                "review_findings must use focus areas listed in review_input.review_focus_areas."
            )
        if not set(review_finding.related_documents).issubset(review_documents):
            raise ValueError(
                "review_findings must reference only documents listed in "
                "review_input.documents_to_review."
            )


def _build_manager_requirement_review_approve_body_draft(
    review_input: ManagerRequirementReviewInput,
) -> str:
    """Builds the draft review body for an approval outcome."""

    reviewed_documents = ", ".join(
        document_type.value for document_type in review_input.documents_to_review
    )
    return (
        f"Approve requirement review for `{review_input.pull_request_title}`.\n\n"
        "The minimum document consistency checks passed for this review round.\n"
        f"Reviewed documents: {reviewed_documents}."
    )


def _build_manager_requirement_review_requested_changes_body_draft(
    review_input: ManagerRequirementReviewInput,
    requested_changes: tuple[str, ...],
) -> str:
    """Builds the draft review body for a request-changes outcome."""

    requested_change_lines = "\n".join(
        f"- {requested_change}" for requested_change in requested_changes
    )
    return (
        f"Request changes for `{review_input.pull_request_title}`.\n\n"
        "Please resolve the following document consistency issues before approval:\n"
        f"{requested_change_lines}"
    )


def _format_manager_requirement_requested_change(
    review_finding: ManagerRequirementReviewDecisionFinding,
) -> str:
    """Formats one review finding into a requested-change item."""

    return f"Address {review_finding.focus_area.value}: {review_finding.summary}"


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
