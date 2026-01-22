"""
Source Service - Business logic for managing project sources.

Educational Note: This service provides the main interface for source operations.
It handles file uploads, processing coordination, and metadata management.
"""
import os
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
from werkzeug.datastructures import FileStorage

from app.utils.file_utils import (
    ALLOWED_EXTENSIONS,
    get_file_category,
    get_file_size,
    is_allowed_file_type
)


class SourceService:
    """
    Service class for managing project sources.

    Educational Note: This handles the complete source lifecycle:
    - File upload and storage
    - Metadata management in sources_index.json
    - Processing status tracking
    - File cleanup operations
    """

    def __init__(self):
        """Initialize the source service."""
        self.data_dir = Path(__file__).parent.parent.parent / 'data'

    def list_sources(self, project_id: str) -> List[Dict[str, Any]]:
        """
        List all sources for a project.

        Args:
            project_id: The project UUID

        Returns:
            List of source metadata dictionaries (newest first)
        """
        try:
            sources_index = self._load_sources_index(project_id)
            # Return sorted by created_at descending (newest first)
            return sorted(sources_index, key=lambda x: x.get('created_at', ''), reverse=True)
        except Exception:
            # Return empty list if index doesn't exist yet
            return []

    def get_source(self, project_id: str, source_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific source's metadata.

        Args:
            project_id: The project UUID
            source_id: The source UUID

        Returns:
            Source metadata dictionary or None if not found
        """
        sources = self.list_sources(project_id)
        return next((s for s in sources if s['id'] == source_id), None)

    def upload_source(self, project_id: str, file: FileStorage, name: Optional[str] = None, 
                     description: str = '') -> Dict[str, Any]:
        """
        Upload a new source file to a project.

        Args:
            project_id: The project UUID
            file: The uploaded file
            name: Display name (optional, defaults to filename)
            description: Description (optional)

        Returns:
            Source metadata dictionary

        Raises:
            ValueError: If file type is not allowed or other validation fails
        """
        if not file or not file.filename:
            raise ValueError("No file provided")

        # Validate file type
        if not is_allowed_file_type(file.filename):
            raise ValueError(f"File type not allowed. Allowed types: {list(ALLOWED_EXTENSIONS.keys())}")

        # Generate unique source ID
        source_id = str(uuid.uuid4())
        
        # Use provided name or default to filename (without extension)
        if name:
            display_name = name.strip()
        else:
            display_name = Path(file.filename).stem

        # Ensure project directories exist
        self._ensure_project_directories(project_id)

        # Save file to raw directory
        raw_dir = self._get_raw_dir(project_id)
        file_extension = Path(file.filename).suffix.lower()
        file_path = raw_dir / f"{source_id}{file_extension}"
        
        file.save(str(file_path))

        # Create source metadata
        source_metadata = {
            'id': source_id,
            'name': display_name,
            'description': description,
            'original_name': file.filename,
            'file_path': str(file_path.relative_to(self.data_dir)),
            'file_size': get_file_size(file_path),
            'file_type': file_extension,
            'category': get_file_category(file.filename),
            'status': 'uploaded',
            'active': True,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'processing_info': {},
            'embedding_info': {},
            'summary_info': {}
        }

        # Add to sources index
        self._add_to_sources_index(project_id, source_metadata)

        # Trigger background processing
        from app.services.source_processing_service import source_processing_service
        source_processing_service.start_processing(project_id, source_id)
        
        return source_metadata

    def update_source(self, project_id: str, source_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a source's metadata.

        Args:
            project_id: The project UUID
            source_id: The source UUID
            updates: Dictionary of fields to update

        Returns:
            Updated source metadata or None if not found
        """
        sources_index = self._load_sources_index(project_id)
        
        for i, source in enumerate(sources_index):
            if source['id'] == source_id:
                # Update allowed fields
                allowed_fields = ['name', 'description', 'active']
                for field in allowed_fields:
                    if field in updates:
                        source[field] = updates[field]
                
                source['updated_at'] = datetime.utcnow().isoformat()
                sources_index[i] = source
                
                # Save updated index
                self._save_sources_index(project_id, sources_index)
                return source
        
        return None

    def delete_source(self, project_id: str, source_id: str) -> bool:
        """
        Delete a source and all its associated files.

        Args:
            project_id: The project UUID
            source_id: The source UUID

        Returns:
            True if deleted, False if not found
        """
        sources_index = self._load_sources_index(project_id)
        source_to_delete = None
        
        # Find and remove from index
        for i, source in enumerate(sources_index):
            if source['id'] == source_id:
                source_to_delete = sources_index.pop(i)
                break
        
        if not source_to_delete:
            return False
        
        # Delete associated files
        try:
            # Delete raw file
            if 'file_path' in source_to_delete:
                file_path = self.data_dir / source_to_delete['file_path']
                if file_path.exists():
                    file_path.unlink()
            
            # Delete processed file (if exists)
            processed_dir = self._get_processed_dir(project_id)
            processed_file = processed_dir / f"{source_id}.txt"
            if processed_file.exists():
                processed_file.unlink()
            
            # Delete chunks directory (if exists)
            chunks_dir = self._get_chunks_dir(project_id) / source_id
            if chunks_dir.exists():
                import shutil
                shutil.rmtree(chunks_dir)
            
            # TODO: Delete embeddings from vector database
            
        except Exception as e:
            # Log but don't fail the deletion
            print(f"Warning: Error deleting files for source {source_id}: {e}")
        
        # Save updated index
        self._save_sources_index(project_id, sources_index)
        return True

    def get_source_file_path(self, project_id: str, source_id: str) -> Optional[Path]:
        """
        Get the file path for a source.

        Args:
            project_id: The project UUID
            source_id: The source UUID

        Returns:
            Path to the source file or None if not found
        """
        source = self.get_source(project_id, source_id)
        if not source or 'file_path' not in source:
            return None
        
        return self.data_dir / source['file_path']

    def get_sources_summary(self, project_id: str) -> Dict[str, Any]:
        """
        Get aggregate statistics for all sources in a project.

        Args:
            project_id: The project UUID

        Returns:
            Summary statistics dictionary
        """
        sources = self.list_sources(project_id)
        
        summary = {
            'total_count': len(sources),
            'by_category': {},
            'by_status': {},
            'total_size': 0
        }
        
        for source in sources:
            # Count by category
            category = source.get('category', 'unknown')
            summary['by_category'][category] = summary['by_category'].get(category, 0) + 1
            
            # Count by status
            status = source.get('status', 'unknown')
            summary['by_status'][status] = summary['by_status'].get(status, 0) + 1
            
            # Sum file sizes
            file_size = source.get('file_size', 0)
            if isinstance(file_size, (int, float)):
                summary['total_size'] += file_size
        
        return summary

    def get_allowed_types(self) -> Dict[str, List[str]]:
        """
        Get list of allowed file extensions grouped by category.

        Returns:
            Dictionary mapping categories to lists of extensions
        """
        return ALLOWED_EXTENSIONS

    # Private helper methods

    def _ensure_project_directories(self, project_id: str):
        """Ensure all necessary directories exist for a project."""
        project_dir = self.data_dir / 'projects' / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Create sources subdirectories
        sources_dir = project_dir / 'sources'
        sources_dir.mkdir(exist_ok=True)
        
        (sources_dir / 'raw').mkdir(exist_ok=True)
        (sources_dir / 'processed').mkdir(exist_ok=True)
        (sources_dir / 'chunks').mkdir(exist_ok=True)

    def _get_raw_dir(self, project_id: str) -> Path:
        """Get the raw files directory for a project."""
        return self.data_dir / 'projects' / project_id / 'sources' / 'raw'

    def _get_processed_dir(self, project_id: str) -> Path:
        """Get the processed files directory for a project."""
        return self.data_dir / 'projects' / project_id / 'sources' / 'processed'

    def _get_chunks_dir(self, project_id: str) -> Path:
        """Get the chunks directory for a project."""
        return self.data_dir / 'projects' / project_id / 'sources' / 'chunks'

    def _get_sources_index_path(self, project_id: str) -> Path:
        """Get the path to the sources index file."""
        return self.data_dir / 'projects' / project_id / 'sources' / 'sources_index.json'

    def _load_sources_index(self, project_id: str) -> List[Dict[str, Any]]:
        """Load the sources index for a project."""
        index_path = self._get_sources_index_path(project_id)
        if not index_path.exists():
            return []
        
        try:
            with open(index_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def _save_sources_index(self, project_id: str, sources_index: List[Dict[str, Any]]):
        """Save the sources index for a project."""
        self._ensure_project_directories(project_id)
        index_path = self._get_sources_index_path(project_id)
        
        with open(index_path, 'w') as f:
            json.dump(sources_index, f, indent=2)

    def _add_to_sources_index(self, project_id: str, source_metadata: Dict[str, Any]):
        """Add a source to the sources index."""
        sources_index = self._load_sources_index(project_id)
        sources_index.append(source_metadata)
        self._save_sources_index(project_id, sources_index)


# Singleton instance
source_service = SourceService()