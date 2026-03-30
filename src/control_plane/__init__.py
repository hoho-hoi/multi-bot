"""Control-plane public entrypoints."""

from control_plane.entrypoint import (
    ControlPlaneStartupReport,
    build_control_plane_startup_report,
)

__all__ = ["ControlPlaneStartupReport", "build_control_plane_startup_report"]
