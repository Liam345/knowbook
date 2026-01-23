"""
Business Report endpoints - AI-generated business reports with data analysis.

Educational Note: Business reports combine AI-generated content with data analysis:
1. Agent plans the report structure
2. Agent can analyze CSV data and generate charts
3. Agent searches source content for context
4. Agent writes sections to create the final report

Output is Markdown with embedded charts which renders nicely on frontend.

Routes:
- POST /projects/<id>/studio/business-report              - Start generation
- GET  /projects/<id>/studio/business-report-jobs/<id>    - Job status
- GET  /projects/<id>/studio/business-report-jobs         - List jobs
- GET  /projects/<id>/studio/business-reports/<id>/preview  - Preview markdown
- GET  /projects/<id>/studio/business-reports/<id>/download - Download file (md)
- GET  /projects/<id>/studio/business-reports/<filename>  - Serve file (chart, etc.)
- DELETE /projects/<id>/studio/business-reports/<id>      - Delete document
"""
import os
from pathlib import Path
from flask import jsonify, request, current_app, send_file

from app.api.studio import studio_bp
from app.services.studio_services import studio_index_service
from app.utils.path_utils import get_studio_dir


@studio_bp.route('/projects/<project_id>/studio/business-report', methods=['POST'])
def generate_business_report(project_id: str):
    """
    Start business report generation (background task).

    Request body:
        {
            "source_id": "source-uuid",
            "direction": "optional user direction/preferences",
            "report_type": "executive_summary|financial_report|market_analysis|...",
            "csv_source_ids": ["uuid1", "uuid2"],  # CSV sources for data analysis
            "context_source_ids": ["uuid3"],  # Non-CSV sources for context
            "focus_areas": ["revenue", "growth"]  # Optional focus areas
        }

    Returns:
        202 Accepted with job_id for polling
    """
    from app.services.ai_agents import business_report_agent_service
    from app.services.source_services import source_service
    import uuid
    from concurrent.futures import ThreadPoolExecutor

    try:
        data = request.get_json()
        source_id = data.get('source_id')

        if not source_id:
            return jsonify({
                'success': False,
                'error': 'source_id is required'
            }), 400

        direction = data.get('direction', '')
        report_type = data.get('report_type', 'executive_summary')
        csv_source_ids = data.get('csv_source_ids', [])
        context_source_ids = data.get('context_source_ids', [])
        focus_areas = data.get('focus_areas', [])

        # Validate report_type
        valid_report_types = [
            'executive_summary', 'financial_report', 'market_analysis',
            'competitive_analysis', 'performance_review', 'quarterly_report',
            'annual_report', 'strategic_plan'
        ]
        if report_type not in valid_report_types:
            report_type = 'executive_summary'

        # Get source info
        source = source_service.get_source(project_id, source_id)
        if not source:
            return jsonify({
                'success': False,
                'error': 'Source not found'
            }), 404

        source_name = source.get('name', 'Unknown Source')

        # Create job
        job_id = str(uuid.uuid4())
        job = studio_index_service.create_business_report_job(
            project_id=project_id,
            job_id=job_id,
            source_id=source_id,
            source_name=source_name,
            direction=direction,
            report_type=report_type,
            csv_source_ids=csv_source_ids,
            context_source_ids=context_source_ids,
            focus_areas=focus_areas
        )

        # Start background task
        executor = ThreadPoolExecutor(max_workers=1)
        executor.submit(
            business_report_agent_service.business_report_agent_service.generate_report,
            project_id,
            source_id,
            job_id,
            direction,
            report_type,
            csv_source_ids,
            context_source_ids,
            focus_areas
        )
        executor.shutdown(wait=False)

        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Business report generation started'
        }), 202  # Accepted

    except Exception as e:
        current_app.logger.error(f"Error starting business report generation: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to start business report generation: {str(e)}'
        }), 500


@studio_bp.route('/projects/<project_id>/studio/business-report-jobs/<job_id>', methods=['GET'])
def get_business_report_job_status(project_id: str, job_id: str):
    """
    Get status of a business report generation job.

    Returns:
        Job object with current status, progress, and results if complete
    """
    try:
        job = studio_index_service.get_business_report_job(project_id, job_id)

        if not job:
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404

        return jsonify({
            'success': True,
            'job': job
        })

    except Exception as e:
        current_app.logger.error(f"Error getting business report job status: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to get job status: {str(e)}'
        }), 500


@studio_bp.route('/projects/<project_id>/studio/business-report-jobs', methods=['GET'])
def list_business_report_jobs(project_id: str):
    """
    List all business report jobs for a project, optionally filtered by source.

    Query params:
        source_id (optional): Filter by source ID

    Returns:
        List of business report jobs sorted by created_at descending
    """
    try:
        source_id = request.args.get('source_id')
        jobs = studio_index_service.list_business_report_jobs(project_id, source_id)

        return jsonify({
            'success': True,
            'jobs': jobs
        })

    except Exception as e:
        current_app.logger.error(f"Error listing business report jobs: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to list jobs: {str(e)}'
        }), 500


