from github import Github, Auth 
from github.GitRelease import GitRelease
from github.Repository import Repository
import os
from typing import Optional
from releaser.utilities import errors_util


class GitHub() :
    """
    Utility class for interacting with GitHub.
    """

    def __init__(self) :
        self._token:str = self._getGitHubToken()
        self._github:Github = Github(auth=Auth.Token(self._token))


    def getRepository(self, repo_name:str) -> Repository:
        return self._github.get_repo(repo_name)
    
    
    def create_github_release(self, repo_name:str, tag_name:str, release_name:str, release_description:str) -> GitRelease:
        """
        Create a new release on GitHub.

        Args:
            repo_name (str): _description_
            tag_name (str): _description_
            release_name (str): _description_
            release_description (str): _description_

        Returns:
            GitRelease: _description_
        """
        repo = self.getRepository(repo_name)
        
        # Create the release
        return repo.create_git_release(tag=tag_name, name=release_name, message=release_description, draft=False, prerelease=False)
        


    def upload_file_to_release(self, release:GitRelease, file_path:str):
        with open(file_path, 'rb') as f:
            release.upload_asset(file_path, file=f)
            
            
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



class GitHubError(errors_util.UtilityError) :
    """Raised by the this utility function to indicate some issue."""
