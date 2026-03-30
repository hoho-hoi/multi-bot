from shared_contracts import (
    EngineerExecutionWorkItemContract,
    EngineerJobInput,
    RepositoryReference,
    UseCaseIdentifier,
    WorkerRoleName,
)
from shared_contracts.issue_contract import IssueWorkItemContract


def create_backlog_ready_issue_work_item_contract() -> IssueWorkItemContract:
    """Creates an implementation issue contract for engineer execution tests."""

    return IssueWorkItemContract(
        repository_reference=RepositoryReference(
            owner_name="example-owner",
            repository_name="multi-bot",
        ),
        issue_number=38,
        issue_title="Build engineer execution work item and running-state transition",
    )


def create_engineer_job_input() -> EngineerJobInput:
    """Creates strict engineer job input for engineer execution tests."""

    return EngineerJobInput(
        issue_title="Build engineer execution work item and running-state transition",
        issue_overview="Prepare the control-plane transition into engineer execution.",
        acceptance_criteria=(
            "Return a strict engineer execution work item.",
            "Transition the workflow to STATE_ENGINEER_JOB_RUNNING when ready.",
        ),
        single_pull_request_scope="Limit the work to engineer execution start orchestration.",
        related_issue_use_case=UseCaseIdentifier.IMPLEMENT_ISSUE_WITH_ENGINEER,
    )


def test_engineer_execution_work_item_contract_preserves_issue_metadata_and_execution_focus() -> (
    None
):
    issue_work_item_contract = create_backlog_ready_issue_work_item_contract()
    engineer_job_input = create_engineer_job_input()

    work_item_contract = EngineerExecutionWorkItemContract.create_from_issue_and_job_input(
        issue_work_item_contract=issue_work_item_contract,
        engineer_job_input=engineer_job_input,
    )

    assert work_item_contract.issue_work_item_contract.to_issue_identifier() == (
        "example-owner/multi-bot#38"
    )
    assert work_item_contract.engineer_job_input == engineer_job_input
    assert work_item_contract.execution_focus.focus_summary == engineer_job_input.issue_overview
    assert work_item_contract.execution_focus.acceptance_criteria == (
        engineer_job_input.acceptance_criteria
    )
    assert work_item_contract.role_name is WorkerRoleName.ENGINEER
