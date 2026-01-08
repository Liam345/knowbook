"""
Source CRUD endpoints - core source management.

Educational Note: These endpoints handle the lifecycle of source files:
- List all sources for a project
- Upload new source files (multipart/form-data)
- Get/update/delete individual sources
- Download original files
- Get aggregate statistics

File Upload Flow:
1. Frontend sends multipart/form-data with file
2. We validate file type against allowed extensions
3. File is saved to data/projects/{id}/sources/raw/
4. Source entry created in sources_index.json
5. Background processing triggered automatically

Supported File Types (by category):
- document: .pdf, .docx, .pptx, .txt, .md
- image: .png, .jpg, .jpeg, .webp, .gif
- audio: .mp3, .wav, .m4a, .ogg, .flac
- data: .csv

Routes:
- GET    /projects/<id>/sources          - List all sources
- POST   /projects/<id>/sources          - Upload file
- GET    /projects/<id>/sources/<id>     - Get source details
- PUT    /projects/<id>/sources/<id>     - Update metadata
- DELETE /projects/<id>/sources/<id>     - Delete source
- GET    /projects/<id>/sources/<id>/download - Download file
- GET    /projects/<id>/sources/summary  - Aggregate stats
- GET    /sources/allowed-types          - List allowed extensions
"""
from flask import Blueprint, jsonify, request, current_app, send_file
from app.services.source_service import SourceService

# Create blueprint
sources_bp = Blueprint('sources', __name__, url_prefix='/api/v1')

# Initialize service
source_service = SourceService()


