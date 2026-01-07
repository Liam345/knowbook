from flask import Blueprint, request, jsonify
from app.services.project_service import project_service

bp = Blueprint('projects', __name__)

@bp.route('/projects', methods=['GET'])
def get_projects():
    """Get list of all projects."""
    try:
        projects = project_service.get_all_projects()
        return jsonify({'success': True, 'data': projects})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/projects', methods=['POST'])
def create_project():
    """Create a new project."""
    try:
        data = request.get_json()
        project = project_service.create_project(
            name=data.get('name'),
            description=data.get('description', '')
        )
        return jsonify({'success': True, 'data': project}), 201
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    """Get a specific project by ID."""
    try:
        project = project_service.get_project(project_id)
        if not project:
            return jsonify({'success': False, 'error': 'Project not found'}), 404
        return jsonify({'success': True, 'data': project})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/projects/<project_id>', methods=['PUT'])
def update_project(project_id):
    """Update a project."""
    try:
        data = request.get_json()
        project = project_service.update_project(
            project_id=project_id,
            name=data.get('name'),
            description=data.get('description')
        )
        if not project:
            return jsonify({'success': False, 'error': 'Project not found'}), 404
        return jsonify({'success': True, 'data': project})
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete a project."""
    try:
        success = project_service.delete_project(project_id)
        if not success:
            return jsonify({'success': False, 'error': 'Project not found'}), 404
        return jsonify({'success': True, 'message': 'Project deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500