import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class ProjectManager:
    def __init__(self):
        self.projects_file = Path("storage/projects.json")
        self.load_projects()
    
    def load_projects(self):
        if self.projects_file.exists():
            with open(self.projects_file, 'r') as f:
                self.projects = json.load(f)
        else:
            self.projects = {
                "projects": [
                    {
                        "id": 1, 
                        "name": "Default Project", 
                        "description": "Default project for all generations", 
                        "created_at": datetime.now().isoformat(), 
                        "image_count": 0
                    }
                ]
            }
            self.save_projects()
    
    def save_projects(self):
        self.projects_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.projects_file, 'w') as f:
            json.dump(self.projects, f, indent=2)
    
    def create_project(self, name: str, description: str = "") -> Dict:
        new_project = {
            "id": len(self.projects["projects"]) + 1,
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "image_count": 0,
            "tags": [],
            "is_active": True
        }
        self.projects["projects"].append(new_project)
        self.save_projects()
        return new_project
    
    def get_projects(self, active_only: bool = False) -> List[Dict]:
        projects = self.projects["projects"]
        if active_only:
            projects = [p for p in projects if p.get("is_active", True)]
        return projects
    
    def update_project(self, project_id: int, updates: Dict) -> Optional[Dict]:
        for project in self.projects["projects"]:
            if project["id"] == project_id:
                project.update(updates)
                self.save_projects()
                return project
        return None
    
    def add_image_to_project(self, project_id: int, image_id: int):
        for project in self.projects["projects"]:
            if project["id"] == project_id:
                project["image_count"] += 1
                if "image_ids" not in project:
                    project["image_ids"] = []
                project["image_ids"].append(image_id)
                self.save_projects()
                return True
        return False
