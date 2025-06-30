import pytest
import tempfile
from unittest.mock import Mock, patch
from git import Repo, GitCommandError, TagReference
from releaser.utilities import git_util

def create_mock_repo():
    """Create a mock Git repository for testing."""
    mock_repo = Mock(spec=Repo)
    mock_repo.working_dir = "/tmp/mock_repo"
    mock_repo.remote.return_value = Mock()
    return mock_repo


def test_git_repository_init():
    """Test GitRepository initialization."""
    mock_repo = create_mock_repo()
    git_repo = git_util.GitRepository("https://github.com/test/repo", mock_repo)
    
    assert git_repo._repo_url == "https://github.com/test/repo"
    assert git_repo._repository == mock_repo


@patch('releaser.utilities.git_util.Repo')
def test_clone_success(mock_repo_class):
    """Test successful repository cloning."""
    mock_repo = create_mock_repo()
    mock_repo_class.clone_from.return_value = mock_repo
    
    with tempfile.TemporaryDirectory() as tmpdir:
        git_repo = git_util.GitRepository.clone("https://github.com/test/repo", tmpdir)
        
        assert isinstance(git_repo, git_util.GitRepository)
        assert git_repo._repo_url == "https://github.com/test/repo"
        assert git_repo._repository == mock_repo
        mock_repo_class.clone_from.assert_called_once_with("https://github.com/test/repo", tmpdir)


@patch('releaser.utilities.git_util.Repo')
def test_clone_failure(mock_repo_class):
    """Test repository cloning failure."""
    mock_repo_class.clone_from.side_effect = GitCommandError("clone", "Failed to clone")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(git_util.GitError):
            git_util.GitRepository.clone("https://github.com/test/repo", tmpdir)


@patch('releaser.utilities.git_util.Repo')
def test_clone_repository_branch_success(mock_repo_class):
    """Test successful repository cloning with specific branch."""
    mock_repo = create_mock_repo()
    mock_repo_class.clone_from.return_value = mock_repo
    
    with tempfile.TemporaryDirectory() as tmpdir:
        git_repo = git_util.GitRepository.cloneRepositoryBranch(
            "https://github.com/test/repo", 
            tmpdir, 
            "main", 
            depth=1
        )
        
        assert isinstance(git_repo, git_util.GitRepository)
        assert git_repo._repo_url == "https://github.com/test/repo"
        assert git_repo._repository == mock_repo
        mock_repo_class.clone_from.assert_called_once_with(
            "https://github.com/test/repo", 
            tmpdir, 
            branch="main", 
            depth=1
        )


@patch('releaser.utilities.git_util.Repo')
def test_clone_repository_branch_failure(mock_repo_class):
    """Test repository cloning with branch failure."""
    mock_repo_class.clone_from.side_effect = GitCommandError("clone", "Failed to clone branch")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(git_util.GitError):
            git_util.GitRepository.cloneRepositoryBranch(
                "https://github.com/test/repo", 
                tmpdir, 
                "main"
            )


def test_init_any_submodules():
    """Test submodule initialization."""
    mock_repo = create_mock_repo()
    git_repo = git_util.GitRepository("https://github.com/test/repo", mock_repo)
    
    git_repo.initAnySubmodules()
    
    mock_repo.submodule_update.assert_called_once_with(init=True, recursive=True)


def test_create_release_tag():
    """Test creating and pushing a release tag."""
    mock_repo = create_mock_repo()
    mock_tag = Mock(spec=TagReference)
    mock_tag.path = "refs/tags/v1.0.0"
    mock_repo.create_tag.return_value = mock_tag
    
    mock_remote = Mock()
    mock_repo.remote.return_value = mock_remote
    
    git_repo = git_util.GitRepository("https://github.com/test/repo", mock_repo)
    
    git_repo.createReleaseTag("v1.0.0", "Release version 1.0.0")
    
    mock_repo.create_tag.assert_called_once_with("v1.0.0", message="Release version 1.0.0")
    mock_repo.remote.assert_called_once_with('origin')
    mock_remote.push.assert_called_once_with("refs/tags/v1.0.0")


def test_git_error_inheritance():
    """Test that GitError inherits from UtilityError."""
    assert issubclass(git_util.GitError, git_util.UtilityError)


def test_git_error_creation():
    """Test GitError can be created and raised."""
    with pytest.raises(git_util.GitError):
        raise git_util.GitError("Test error message")


@patch('releaser.utilities.git_util.Repo')
def test_clone_with_empty_url(mock_repo_class):
    """Test cloning with empty repository URL."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(git_util.GitError):
            git_util.GitRepository.clone("", tmpdir)


def test_git_repository_repr():
    """Test GitRepository string representation."""
    mock_repo = create_mock_repo()
    git_repo = git_util.GitRepository("https://github.com/test/repo", mock_repo)
    
    # Test that the object can be converted to string (for debugging)
    str_repr = str(git_repo)
    assert "GitRepository" in str_repr or "object" in str_repr 
