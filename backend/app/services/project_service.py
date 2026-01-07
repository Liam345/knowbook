import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional
import shutil
from config import Config

class ProjectService:
    """Service for managing projects."""
    
    def __init__(self):
        self.projects_dir = Config.PROJECTS_DIR
        self.projects_index_path = os.path.join(Config.DATA_DIR, 'projects_index.json')
        
        # Initialize projects index if it doesn't exist
        if not os.path.exists(self.projects_index_path):
            self._save_projects_index([])
    
    def _load_projects_index(self) -> List[Dict]:
        """Load the projects index from disk."""
        try:
            with open(self.projects_index_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_projects_index(self, projects: List[Dict]) -> None:
        """Save the projects index to disk."""
        with open(self.projects_index_path, 'w') as f:
            json.dump(projects, f, indent=2)
    
    def _generate_project_id(self) -> str:
        """Generate a unique project ID."""
        return str(uuid.uuid4())
    
    def _get_project_path(self, project_id: str) -> str:
        """Get the path to a project's data directory."""
        return os.path.join(self.projects_dir, project_id)
    
    def _get_project_file_path(self, project_id: str) -> str:
        """Get the path to a project's JSON file."""
        return os.path.join(self.projects_dir, f"{project_id}.json")
    
    def _create_project_structure(self, project_id: str) -> None:
        """Create the directory structure for a new project."""
        project_path = self._get_project_path(project_id)
        os.makedirs(project_path, exist_ok=True)
        
        # Create subdirectories
        subdirs = ['sources', 'chats', 'memory']
        for subdir in subdirs:
            os.makedirs(os.path.join(project_path, subdir), exist_ok=True)
    
    def get_all_projects(self) -> List[Dict]:
        """Get all projects with basic info."""
        projects = self._load_projects_index()
        
        # Add full project data for each project
        result = []
        for project_info in projects:
            project_id = project_info['id']
            project = self.get_project(project_id)
            if project:
                result.append(project)
        
        return result
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get a specific project by ID."""
        project_file = self._get_project_file_path(project_id)
        
        try:
            with open(project_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def create_project(self, name: str, description: str = '') -> Dict:
        """Create a new project."""
        if not name or not name.strip():
            raise ValueError("Project name is required")
        
        project_id = self._generate_project_id()
        current_time = datetime.utcnow().isoformat()
        
        project = {
            'id': project_id,
            'name': name.strip(),
            'description': description.strip(),
            'created_at': current_time,
            'updated_at': current_time,
            'last_opened': current_time,
            'stats': {
                'sources_count': 0,
                'chats_count': 0,
                'total_size': 0
            }
        }
        
        # Create project structure
        self._create_project_structure(project_id)
        
        # Save project file
        project_file = self._get_project_file_path(project_id)
        with open(project_file, 'w') as f:
            json.dump(project, f, indent=2)
        
        # Update projects index
        projects = self._load_projects_index()
        projects.append({
            'id': project_id,
            'name': project['name'],
            'created_at': project['created_at']
        })
        self._save_projects_index(projects)
        
        return project
    
    def update_project(self, project_id: str, name: str = None, description: str = None) -> Optional[Dict]:
        """Update a project."""
        project = self.get_project(project_id)
        if not project:
            return None
        
        if name is not None:
            if not name.strip():
                raise ValueError("Project name cannot be empty")
            project['name'] = name.strip()
        
        if description is not None:
            project['description'] = description.strip()
        
        project['updated_at'] = datetime.utcnow().isoformat()
        
        # Save updated project
        project_file = self._get_project_file_path(project_id)
        with open(project_file, 'w') as f:
            json.dump(project, f, indent=2)
        
        # Update projects index if name changed
        if name is not None:
            projects = self._load_projects_index()
            for proj in projects:
                if proj['id'] == project_id:
                    proj['name'] = project['name']
                    break
            self._save_projects_index(projects)
        
        return project
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project and all its data."""
        project = self.get_project(project_id)
        if not project:
            return False
        
        # Remove from projects index
        projects = self._load_projects_index()
        projects = [p for p in projects if p['id'] != project_id]
        self._save_projects_index(projects)
        
        # Remove project file
        project_file = self._get_project_file_path(project_id)
        if os.path.exists(project_file):
            os.remove(project_file)
        
        # Remove project directory
        project_path = self._get_project_path(project_id)
        if os.path.exists(project_path):
            shutil.rmtree(project_path)
        
        return True
    
    def update_last_opened(self, project_id: str) -> None:
        """Update the last opened timestamp for a project."""
        project = self.get_project(project_id)
        if project:
            project['last_opened'] = datetime.utcnow().isoformat()
            project_file = self._get_project_file_path(project_id)
            with open(project_file, 'w') as f:
                json.dump(project, f, indent=2)

# Singleton instance
project_service = ProjectService()