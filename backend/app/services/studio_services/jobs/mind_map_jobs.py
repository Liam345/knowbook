"""
Mind Map Job Management - Tracks mind map generation jobs.

Educational Note: Mind map jobs use Claude to generate hierarchical node structures
for visual concept mapping. The nodes form a tree structure with a single root node
and branches representing subtopics and details.

Node Structure Pattern:
- Each node has: id, label, parent_id, node_type, description
- Root node is the main topic (parent_id: null)
- Category nodes group related subtopics
- Leaf nodes contain specific details/facts
"""
from datetime import datetime
from typing import Dict, List, Any, Optional

from app.services.studio_services.studio_index_service import load_index, save_index


def create_mind_map_job(
    project_id: str,
    job_id: str,
    source_id: str,
    source_name: str,
    direction: str
) -> Dict[str, Any]:
    """
    Create a new mind map generation job.

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
        # Mind map content
        "nodes": [],
        "topic_summary": None,
        "node_count": 0,
        # Metadata
        "generation_time_seconds": None,
        "created_at": datetime.now().isoformat(),
        "started_at": None,
        "completed_at": None
    }

    index = load_index(project_id)
    index["mind_map_jobs"].append(job)
    save_index(project_id, index)

    return job


def update_mind_map_job(
    project_id: str,
    job_id: str,
    **updates
) -> Optional[Dict[str, Any]]:
    """
    Update a mind map job's fields.

    Args:
        project_id: The project UUID
        job_id: The job ID to update
        **updates: Fields to update

    Returns:
        Updated job record or None if not found
    """
    index = load_index(project_id)

    for i, job in enumerate(index["mind_map_jobs"]):
        if job["id"] == job_id:
            for key, value in updates.items():
                if value is not None:
                    job[key] = value
            job["updated_at"] = datetime.now().isoformat()
            index["mind_map_jobs"][i] = job
            save_index(project_id, index)
            return job

    return None


def get_mind_map_job(project_id: str, job_id: str) -> Optional[Dict[str, Any]]:
    """Get a mind map job by ID."""
    index = load_index(project_id)
    jobs = index.get("mind_map_jobs", [])

    for job in jobs:
        if job["id"] == job_id:
            return job

    return None


def list_mind_map_jobs(project_id: str, source_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List mind map jobs, optionally filtered by source.

    Args:
        project_id: The project UUID
        source_id: Optional source ID to filter by

    Returns:
        List of mind map jobs (newest first)
    """
    index = load_index(project_id)
    jobs = index.get("mind_map_jobs", [])

    if source_id:
        jobs = [j for j in jobs if j.get("source_id") == source_id]

    # Sort by created_at descending
    return sorted(jobs, key=lambda j: j.get("created_at", ""), reverse=True)


def delete_mind_map_job(project_id: str, job_id: str) -> bool:
    """
    Delete a mind map job from the index.

    Returns:
        True if job was found and deleted
    """
    index = load_index(project_id)
    original_count = len(index["mind_map_jobs"])

    index["mind_map_jobs"] = [j for j in index["mind_map_jobs"] if j["id"] != job_id]

    if len(index["mind_map_jobs"]) < original_count:
        save_index(project_id, index)
        return True

    return False
