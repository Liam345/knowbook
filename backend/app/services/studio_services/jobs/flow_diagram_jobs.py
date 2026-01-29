"""
Flow Diagram Job Management - Tracks flow diagram generation jobs.

Educational Note: Flow diagram jobs use Claude to generate Mermaid.js syntax
for visual process and relationship mapping. Unlike mind maps which use a custom
node structure, flow diagrams use Mermaid.js which handles its own rendering.

Mermaid supports many diagram types:
- Flowcharts (graph TD/LR)
- Sequence diagrams
- State diagrams
- ER diagrams
- Class diagrams
- Pie charts
- Gantt charts
- User journeys
"""
from datetime import datetime
from typing import Dict, List, Any, Optional

from app.services.studio_services.studio_index_service import load_index, save_index


def create_flow_diagram_job(
    project_id: str,
    job_id: str,
    source_id: str,
    source_name: str,
    direction: str
) -> Dict[str, Any]:
    """
    Create a new flow diagram generation job.

    Args:
        project_id: The project UUID
        job_id: Unique job identifier
        source_id: Source being processed
        source_name: Name of the source
        direction: User's direction for what to focus on

    Returns:
        The created job record
    """
    job = {
        "id": job_id,
        "source_id": source_id,
        "source_name": source_name,
        "direction": direction,
        "status": "pending",
        "progress": "Initializing...",
        "error": None,
        # Flow diagram content
        "mermaid_syntax": None,
        "diagram_type": None,
        "title": None,
        "description": None,
        # Metadata
        "generation_time_seconds": None,
        "created_at": datetime.now().isoformat(),
        "started_at": None,
        "completed_at": None
    }

    index = load_index(project_id)
    index["flow_diagram_jobs"].append(job)
    save_index(project_id, index)

    return job


def update_flow_diagram_job(
    project_id: str,
    job_id: str,
    **updates
) -> Optional[Dict[str, Any]]:
    """
    Update a flow diagram job's fields.

    Args:
        project_id: The project UUID
        job_id: The job ID to update
        **updates: Fields to update

    Returns:
        Updated job record or None if not found
    """
    index = load_index(project_id)

    for i, job in enumerate(index["flow_diagram_jobs"]):
        if job["id"] == job_id:
            for key, value in updates.items():
                if value is not None:
                    job[key] = value
            job["updated_at"] = datetime.now().isoformat()
            index["flow_diagram_jobs"][i] = job
            save_index(project_id, index)
            return job

    return None


def get_flow_diagram_job(project_id: str, job_id: str) -> Optional[Dict[str, Any]]:
    """Get a flow diagram job by ID."""
    index = load_index(project_id)
    jobs = index.get("flow_diagram_jobs", [])

    for job in jobs:
        if job["id"] == job_id:
            return job

    return None


def list_flow_diagram_jobs(project_id: str, source_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List flow diagram jobs, optionally filtered by source.

    Args:
        project_id: The project UUID
        source_id: Optional source ID to filter by

    Returns:
        List of flow diagram jobs (newest first)
    """
    index = load_index(project_id)
    jobs = index.get("flow_diagram_jobs", [])

    if source_id:
        jobs = [j for j in jobs if j.get("source_id") == source_id]

    # Sort by created_at descending
    return sorted(jobs, key=lambda j: j.get("created_at", ""), reverse=True)


def delete_flow_diagram_job(project_id: str, job_id: str) -> bool:
    """
    Delete a flow diagram job from the index.

    Returns:
        True if job was found and deleted
    """
    index = load_index(project_id)
    original_count = len(index["flow_diagram_jobs"])

    index["flow_diagram_jobs"] = [j for j in index["flow_diagram_jobs"] if j["id"] != job_id]

    if len(index["flow_diagram_jobs"]) < original_count:
        save_index(project_id, index)
        return True

    return False