@studio_bp.route('/projects/<project_id>/studio/business-reports/<job_id>/preview', methods=['GET'])
def preview_business_report(project_id: str, job_id: str):
    """
    Preview business report by returning markdown content.

    Returns:
        JSON with markdown content for rendering on frontend
    """
    try:
        job = studio_index_service.get_business_report_job(project_id, job_id)

        if not job:
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404

        markdown_file = job.get('markdown_file')
        if not markdown_file:
            return jsonify({
                'success': False,
                'error': 'Business report file not yet generated'
            }), 404

        # Read markdown content
        report_dir = Path(get_studio_dir(project_id)) / "business_reports"
        file_path = report_dir / markdown_file

        if not file_path.exists():
            return jsonify({
                'success': False,
                'error': 'Business report file not found'
            }), 404

        with open(file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        return jsonify({
            'success': True,
            'title': job.get('title', 'Business Report'),
            'report_type': job.get('report_type'),
            'executive_summary': job.get('executive_summary'),
            'charts': job.get('charts', []),
            'markdown_content': markdown_content,
            'status': job.get('status')
        })

    except Exception as e:
        current_app.logger.error(f"Error previewing business report: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to preview business report: {str(e)}'
        }), 500


@studio_bp.route('/projects/<project_id>/studio/business-reports/<job_id>/download', methods=['GET'])
def download_business_report(project_id: str, job_id: str):
    """
    Download business report as markdown file.

    Returns:
        Markdown file for download
    """
    try:
        job = studio_index_service.get_business_report_job(project_id, job_id)

        if not job:
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404

        markdown_file = job.get('markdown_file')
        if not markdown_file:
            return jsonify({
                'success': False,
                'error': 'Business report file not yet generated'
            }), 404

        report_dir = Path(get_studio_dir(project_id)) / "business_reports"
        file_path = report_dir / markdown_file

        if not file_path.exists():
            return jsonify({
                'success': False,
                'error': 'Business report file not found'
            }), 404

        # Create safe filename from title
        title = job.get('title', 'Business Report')
        safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()
        if not safe_title:
            safe_title = "Business_Report"
        download_filename = f"{safe_title}.md"

        return send_file(
            file_path,
            mimetype='text/markdown',
            as_attachment=True,
            download_name=download_filename
        )

    except Exception as e:
        current_app.logger.error(f"Error downloading business report: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to download business report: {str(e)}'
        }), 500


@studio_bp.route('/projects/<project_id>/studio/business-reports/<filename>', methods=['GET'])
def get_business_report_file(project_id: str, filename: str):
    """
    Serve a business report file (chart image, etc.).

    Response:
        - File with appropriate headers
    """
    try:
        report_dir = get_studio_dir(project_id) / "business_reports"
        filepath = report_dir / filename

        if not filepath.exists():
            return jsonify({
                'success': False,
                'error': f'File not found: {filename}'
            }), 404

        # Validate the file is within the expected directory (security)
        try:
            filepath.resolve().relative_to(report_dir.resolve())
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid file path'
            }), 400

        # Determine mimetype
        if filename.endswith('.md'):
            mimetype = 'text/markdown'
        elif filename.endswith('.png'):
            mimetype = 'image/png'
        elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
            mimetype = 'image/jpeg'
        elif filename.endswith('.svg'):
            mimetype = 'image/svg+xml'
        else:
            mimetype = 'application/octet-stream'

        return send_file(
            filepath,
            mimetype=mimetype,
            as_attachment=False
        )

    except Exception as e:
        current_app.logger.error(f"Error serving business report file: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to serve file: {str(e)}'
        }), 500


@studio_bp.route('/projects/<project_id>/studio/business-reports/<job_id>', methods=['DELETE'])
def delete_business_report(project_id: str, job_id: str):
    """
    Delete a business report and its files.

    Returns:
        Success status
    """
    try:
        # Get job to verify it exists
        job = studio_index_service.get_business_report_job(project_id, job_id)
        if not job:
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404

        report_dir = Path(get_studio_dir(project_id)) / "business_reports"

        # Delete markdown file if it exists
        markdown_file = job.get('markdown_file')
        if markdown_file:
            file_path = report_dir / markdown_file
            if file_path.exists():
                os.remove(file_path)

        # Delete chart files if they exist
        charts = job.get('charts', [])
        for chart in charts:
            chart_filename = chart.get('filename')
            if chart_filename:
                chart_path = report_dir / chart_filename
                if chart_path.exists():
                    os.remove(chart_path)

        # Delete from index
        deleted = studio_index_service.delete_business_report_job(project_id, job_id)

        return jsonify({
            'success': deleted,
            'message': 'Business report deleted' if deleted else 'Failed to delete from index'
        })

    except Exception as e:
        current_app.logger.error(f"Error deleting business report: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to delete business report: {str(e)}'
        }), 500
