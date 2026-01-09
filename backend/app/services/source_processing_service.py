"""
Source Processing Service - Handles background processing of uploaded sources.

Educational Note: This service manages the status flow of sources through
the processing pipeline:
uploaded -> processing -> embedding -> ready

For Module 3 (Basic), this is a simplified implementation that simulates
processing without actual AI integration. Future modules will add:
- Text extraction from PDFs, DOCX, PPTX
- Image analysis with Claude vision
- Audio transcription
- Content chunking and embedding
"""
import json
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class SourceProcessingService:
    """
    Service for processing source files in the background.
    
    Educational Note: This uses Python threading for background processing.
    In production, you might use Celery, RQ, or another task queue system.
    For this module, we keep it simple with threading.
    """

    def __init__(self):
        """Initialize the processing service."""
        self.data_dir = Path(__file__).parent.parent.parent / 'data'
        self._processing_threads = {}

    def start_processing(self, project_id: str, source_id: str):
        """
        Start background processing for a source.

        Args:
            project_id: The project UUID
            source_id: The source UUID
        """
        # Check if already processing
        thread_key = f"{project_id}_{source_id}"
        if thread_key in self._processing_threads:
            existing_thread = self._processing_threads[thread_key]
            if existing_thread.is_alive():
                return  # Already processing

        # Start new processing thread
        thread = threading.Thread(
            target=self._process_source,
            args=(project_id, source_id),
            daemon=True
        )
        thread.start()
        self._processing_threads[thread_key] = thread

    def cancel_processing(self, project_id: str, source_id: str) -> bool:
        """
        Cancel processing for a source.

        Args:
            project_id: The project UUID
            source_id: The source UUID

        Returns:
            True if cancelled, False if not processing
        """
        # Update status to cancelled
        return self._update_source_status(project_id, source_id, 'uploaded')

    def retry_processing(self, project_id: str, source_id: str):
        """
        Retry processing for a failed source.

        Args:
            project_id: The project UUID
            source_id: The source UUID
        """
        # Reset status and start processing
        self._update_source_status(project_id, source_id, 'uploaded')
        self.start_processing(project_id, source_id)

    def get_processing_status(self, project_id: str, source_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current processing status for a source.

        Args:
            project_id: The project UUID
            source_id: The source UUID

        Returns:
            Processing status info or None if not found
        """
        source = self._load_source_from_index(project_id, source_id)
        if not source:
            return None

        return {
            'status': source.get('status', 'unknown'),
            'processing_info': source.get('processing_info', {}),
            'embedding_info': source.get('embedding_info', {}),
            'error_info': source.get('error_info', {})
        }

    def _process_source(self, project_id: str, source_id: str):
        """
        Background processing method for a single source.

        Args:
            project_id: The project UUID
            source_id: The source UUID
        """
        try:
            # Load source metadata
            source = self._load_source_from_index(project_id, source_id)
            if not source:
                return

            # Update status to processing
            self._update_source_status(project_id, source_id, 'processing', {
                'started_at': datetime.utcnow().isoformat(),
                'stage': 'content_extraction'
            })

            # Simulate content extraction (2-3 seconds)
            time.sleep(2.5)

            # Check if cancelled
            current_source = self._load_source_from_index(project_id, source_id)
            if not current_source or current_source.get('status') != 'processing':
                return

            # Create processed content file (simplified for Module 3)
            self._create_processed_content(project_id, source_id, source)

            # Update status to embedding
            self._update_source_status(project_id, source_id, 'embedding', {
                'started_at': datetime.utcnow().isoformat(),
                'stage': 'vector_embedding'
            })

            # Simulate embedding generation (1-2 seconds)
            time.sleep(1.5)

            # Check if cancelled
            current_source = self._load_source_from_index(project_id, source_id)
            if not current_source or current_source.get('status') != 'embedding':
                return

            # Create embedding info (simulated for Module 3)
            embedding_info = {
                'created_at': datetime.utcnow().isoformat(),
                'chunk_count': 5,  # Simulated
                'token_count': 1200,  # Simulated
                'embedding_model': 'text-embedding-3-small'  # Future integration
            }

            # Update status to ready
            self._update_source_status(project_id, source_id, 'ready', {
                'completed_at': datetime.utcnow().isoformat(),
                'total_processing_time': '4.0s'
            }, embedding_info)

        except Exception as e:
            # Update status to failed
            self._update_source_status(project_id, source_id, 'failed', {
                'failed_at': datetime.utcnow().isoformat(),
                'error_message': str(e),
                'stage': 'processing'
            })

    def _create_processed_content(self, project_id: str, source_id: str, source: Dict[str, Any]):
        """
        Create processed content file (simplified for Module 3).

        Args:
            project_id: The project UUID
            source_id: The source UUID
            source: Source metadata
        """
        processed_dir = self.data_dir / 'projects' / project_id / 'sources' / 'processed'
        processed_dir.mkdir(parents=True, exist_ok=True)

        processed_file = processed_dir / f"{source_id}.txt"
        
        # For Module 3, create a simple placeholder processed content
        file_type = source.get('file_type', '')
        original_name = source.get('original_name', 'unknown')
        
        content = f"""# Extracted from {file_type.upper()} document: {original_name}
# Type: {file_type.upper()}
# Total pages: 1
# Processed at: {datetime.utcnow().isoformat()}
# token_count: 1200
# ---

=== {file_type.upper()} PAGE 1 of 1 ===

This is processed content for: {original_name}

[Module 3 Basic Implementation - Actual content extraction will be implemented in future modules]

File Type: {source.get('category', 'unknown').title()}
File Size: {source.get('file_size', 0)} bytes
Status: Successfully processed

This processed content file serves as a placeholder for the actual text extraction
that will be implemented in Module 5: Source Management - Advanced.
"""

        with open(processed_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def _load_source_from_index(self, project_id: str, source_id: str) -> Optional[Dict[str, Any]]:
        """Load a specific source from the sources index."""
        sources_index_path = self.data_dir / 'projects' / project_id / 'sources' / 'sources_index.json'
        
        if not sources_index_path.exists():
            return None
        
        try:
            with open(sources_index_path, 'r') as f:
                sources = json.load(f)
                return next((s for s in sources if s['id'] == source_id), None)
        except (json.JSONDecodeError, IOError):
            return None

    def _update_source_status(self, project_id: str, source_id: str, status: str, 
                             processing_info: Optional[Dict[str, Any]] = None,
                             embedding_info: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update the status of a source in the sources index.

        Args:
            project_id: The project UUID
            source_id: The source UUID
            status: New status
            processing_info: Processing information to update
            embedding_info: Embedding information to update

        Returns:
            True if updated successfully, False otherwise
        """
        sources_index_path = self.data_dir / 'projects' / project_id / 'sources' / 'sources_index.json'
        
        if not sources_index_path.exists():
            return False
        
        try:
            # Load current index
            with open(sources_index_path, 'r') as f:
                sources = json.load(f)
            
            # Find and update source
            for i, source in enumerate(sources):
                if source['id'] == source_id:
                    source['status'] = status
                    source['updated_at'] = datetime.utcnow().isoformat()
                    
                    if processing_info:
                        source['processing_info'] = processing_info
                    
                    if embedding_info:
                        source['embedding_info'] = embedding_info
                    
                    sources[i] = source
                    break
            else:
                return False  # Source not found
            
            # Save updated index
            with open(sources_index_path, 'w') as f:
                json.dump(sources, f, indent=2)
            
            return True
            
        except (json.JSONDecodeError, IOError):
            return False


# Global instance for use by other services
source_processing_service = SourceProcessingService()