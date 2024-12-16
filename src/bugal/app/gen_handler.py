"""
Gehört zu busines layer. spezialisierter Handler.

"""
import zipfile
import logging
from pathlib import Path
from typing import Any, Optional

from bugal.app import bugal_if as a
from cfg import config as cfg
logger = logging.getLogger(__name__)

class ArtifactHandler(a.Artifact):
    """Handles artifacts
    """
    def __init__(self, archive=None):
        if archive is not None and archive.is_file():
            self.archive = archive
        else:
            self.archive = cfg.ARCHIVE

    def archive_imports(self, artifact=None):
        """adds the imported csv file into archive
        """
        if artifact is not None:
            with zipfile.ZipFile(self.archive, 'a', compression=zipfile.ZIP_DEFLATED) as newzip:
                newzip.write(artifact, arcname=artifact.name)
            artifact.unlink()
            logger.info("CSV file archived in %s: ", self.archive)
            return True
        else:
            return False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} for archiving in {self.archive}"

class PathHandler(a.AbstractHandler):
    def handle(self, request: Any) -> str:
        if isinstance(request, Path):
            return self.validate_path(request)
        else:
            return super().handle(request)

    def validate_path(self, _path):
        """Function for path validation, provided by user configuration

        Args:
            _path (str): path received for validation

        Returns:
            tuple(message, Path): returns message and Path type after successful validation
        """
        message = ''
        if len(str(_path)) > 0:
            if Path(_path).is_dir():
                message = message + ' - Path configured ok \n'
            elif Path(_path).is_file():
                str(Path(_path).suffix)
                message = message + ' - File configured ok \n'
            else:
                message = message + ' - Path is incorrect \n'
                return (message, '')
        else:
            message = message + ' - Path will use working directory \n'
            
        return (message, Path(_path))