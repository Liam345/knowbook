"""
Studio Index Service - Core index management for studio generation jobs.

Educational Note: This service manages a studio_index.json file that tracks
all studio content generation jobs. Similar to sources_index.json but for
generated content.

Job Status Flow:
    pending -> processing -> ready
                          -> error

The frontend polls the status endpoint to know when content is ready.

Architecture:
    This file contains ONLY the core index management functions (load/save).
    Individual job type management (create, update, get, list, delete) is
    organized into separate modules in the jobs/ subfolder:

    jobs/
    ├── blog_jobs.py
    ├── prd_jobs.py
    ├── marketing_strategy_jobs.py
    ├── business_report_jobs.py
    ├── mind_map_jobs.py
    ├── flow_diagram_jobs.py
    ├── infographic_jobs.py
    └── wireframe_jobs.py
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from app.utils.path_utils import get_studio_dir


# =============================================================================
# Core Index Management Functions
# =============================================================================

def _get_index_path(project_id: str) -> Path:
    """Get the studio index file path for a project."""
    return get_studio_dir(project_id) / "studio_index.json"


def load_index(project_id: str) -> Dict[str, Any]:
    """
    Load the studio index for a project.

    Returns empty structure if index doesn't exist.
    Handles migration for existing indexes missing new job types.
    """
    index_path = _get_index_path(project_id)

    default_index = {
        "blog_jobs": [],
        "prd_jobs": [],
        "marketing_strategy_jobs": [],
        "business_report_jobs": [],
        "mind_map_jobs": [],
        "flow_diagram_jobs": [],
        "infographic_jobs": [],
        "wireframe_jobs": [],
        "last_updated": datetime.now().isoformat()
    }

    if not index_path.exists():
        return default_index

    try:
        with open(index_path, 'r') as f:
            data = json.load(f)

            # Ensure all job arrays exist (migration for existing indexes)
            needs_save = False
            job_types = [
                "blog_jobs", "prd_jobs", "marketing_strategy_jobs",
                "business_report_jobs", "mind_map_jobs", "flow_diagram_jobs",
                "infographic_jobs", "wireframe_jobs"
            ]

            for job_type in job_types:
                if job_type not in data:
                    data[job_type] = []
                    needs_save = True

            # Persist the migration if we added missing keys
            if needs_save:
                save_index(project_id, data)

            return data
    except (json.JSONDecodeError, FileNotFoundError):
        return default_index


def save_index(project_id: str, index_data: Dict[str, Any]) -> None:
    """Save the studio index for a project."""
    index_path = _get_index_path(project_id)
    index_path.parent.mkdir(parents=True, exist_ok=True)

    index_data["last_updated"] = datetime.now().isoformat()
    with open(index_path, 'w') as f:
        json.dump(index_data, f, indent=2)


# =============================================================================
# Re-exports for Backward Compatibility
# =============================================================================
# All job-specific functions are now in separate modules under jobs/
# These re-exports ensure existing imports continue to work.

from app.services.studio_services.jobs.blog_jobs import (
    create_blog_job,
    update_blog_job,
    get_blog_job,
    list_blog_jobs,
    delete_blog_job,
)

from app.services.studio_services.jobs.prd_jobs import (
    create_prd_job,
    update_prd_job,
    get_prd_job,
    list_prd_jobs,
    delete_prd_job,
)

from app.services.studio_services.jobs.marketing_strategy_jobs import (
    create_marketing_strategy_job,
    update_marketing_strategy_job,
    get_marketing_strategy_job,
    list_marketing_strategy_jobs,
    delete_marketing_strategy_job,
)

from app.services.studio_services.jobs.business_report_jobs import (
    create_business_report_job,
    update_business_report_job,
    get_business_report_job,
    list_business_report_jobs,
    delete_business_report_job,
)

from app.services.studio_services.jobs.mind_map_jobs import (
    create_mind_map_job,
    update_mind_map_job,
    get_mind_map_job,
    list_mind_map_jobs,
    delete_mind_map_job,
)

from app.services.studio_services.jobs.flow_diagram_jobs import (
    create_flow_diagram_job,
    update_flow_diagram_job,
    get_flow_diagram_job,
    list_flow_diagram_jobs,
    delete_flow_diagram_job,
)

from app.services.studio_services.jobs.infographic_jobs import (
    create_infographic_job,
    update_infographic_job,
    get_infographic_job,
    list_infographic_jobs,
    delete_infographic_job,
)

from app.services.studio_services.jobs.wireframe_jobs import (
    create_wireframe_job,
    update_wireframe_job,
    get_wireframe_job,
    list_wireframe_jobs,
    delete_wireframe_job,
)
