import pytest
from releaser.utilities import errors_util

def test_project_error():
    with pytest.raises(errors_util.ProjectError):
        raise errors_util.ProjectError('project error')

def test_utility_error():
    with pytest.raises(errors_util.UtilityError):
        raise errors_util.UtilityError('utility error')

def test_zip_error():
    with pytest.raises(errors_util.ZipError):
        raise errors_util.ZipError('zip error')

def test_file_error():
    with pytest.raises(errors_util.FileError):
        raise errors_util.FileError('file error') 