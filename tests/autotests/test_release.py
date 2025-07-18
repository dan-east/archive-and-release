import pytest
from unittest import mock
from releaser import release

@pytest.fixture(autouse=True)
def patch_logger():
    with mock.patch.object(release, "_logger") as logger:
        yield logger

def test_validateRepositoryUrl_valid(monkeypatch):
    monkeypatch.setattr(release.helpers, "isValidUrl", lambda url: True)
    # Should not exit for valid URL
    release._validateRepositoryUrl("https://github.com/example/repo")

def test_validateRepositoryUrl_invalid(monkeypatch):
    monkeypatch.setattr(release.helpers, "isValidUrl", lambda url: False)
    with pytest.raises(SystemExit):
        release._validateRepositoryUrl("not_a_url")

def test_prepareRepositoryTargetDirectory_creates_dir(monkeypatch):
    monkeypatch.setattr(release.file_util, "exists", lambda d: False)
    mkdir = mock.Mock()
    monkeypatch.setattr(release.file_util, "mkdir", mkdir)
    monkeypatch.setattr(release.helpers, "assertSet", lambda *a, **k: None)
    release._prepareRepositoryTargetDirectory("/tmp/testdir")
    mkdir.assert_called_once_with("/tmp/testdir")

def test_prepareRepositoryTargetDirectory_deletes_contents(monkeypatch):
    monkeypatch.setattr(release.file_util, "exists", lambda d: True)
    monkeypatch.setattr(release.file_util, "isDir", lambda d: True)
    delete = mock.Mock()
    monkeypatch.setattr(release.file_util, "deleteContents", delete)
    monkeypatch.setattr(release.helpers, "assertSet", lambda *a, **k: None)
    release._prepareRepositoryTargetDirectory("/tmp/testdir")
    delete.assert_called_once_with("/tmp/testdir")

def test_prepareRepositoryTargetDirectory_not_a_dir(monkeypatch):
    monkeypatch.setattr(release.file_util, "exists", lambda d: True)
    monkeypatch.setattr(release.file_util, "isDir", lambda d: False)
    monkeypatch.setattr(release.helpers, "assertSet", lambda *a, **k: None)
    with pytest.raises(release.errors_util.ProjectError):
        release._prepareRepositoryTargetDirectory("/tmp/notadir")

def test_prepareReleaseTargetDirectory_creates_dir(monkeypatch):
    monkeypatch.setattr(release.file_util, "exists", lambda d: False)
    mkdir = mock.Mock()
    monkeypatch.setattr(release.file_util, "mkdir", mkdir)
    monkeypatch.setattr(release.helpers, "assertSet", lambda *a, **k: None)
    release._prepareReleaseTargetDirectory("/tmp/releasedir")
    mkdir.assert_called_once_with("/tmp/releasedir")

def test_prepareReleaseTargetDirectory_not_a_dir(monkeypatch):
    monkeypatch.setattr(release.file_util, "exists", lambda d: True)
    monkeypatch.setattr(release.file_util, "isDir", lambda d: False)
    monkeypatch.setattr(release.helpers, "assertSet", lambda *a, **k: None)
    with pytest.raises(release.errors_util.ProjectError):
        release._prepareReleaseTargetDirectory("/tmp/notadir")

def test_cleanRepository_calls_removeFilesOfTypes(monkeypatch):
    remove = mock.Mock()
    monkeypatch.setattr(release.file_util, "removeFilesOfTypes", remove)
    monkeypatch.setattr(release.file_util, "readListFromFile", lambda f: ["*.tmp"])
    release._cleanRepository("/tmp/repo", "patterns.txt")
    remove.assert_called_once_with("/tmp/repo", ["*.tmp"])

def test_zipRepository_calls_zip(monkeypatch):
    zip_mock = mock.Mock(return_value="/tmp/release.zip")
    monkeypatch.setattr(release.zip_util, "zip", zip_mock)
    result = release._zipRepository("/tmp/repo", "/tmp/rel", "release.zip")
    zip_mock.assert_called_once_with("/tmp/repo", "/tmp/rel", "release.zip")
    assert result == "/tmp/release.zip"

def test_createTag_calls_repo(monkeypatch):
    repo = mock.Mock()
    repo.getRepository.return_value.working_dir = "/tmp/repo"
    release._createTag(repo, "v1.0", "desc")
    repo.createTag.assert_called_once_with(tag_name="v1.0", tag_description="desc")

def test_buildCommand_calls_build(monkeypatch):
    called = {}
    def fake_build(*args, **kwargs):
        called['called'] = True
    monkeypatch.setattr(release, "_build", fake_build)
    args = mock.Mock()
    args.repo = "repo"
    args.branch = "main"
    args.repo_target_dir = "dir"
    args.clean_patterns = "patterns"
    args.release_target_dir = "rel"
    args.release_file_name = "file.zip"
    release._buildCommand(args)
    assert called['called']

def test_buildAndReleaseCommand_uses_tag_if_release_not_set(monkeypatch):
    called = {}
    def fake_buildAndReleaseToGitHub(*args, **kwargs):
        called['args'] = args
    monkeypatch.setattr(release, "_buildAndReleaseToGitHub", fake_buildAndReleaseToGitHub)
    args = mock.Mock()
    args.repo = "repo"
    args.branch = "main"
    args.repo_target_dir = "dir"
    args.clean_patterns = "patterns"
    args.release_target_dir = "rel"
    args.release_file_name = "file.zip"
    args.tag_version = "v1.0"
    args.tag_description = "desc"
    args.release_version = None
    args.release_description = None
    monkeypatch.setattr(release.helpers, "hasValue", lambda v: v is not None)
    release._buildAndReleaseCommand(args)
    assert called['args'][6] == "v1.0"  # tag_version used as release_version

def test_buildAndReleaseToGitHub_calls_all(monkeypatch):
    monkeypatch.setattr(release.helpers, "assertSet", lambda *a, **k: None)
    monkeypatch.setattr(release, "_validateRepositoryUrl", lambda url: None)
    repo = mock.Mock()
    repo.getRepository.return_value = mock.Mock(working_dir="/tmp/repo")
    monkeypatch.setattr(release, "_cloneRepository", lambda **kwargs: repo)
    monkeypatch.setattr(release, "_createTag", lambda **kwargs: None)
    github_repo = mock.Mock()
    github_repo.createRelease.return_value = "release"
    github_repo.uploadFileToRelease = mock.Mock()
    monkeypatch.setattr(release.github_util, "GitHubRepository", lambda r: github_repo)
    monkeypatch.setattr(release, "_buildRelease", lambda **kwargs: "/tmp/release.zip")
    release._buildAndReleaseToGitHub(
        "repo_url", "branch", "target_dir", "patterns", "rel_dir", "rel_name",
        "tag", "tag_desc", "rel_ver", "rel_desc"
    )
    github_repo.createRelease.assert_called_once()
    github_repo.uploadFileToRelease.assert_called_once()