@sources_bp.route('/projects/<project_id>/sources', methods=['GET'])
def list_sources(project_id: str):
    """
    List all sources for a project.

    Educational Note: Returns metadata for all uploaded sources,
    sorted by most recent first. Includes processing status so
    UI can show progress indicators.

    Returns:
        {
            "success": true,
            "sources": [...],
            "count": 5
        }
    """
    try:
        sources = source_service.list_sources(project_id)

        return jsonify({
            'success': True,
            'sources': sources,
            'count': len(sources)
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error listing sources: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sources_bp.route('/projects/<project_id>/sources', methods=['POST'])
def upload_source(project_id: str):
    """
    Upload a new source file to a project.

    Educational Note: This endpoint demonstrates multipart/form-data handling.
    Files are streamed to disk, not loaded entirely into memory - important
    for large PDFs and audio files.

    Content-Type: multipart/form-data
    Form Fields:
        - file: The source file (required)
        - name: Display name (optional, defaults to filename)
        - description: Description (optional)

    Processing is triggered automatically after upload. Status will be:
    uploaded -> processing -> embedding -> ready

    Returns:
        {
            "success": true,
            "source": { ... source object ... },
            "message": "Source uploaded successfully"
        }
    """
    try:
        # Validate file is in request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400

        file = request.files['file']

        if not file.filename:
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400

        # Get optional fields from form data
        name = request.form.get('name')
        description = request.form.get('description', '')

        # Upload the source (triggers background processing)
        source = source_service.upload_source(
            project_id=project_id,
            file=file,
            name=name,
            description=description
        )

        return jsonify({
            'success': True,
            'source': source,
            'message': 'Source uploaded successfully'
        }), 201

    except ValueError as e:
        # Validation errors (file type not allowed, etc.)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

    except Exception as e:
        current_app.logger.error(f"Error uploading source: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sources_bp.route('/projects/<project_id>/sources/<source_id>', methods=['GET'])
def get_source(project_id: str, source_id: str):
    """
    Get a specific source's metadata.

    Educational Note: Returns full metadata including:
    - Basic info (name, description, file type)
    - Processing status and progress
    - Embedding info (if processed)
    - Summary (AI-generated description)

    Returns:
        {
            "success": true,
            "source": { ... full source object ... }
        }
    """
    try:
        source = source_service.get_source(project_id, source_id)

        if not source:
            return jsonify({
                'success': False,
                'error': 'Source not found'
            }), 404

        return jsonify({
            'success': True,
            'source': source
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error getting source: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sources_bp.route('/projects/<project_id>/sources/<source_id>', methods=['PUT'])
def update_source(project_id: str, source_id: str):
    """
    Update a source's metadata (name, description, active status).

    Educational Note: This endpoint allows changing display metadata
    without re-uploading or reprocessing the file. The 'active' flag
    controls whether the source is included in RAG queries.

    Request Body:
        {
            "name": "New name",
            "description": "New description",
            "active": true
        }

    Returns:
        {
            "success": true,
            "source": { ... updated source object ... }
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        source = source_service.update_source(project_id, source_id, data)

        if not source:
            return jsonify({
                'success': False,
                'error': 'Source not found'
            }), 404

        return jsonify({
            'success': True,
            'source': source
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error updating source: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sources_bp.route('/projects/<project_id>/sources/<source_id>', methods=['DELETE'])
def delete_source(project_id: str, source_id: str):
    """
    Delete a source and all its associated files.

    Educational Note: This is a "hard delete" that removes:
    - Original file from raw/ directory
    - Processed content from processed/ directory  
    - Individual chunks from chunks/ directory
    - Embeddings from vector database
    - Entry from sources_index.json

    This operation cannot be undone.

    Returns:
        {
            "success": true,
            "message": "Source deleted successfully"
        }
    """
    try:
        success = source_service.delete_source(project_id, source_id)

        if not success:
            return jsonify({
                'success': False,
                'error': 'Source not found'
            }), 404

        return jsonify({
            'success': True,
            'message': 'Source deleted successfully'
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error deleting source: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sources_bp.route('/projects/<project_id>/sources/<source_id>/download', methods=['GET'])
def download_source(project_id: str, source_id: str):
    """
    Download the original source file.

    Educational Note: Uses Flask's send_file() to stream the file
    with appropriate MIME type headers. This avoids loading large
    files into memory and provides proper browser download behavior.

    Returns:
        File stream with appropriate headers
    """
    try:
        file_path = source_service.get_source_file_path(project_id, source_id)

        if not file_path or not file_path.exists():
            return jsonify({
                'success': False,
                'error': 'Source file not found'
            }), 404

        # Get source metadata for proper filename
        source = source_service.get_source(project_id, source_id)
        download_name = source.get('original_name', file_path.name) if source else file_path.name

        return send_file(
            file_path,
            as_attachment=True,
            download_name=download_name
        )

    except Exception as e:
        current_app.logger.error(f"Error downloading source: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sources_bp.route('/projects/<project_id>/sources/summary', methods=['GET'])
def get_sources_summary(project_id: str):
    """
    Get aggregate statistics for all sources in a project.

    Educational Note: Provides dashboard-friendly summaries:
    - Total source count
    - Count by category (document, image, audio, data)
    - Count by status (uploaded, processing, ready, failed)
    - Total file size

    Returns:
        {
            "success": true,
            "summary": {
                "total_count": 25,
                "by_category": {...},
                "by_status": {...},
                "total_size": 1048576
            }
        }
    """
    try:
        summary = source_service.get_sources_summary(project_id)

        return jsonify({
            'success': True,
            'summary': summary
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error getting sources summary: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sources_bp.route('/sources/allowed-types', methods=['GET'])
def get_allowed_types():
    """
    Get list of allowed file extensions and their categories.

    Educational Note: Returns the complete mapping of supported
    file types. Useful for frontend validation and file picker
    configuration.

    Returns:
        {
            "success": true,
            "allowed_types": {
                "document": [".pdf", ".docx", ".pptx", ".txt", ".md"],
                "image": [".png", ".jpg", ".jpeg", ".webp", ".gif"],
                "audio": [".mp3", ".wav", ".m4a", ".ogg", ".flac"],
                "data": [".csv"]
            }
        }
    """
    try:
        allowed_types = source_service.get_allowed_types()

        return jsonify({
            'success': True,
            'allowed_types': allowed_types
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error getting allowed types: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def register_sources_blueprint(app):
    """Register the sources blueprint with the Flask app."""
    app.register_blueprint(sources_bp)