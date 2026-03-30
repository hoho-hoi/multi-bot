from control_plane import ControlPlaneStartupReport, build_control_plane_startup_report
from shared_contracts import IssueWorkItemContract, RepositoryReference
from worker_runtime import WorkerRuntimeStartupReport, build_worker_runtime_startup_report


def create_issue_work_item_contract() -> IssueWorkItemContract:
    """Creates a minimal issue work item contract for bootstrap tests."""

    return IssueWorkItemContract(
        repository_reference=RepositoryReference(
            owner_name="example-owner",
            repository_name="multi-bot",
        ),
        issue_number=2,
        issue_title="Bootstrap the Python monorepo",
    )


def test_shared_contract_returns_repository_qualified_issue_identifier() -> None:
    issue_work_item_contract = create_issue_work_item_contract()

    assert issue_work_item_contract.to_issue_identifier() == "example-owner/multi-bot#2"


def test_control_plane_entrypoint_returns_startup_report() -> None:
    issue_work_item_contract = create_issue_work_item_contract()

    control_plane_startup_report = build_control_plane_startup_report(issue_work_item_contract)

    assert isinstance(control_plane_startup_report, ControlPlaneStartupReport)
    assert control_plane_startup_report.issue_identifier == "example-owner/multi-bot#2"
    assert "Bootstrap the Python monorepo" in control_plane_startup_report.next_action_summary


def test_worker_runtime_entrypoint_returns_startup_report() -> None:
    issue_work_item_contract = create_issue_work_item_contract()

    worker_runtime_startup_report = build_worker_runtime_startup_report(issue_work_item_contract)

    assert isinstance(worker_runtime_startup_report, WorkerRuntimeStartupReport)
    assert worker_runtime_startup_report.issue_identifier == "example-owner/multi-bot#2"
    assert "Bootstrap the Python monorepo" in worker_runtime_startup_report.next_action_summary
