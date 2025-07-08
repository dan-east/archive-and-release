import logging
from git import Repo, TagReference
from git.util import T
from .errors_util import UtilityError
from . import helpers, file_util

# Logging
_logger:logging.Logger = logging.getLogger(__name__)


class GitRepository() :
    """
    Utility class for interacting with Git.
    
    Args:
        repo_url (str): The URL of the Git repository to clone.
        repository (Repo): The repository object.
    """

    def __init__(self, repo_url:str, repository:Repo) :
        helpers.assertSet(_logger, "GitRepository::The repository URL is not set", repo_url)
        helpers.assertSet(_logger, "GitRepository::The repository is not set", repository)
        self._repo_url:str = repo_url
        self._repository:Repo = repository
        
        
    @classmethod
    def clone(cls, repo_url:str, clone_target_dir:str) -> 'GitRepository' :
        """
        Clone a Git repository from the given URL to the specified path.

        Args:
            repo_url (str): The URL of the Git repository to clone.
            clone_target_dir (str): The local path where the repository should be cloned.

        Returns:
            Git: A Git object representing the cloned repository.

        Raises:
            GitError: If the repository cannot be cloned.
        """
        if helpers.isValidUrl(repo_url) :
            if helpers.hasValue(clone_target_dir) and file_util.isDir(clone_target_dir) :
                _logger.debug(f"Cloning repository from {repo_url} to {clone_target_dir}")
                try:
                    repository:Repo = Repo.clone_from(repo_url, clone_target_dir)
                    _logger.debug(f"Repository cloned successfully to {clone_target_dir}") 
                    return cls(repo_url, repository)
                except Exception as e:
                    _logger.error(f"Error cloning repository: {e}")
                    raise GitError(f"Failed to clone repository from {repo_url} to {clone_target_dir}") from e
            else :
                raise GitError(f"Invalid clone target directory: {clone_target_dir}")
        else :
            raise GitError(f"Invalid repository URL: {repo_url}")


    @classmethod
    def cloneRepositoryBranch(cls, repo_url, clone_target_dir:str, branch:str, depth:int = 1) -> 'GitRepository' :
        """
        Clone a Git repository from the given URL to the specified path.

        Args:
            repo_url (str): The URL of the Git repository to clone.
            clone_target_dir (str): The local path where the repository should be cloned.
            branch (str): The branch of the Git repository to clone.
            depth (int): The depth of the Git repository to clone. Defaults to 1, a shallow clone (no history)

        Returns:
            Git: A Git object representing the cloned repository.

        Raises:
            GitError: If the repository cannot be cloned.
        """
        if helpers.hasValue(repo_url) and helpers.isValidUrl(repo_url) :
            if helpers.hasValue(clone_target_dir) and file_util.isDir(clone_target_dir) :
                _logger.debug(f"Cloning repository from {repo_url} to {clone_target_dir}")
                try:
                    repository:Repo = Repo.clone_from(repo_url, clone_target_dir, branch=branch, depth=depth) # Using depth=1 for a shallow clone (not interested in history)
                    _logger.debug(f"Repository cloned successfully to {clone_target_dir}") 
                    return cls(repo_url, repository)
                except Exception as e:
                    _logger.error(f"Error cloning repository: {e}")
                    raise GitError(f"Failed to clone repository from {repo_url} to {clone_target_dir}") from e
            else :
                raise GitError(f"Invalid clone target directory: {clone_target_dir}")
        else :
            raise GitError(f"Invalid repository URL: {repo_url}")
                
                
    def initAnySubmodules(self) :
        """
        Initialize any submodules in the given repository.

        Args:
            repository (Repo): The Repo object representing the repository in which to initialize submodules.
        """
        _logger.debug(f"Initializing submodules in {self._repository.working_dir}...")
        self._repository.submodule_update(init=True, recursive=True)
        _logger.debug(f"Submodules initialized in {self._repository.working_dir}") 
        
        
    def createTag(self, tag_name:str, tag_description:str = "") :
        """
        Create a new tag in the given repository.

        Args:
            tag_name (str): The name of the tag to create.
            tag_description (str): The description of the tag to create.
            
        Raises:
            GitError: If the tag cannot be created (for example the tag already exists)
        """
        helpers.assertSet(_logger, "GitRepository::The tag name is not set", tag_name)
        _logger.debug(f"Creating tag {tag_name} in {self._repository.working_dir}...")

        try :
            # Create the tag
            tag:TagReference = self._repository.create_tag(tag_name, message=tag_description)
            
            # Push to the remote repository
            self._repository.remote('origin').push(tag.path)
        except Exception as e:
            _logger.error(f"Failed to create tag {tag_name} in {self._repository.working_dir}: {e}")
            raise GitError(f"Failed to create tag {tag_name} in {self._repository.working_dir}") from e
        
        _logger.debug(f"Tag {tag_name} created and pushed to origin")
        
        
    def archive(self, archive_name:str, archive_format:str = "zip") -> str :
        """
        Archive the repository to a file.
        Note that this is functionally equivalent to running `git archive` in the repository directory.
        That means untracked, ignored, and uncommitted files are not included in the archive.

        Args:
            archive_name (str): The name of the archive to create.
            archive_format (str, optional): The format of the archive to create. Defaults to "zip".

        Returns:
            str: The path to the archive file.
        """
        _logger.debug(f"Archiving repository {self._repository.working_dir} to {archive_name}...")
        
        file_path:str = file_util.buildPath(str(self._repository.working_dir), archive_name)
        with open(file_path, "wb") as archive_file:
            self._repository.archive(archive_file, archive_format)
            
        _logger.debug(f"Archive {archive_name} created at {file_path}")
        
        return file_path
    
    
    def getRepository(self) -> Repo:
        """
        Get the repository for this GitRepository.

        Returns:
            Repo: The repository object.
        """
        return self._repository
        
    
class GitError(UtilityError):
    """
    Wraps underlying exceptions to make handling them easier for calling code.
    All Git-related errors are represented by this class.
    """