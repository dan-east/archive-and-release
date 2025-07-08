import logging
import os
from typing import Optional
from git import Repo
from github import Github, Auth 
from github.GitRelease import GitRelease
from releaser.utilities import file_util
from . import errors_util, helpers

_logger:logging.Logger = logging.getLogger(__name__)

class GitHubRepository() :
    """
    Utility class for interacting with GitHub.
    """

    def __init__(self, git_repository:Repo) :
        helpers.assertSet(_logger, "GitHub::The git repository is not set", git_repository)
        self._git_repository:Repo = git_repository
       
        self._token:str = self._getGitHubToken()
        self._github:Github = Github(auth=Auth.Token(self._token))
        
        
    def createRelease(self, release_name:str, release_description:str, tagName:str) -> GitRelease:
        """
        Create a new release on GitHub.

        Args:
            release_name (str): The name of the release.
            release_description (str): The description of the release.
            tagName (str): The name of the tag to create the release from.

        Returns:
            GitRelease: The release.
        """
        helpers.assertSet(_logger, "GitHub::The release name is not set", release_name)
        helpers.assertSet(_logger, "GitHub::The release description is not set", release_description)
        helpers.assertSet(_logger, "GitHub::The tag name is not set", tagName)
        return self._getGitHubRepository().create_git_release(tagName, name=release_name, message=release_description, draft=False, prerelease=False)
 
 
    def uploadFileToRelease(self, release:GitRelease, file_name:str, file_path:str, content_type:str = "") :
        """
        Upload a file to a release on GitHub.

        Args:
            release (GitRelease): The release to upload the file to.
            file_name (str): The name of the file to upload.
            file_path (str): The path to the file to upload.
            content_type (str): The content type of the file to upload.
            
        Raises:
            GitHubError: If the file does not exist or is not a file.
        """
        helpers.assertSet(_logger, "GitHub::The release is not set", release)
        helpers.assertSet(_logger, "GitHub::The file name is not set", file_name)
        helpers.assertSet(_logger, "GitHub::The file path is not set", file_path)
        
        _logger.info(f"Uploading {file_path} to release.")
        
        # Check the file exists and is a file
        if file_util.exists(file_path) and file_util.isFile(file_path) : 
            if(helpers.hasValue(content_type)) :
                release.upload_asset(file_path, content_type=content_type, name=file_name)
            else :
                release.upload_asset(file_path, name=file_name)
        else :
            raise GitHubError(f"Cannot upload file to release ({release.name}) - the file does not exist ({file_path}).")
            
        _logger.info(f"Uploaded {file_path} to release.")


    def _getGitHubRepository(self):
        """
        Get the GitHub repository.

        Returns:
            Github: The GitHub repository.
        """
        return self._github.get_repo(self.getRepositoryName())
           
            
    def _getGitHubToken(self) -> str:
        """
        Get the GitHub token from the environment variable GITHUB_TOKEN.

        Raises:
            errors_util.ProjectError: If the GITHUB_TOKEN environment variable is not set.

        Returns:
            str: The token.
        """
        token:Optional[str] = os.getenv('GITHUB_TOKEN')
        if not token:
            raise GitHubError("GITHUB_TOKEN environment variable is not set")
        return token


    def getRepositoryName(self) -> str:
        """
        Get the name (Owner/Repository) of this repository.
        
        Returns:
            str: The name (Owner/Repository) of this repository.
        """
        return self._determineRepositoryName()
    
    
    def _determineRepositoryName(self) -> str:
    
        url:str = self._getRepository().remotes.origin.url
                
        # Remove protocol and domain
        if url.startswith("https://github.com/"):
            repo_path = url[len("https://github.com/"):]
        elif url.startswith("git@github.com:"):
            repo_path = url[len("git@github.com:"):]
        else:
            raise GitHubError(f"The repository is a GitHub repository ({url}).")

        # Remove .git suffix if present
        if repo_path.endswith(".git"):
            repo_path = repo_path[:-4]

        # Remove trailing slash if present
        return repo_path.rstrip("/")


    def _getRepository(self) -> Repo:
        """
        Get the repository from the git repository.

        Returns:
            Repo: The repository.
        """
        return self._git_repository


class GitHubError(errors_util.UtilityError) :
    """Raised by the this utility function to indicate some issue."""
