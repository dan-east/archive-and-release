import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from git import Repo
from github import Github, Auth
from github.GitRelease import GitRelease

from releaser.utilities.github_util import GitHubRepository, GitHubError


class TestGitHubRepository:
    """Test cases for GitHubRepository class."""
    
    @pytest.fixture
    def mock_repo(self):
        """Create a mock git repository."""
        mock_repo = Mock(spec=Repo)
        mock_remote = Mock()
        mock_remote.url = "https://github.com/testowner/testrepo.git"
        mock_repo.remotes.origin = mock_remote
        return mock_repo
    
    @pytest.fixture
    def mock_github(self):
        """Create a mock GitHub instance."""
        return Mock(spec=Github)
    
    @pytest.fixture
    def mock_github_repo(self):
        """Create a mock GitHub repository."""
        return Mock()
    
    @pytest.fixture
    def mock_git_release(self):
        """Create a mock GitRelease instance."""
        return Mock(spec=GitRelease)
    
    def test_init_success(self, mock_repo):
        """Test successful initialization of GitHubRepository."""
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'test_token'}):
            with patch('releaser.utilities.github_util.Github') as mock_github_class:
                mock_github_instance = Mock()
                mock_github_class.return_value = mock_github_instance
                
                github_repo = GitHubRepository(mock_repo)
                
                assert github_repo._git_repository == mock_repo
                mock_github_class.assert_called_once()
                call_args = mock_github_class.call_args
                assert call_args is not None
                assert 'auth' in call_args.kwargs
                assert isinstance(call_args.kwargs['auth'], Auth.Token)
                assert call_args.kwargs['auth'].token == 'test_token'
    
    def test_init_missing_token(self, mock_repo):
        """Test initialization fails when GITHUB_TOKEN is not set."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(GitHubError, match="GITHUB_TOKEN environment variable is not set"):
                GitHubRepository(mock_repo)
    
    def test_init_none_repository(self):
        """Test initialization fails when repository is None."""
        with pytest.raises(SystemExit):
            GitHubRepository(None)  # type: ignore
    
    def test_get_repository_name_https(self, mock_repo):
        """Test getting repository name from HTTPS URL."""
        mock_repo.remotes.origin.url = "https://github.com/testowner/testrepo.git"
        
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'test_token'}):
            with patch('releaser.utilities.github_util.Github'):
                github_repo = GitHubRepository(mock_repo)
                repo_name = github_repo.getRepositoryName()
                
                assert repo_name == "testowner/testrepo"
    
    def test_get_repository_name_ssh(self, mock_repo):
        """Test getting repository name from SSH URL."""
        mock_repo.remotes.origin.url = "git@github.com:testowner/testrepo.git"
        
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'test_token'}):
            with patch('releaser.utilities.github_util.Github'):
                github_repo = GitHubRepository(mock_repo)
                repo_name = github_repo.getRepositoryName()
                
                assert repo_name == "testowner/testrepo"
    
    def test_get_repository_name_without_git_suffix(self, mock_repo):
        """Test getting repository name from URL without .git suffix."""
        mock_repo.remotes.origin.url = "https://github.com/testowner/testrepo"
        
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'test_token'}):
            with patch('releaser.utilities.github_util.Github'):
                github_repo = GitHubRepository(mock_repo)
                repo_name = github_repo.getRepositoryName()
                
                assert repo_name == "testowner/testrepo"
    
    def test_get_repository_name_with_trailing_slash(self, mock_repo):
        """Test getting repository name from URL with trailing slash."""
        mock_repo.remotes.origin.url = "https://github.com/testowner/testrepo/"
        
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'test_token'}):
            with patch('releaser.utilities.github_util.Github'):
                github_repo = GitHubRepository(mock_repo)
                repo_name = github_repo.getRepositoryName()
                
                assert repo_name == "testowner/testrepo"
    
    def test_get_repository_name_invalid_url(self, mock_repo):
        """Test getting repository name from invalid URL raises error."""
        mock_repo.remotes.origin.url = "https://gitlab.com/testowner/testrepo.git"
        
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'test_token'}):
            with patch('releaser.utilities.github_util.Github'):
                github_repo = GitHubRepository(mock_repo)
                with pytest.raises(GitHubError, match="The repository is a GitHub repository"):
                    github_repo.getRepositoryName()
    
    def test_create_release_success(self, mock_repo, mock_github_repo, mock_git_release):
        """Test successful release creation."""
        mock_github_repo.create_git_release.return_value = mock_git_release
        
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'test_token'}):
            with patch('releaser.utilities.github_util.Github') as mock_github_class:
                mock_github_instance = Mock()
                mock_github_instance.get_repo.return_value = mock_github_repo
                mock_github_class.return_value = mock_github_instance
                
                github_repo = GitHubRepository(mock_repo)
                result = github_repo.createRelease(
                    release_name="Test Release",
                    release_description="Test Description",
                    tagName="v1.0.0"
                )
                
                assert result == mock_git_release
                mock_github_repo.create_git_release.assert_called_once_with(
                    "v1.0.0",
                    name="Test Release",
                    message="Test Description",
                    draft=False,
                    prerelease=False
                )
    
    def test_create_release_missing_name(self, mock_repo):
        """Test release creation fails when name is None."""
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'test_token'}):
            with patch('releaser.utilities.github_util.Github'):
                github_repo = GitHubRepository(mock_repo)
                with pytest.raises(SystemExit):
                    github_repo.createRelease(None, "description", "tag")  # type: ignore
    
    def test_create_release_missing_description(self, mock_repo):
        """Test release creation fails when description is None."""
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'test_token'}):
            with patch('releaser.utilities.github_util.Github'):
                github_repo = GitHubRepository(mock_repo)
                with pytest.raises(SystemExit):
                    github_repo.createRelease("name", None, "tag")  # type: ignore
    
    def test_create_release_missing_tag(self, mock_repo):
        """Test release creation fails when tag is None."""
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'test_token'}):
            with patch('releaser.utilities.github_util.Github'):
                github_repo = GitHubRepository(mock_repo)
                with pytest.raises(SystemExit):
                    github_repo.createRelease("name", "description", None)  # type: ignore
    
    def test_upload_file_to_release_success_with_content_type(self, mock_repo, mock_git_release):
        """Test successful file upload to release with content type."""
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'test_token'}):
            with patch('releaser.utilities.github_util.Github'):
                with patch('releaser.utilities.github_util.file_util') as mock_file_util:
                    mock_file_util.exists.return_value = True
                    mock_file_util.isFile.return_value = True
                    
                    github_repo = GitHubRepository(mock_repo)
                    github_repo.uploadFileToRelease(
                        release=mock_git_release,
                        file_name="test.zip",
                        file_path="/path/to/test.zip",
                        content_type="application/zip"
                    )
                    
                    mock_git_release.upload_asset.assert_called_once_with(
                        "/path/to/test.zip",
                        content_type="application/zip",
                        name="test.zip"
                    )
    
    def test_upload_file_to_release_success_without_content_type(self, mock_repo, mock_git_release):
        """Test successful file upload to release without content type."""
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'test_token'}):
            with patch('releaser.utilities.github_util.Github'):
                with patch('releaser.utilities.github_util.file_util') as mock_file_util:
                    mock_file_util.exists.return_value = True
                    mock_file_util.isFile.return_value = True
                    
                    github_repo = GitHubRepository(mock_repo)
                    github_repo.uploadFileToRelease(
                        release=mock_git_release,
                        file_name="test.zip",
                        file_path="/path/to/test.zip",
                        content_type=""
                    )
                    
                    mock_git_release.upload_asset.assert_called_once_with(
                        "/path/to/test.zip",
                        name="test.zip"
                    )
    
    def test_upload_file_to_release_file_not_exists(self, mock_repo, mock_git_release):
        """Test file upload fails when file doesn't exist."""
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'test_token'}):
            with patch('releaser.utilities.github_util.Github'):
                with patch('releaser.utilities.github_util.file_util') as mock_file_util:
                    mock_file_util.exists.return_value = False
                    
                    github_repo = GitHubRepository(mock_repo)
                    with pytest.raises(GitHubError, match="Cannot upload file to release"):
                        github_repo.uploadFileToRelease(
                            release=mock_git_release,
                            file_name="test.zip",
                            file_path="/path/to/test.zip"
                        )
    
    def test_upload_file_to_release_not_a_file(self, mock_repo, mock_git_release):
        """Test file upload fails when path is not a file."""
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'test_token'}):
            with patch('releaser.utilities.github_util.Github'):
                with patch('releaser.utilities.github_util.file_util') as mock_file_util:
                    mock_file_util.exists.return_value = True
                    mock_file_util.isFile.return_value = False
                    
                    github_repo = GitHubRepository(mock_repo)
                    with pytest.raises(GitHubError, match="Cannot upload file to release"):
                        github_repo.uploadFileToRelease(
                            release=mock_git_release,
                            file_name="test.zip",
                            file_path="/path/to/test.zip"
                        )
    
    def test_upload_file_to_release_missing_release(self, mock_repo):
        """Test file upload fails when release is None."""
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'test_token'}):
            with patch('releaser.utilities.github_util.Github'):
                github_repo = GitHubRepository(mock_repo)
                with pytest.raises(SystemExit):
                    github_repo.uploadFileToRelease(
                        release=None,  # type: ignore
                        file_name="test.zip",
                        file_path="/path/to/test.zip"
                    )
    
    def test_upload_file_to_release_missing_file_name(self, mock_repo, mock_git_release):
        """Test file upload fails when file name is None."""
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'test_token'}):
            with patch('releaser.utilities.github_util.Github'):
                github_repo = GitHubRepository(mock_repo)
                with pytest.raises(SystemExit):
                    github_repo.uploadFileToRelease(
                        release=mock_git_release,
                        file_name=None,  # type: ignore
                        file_path="/path/to/test.zip"
                    )
    
    def test_upload_file_to_release_missing_file_path(self, mock_repo, mock_git_release):
        """Test file upload fails when file path is None."""
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'test_token'}):
            with patch('releaser.utilities.github_util.Github'):
                github_repo = GitHubRepository(mock_repo)
                with pytest.raises(SystemExit):
                    github_repo.uploadFileToRelease(
                        release=mock_git_release,
                        file_name="test.zip",
                        file_path=None  # type: ignore
                    )
    
    def test_get_github_repository(self, mock_repo, mock_github_repo):
        """Test getting GitHub repository."""
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'test_token'}):
            with patch('releaser.utilities.github_util.Github') as mock_github_class:
                mock_github_instance = Mock()
                mock_github_instance.get_repo.return_value = mock_github_repo
                mock_github_class.return_value = mock_github_instance
                
                github_repo = GitHubRepository(mock_repo)
                result = github_repo._getGitHubRepository()
                
                assert result == mock_github_repo
                mock_github_instance.get_repo.assert_called_once_with("testowner/testrepo")
    
    def test_get_github_token(self, mock_repo):
        """Test getting GitHub token from environment."""
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'test_token'}):
            with patch('releaser.utilities.github_util.Github'):
                github_repo = GitHubRepository(mock_repo)
                token = github_repo._getGitHubToken()
                
                assert token == "test_token"
    
    def test_get_github_token_missing(self, mock_repo):
        """Test getting GitHub token fails when not set."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(GitHubError, match="GITHUB_TOKEN environment variable is not set"):
                GitHubRepository(mock_repo)
    
    def test_get_repository(self, mock_repo):
        """Test getting the git repository."""
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'test_token'}):
            with patch('releaser.utilities.github_util.Github'):
                github_repo = GitHubRepository(mock_repo)
                result = github_repo._getRepository()
                
                assert result == mock_repo


class TestGitHubError:
    """Test cases for GitHubError class."""
    
    def test_github_error_inheritance(self):
        """Test that GitHubError inherits from UtilityError."""
        from releaser.utilities.errors_util import UtilityError
        
        error = GitHubError("Test error")
        assert isinstance(error, UtilityError)
    
    def test_github_error_message(self):
        """Test that GitHubError has correct message."""
        error = GitHubError("Test error message")
        assert str(error) == "Test error message" 