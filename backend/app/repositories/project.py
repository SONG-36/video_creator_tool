"""Project repository."""

from app.models.project import Project
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    """Data access for projects."""

    model = Project
    id_field = "project_id"
