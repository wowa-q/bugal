import pathlib
import shutil

# 3rd party
import pytest

@pytest.fixture
def fx_zip_archive():
    archive = FIXTURE_DIR.resolve() / 'archive.zip'
    with zipfile.ZipFile(FIXTURE_DIR.resolve() / 'archive.zip', 'w') as myzip:
        pass

    yield archive
        
    try:
        archive.unlink()
    except PermissionError:
        pass

@pytest.fixture
def fx_zip_archive_configured():
    config = tom.load_config()
    src_config = config['bugal']['src']
    for cfg in src_config:
        if pathlib.Path(cfg.get('zip_file')).is_file():
            archive = tom.ARCHIVE
        else:
            archive = pathlib.Path(cfg.get('zip_file'))
            with zipfile.ZipFile(archive, 'w') as myzip:
                pass

    yield archive
        
    try:
        archive.unlink()
    except PermissionError:
        pass