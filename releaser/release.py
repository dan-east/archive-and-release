#!/usr/bin/env python3

import argparse
import logging
import traceback
import dotenv

from releaser.utilities import github_util, helpers, log_util, git_util, file_util, zip_util, errors_util, time_util
import releaser.constants as constants

# Logging
_logger = logging.getLogger(__name__)  # module name


# Sets up the whole shebang
def _init() :
    dotenv.load_dotenv()
    log_util.setupRootLogging(constants.LOG_TO_FILE)


# Deals with all the command-line interface
def _commandRunner() :
    parser = argparse.ArgumentParser(description="Fetch and resolve external dependencies for a project.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers()
    _buildFrontend(subparsers)
    _buildBackend(subparsers)
    _build(subparsers)

    args:argparse.Namespace = parser.parse_args()
    args.func(args)

# Builds the frontend release.
def _buildFrontend(subparsers) :
    runner = subparsers.add_parser("build_frontend", help="Builds the frontend release.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    runner.add_argument("--repo", "-r", help='The repo to clone', default=constants.FRONTEND_REPO_URL)
    runner.add_argument("--branch", "-b", help='The branch to use', default=constants.FRONTEND_REPO_BRANCH)
    runner.add_argument("--repo_target_dir", "-c", help='Where to clone the repo to (warning: existing directories will be emptied first)', default=constants.FRONTEND_CLONE_DIR)
    runner.add_argument("--release_target_dir", "-t", help='Where to put the zipped release', default=constants.RELEASE_DIR)
    runner.add_argument("--release_name", "-n", help='The name to use.', default=constants.FRONTEND_RELEASE_NAME) 
    runner.add_argument("--clean_patterns", "-p", help='A path to a file containing a list of files to be removed from the repository prior to creating the release.', default=constants.CLEAN_PATTERNS_FILE)
    runner.set_defaults(func=_buildCommand)


# Builds the backend release.
def _buildBackend(subparsers) :
    runner = subparsers.add_parser("build_backend", help="Builds the backend release.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    runner.add_argument("--repo", "-r", help='The repo to clone', default=constants.BACKEND_REPO_URL)
    runner.add_argument("--branch", "-b", help='The branch to use', default=constants.BACKEND_REPO_BRANCH)
    runner.add_argument("--repo_target_dir", "-c", help='Where to clone the repo to (warning: existing directories will be emptied first)', default=constants.BACKEND_CLONE_DIR)
    runner.add_argument("--release_target_dir", "-t", help='Where to put the zipped release', default=constants.RELEASE_DIR)
    runner.add_argument("--release_name", "-n", help='The name to use.', default=constants.BACKEND_RELEASE_NAME) 
    runner.add_argument("--clean_patterns", "-p", help='A path to a file containing a list of files to be removed from the repository prior to creating the release.', default=constants.CLEAN_PATTERNS_FILE)
    runner.set_defaults(func=_buildCommand)


# Builds a release for the specified repository.
def _build(subparsers) :
    runner = subparsers.add_parser("build", help="Builds a release for the specified repository.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    runner.add_argument("--repo", "-r", help='The repo to clone')
    runner.add_argument("--branch", "-b", help='The branch to use', default="main")
    runner.add_argument("--repo_target_dir", "-c", help='Where to clone the repo to (warning: existing directories will be emptied first)', default=constants.CLONE_DIR)
    runner.add_argument("--release_target_dir", "-t", help='Where to put the zipped release', default=constants.RELEASE_DIR)
    runner.add_argument("--release_name", "-n", help='The name to use.', default=f"archive-{time_util.getCurrentDateTimeString(format="%Y%m%d")}.zip") 
    runner.add_argument("--clean_patterns", "-p", help='A path to a file containing a list of files to be removed from the repository prior to creating the release.', default=constants.CLEAN_PATTERNS_FILE)
    runner.set_defaults(func=_buildCommand)


def _buildCommand(args:argparse.Namespace) :
    _buildRelease(args.repo, args.branch, args.repo_target_dir, args.clean_patterns, args.release_target_dir, args.release_name)
    

def _buildRelease(repository_url:str, repository_branch:str, repository_target_dir:str, patterns_file:str, release_target_dir:str, release_target_name:str) :
    """
    Builds the release from the given repository and branch to the given directory and name.

    Args:
        repository_url (str): The Url of the repository to create the release for.
        repository_branch (str): The branch of the repository to use.
        repository_target_dir (str): The directory to clone the repository to.
        patterns_file (str): Path to a file containing patterns of files to remove before creating the release.
        release_target_dir (str): The directory to place the release in.
        release_target_name (str): The name of the release file.
    """
    _logger.info(f"Building release for {repository_url}:{repository_branch}")
    
    # Prepare repository target dirs
    _prepareRepositoryTargetDirectory(repository_target_dir)
    _prepareReleaseTargetDirectory(release_target_dir)
    
    # Clone the repository from the given path
    repository:git_util.GitRepository = _cloneRepository(repository_url=repository_url, repository_branch=repository_branch, repository_target_dir=repository_target_dir)

    # Create the release tag
#    repository.createReleaseTag(release_name=release_target_name, release_description=f"Release {release_target_name}")

    # Clean the repository
    _cleanRepository(repository_target_dir=repository_target_dir, patterns_file=patterns_file)
    
    # Zip the repository - this is where the actual build happens
    _zipRepository(repository_target_dir=repository_target_dir, release_target_dir=release_target_dir, release_target_name=release_target_name)
    
    # Release to GitHub   
 #   github_util.createRelease(repo_name="your-org/your-repo", tag_name=f"v{release_target_name}", release_name=f"Release {release_target_name}", body="Release notes here", file_path=zip_path)
    
    
    # Here you would add the logic to build the release, e.g., compiling code, packaging files, etc.
    _logger.info("Release build completed successfully.")


def _prepareRepositoryTargetDirectory(repository_target_dir:str) :
    """
    Prepares the repository target directory by creating it if it doesn't exist and deleting its contents if it does.

    Args:
        repository_target_dir (str): The directory to prepare.

    Raises:
        errors_util.ProjectError: If the directory is not actually directory.
    """
    helpers.assertSet(_logger, "_prepareRepositoryTargetDirectory::repository_target_dir not set", repository_target_dir)
    _logger.info(f"Preparing repository target directory: {repository_target_dir}")
    
    if file_util.exists(repository_target_dir) :
        if not file_util.isDir(repository_target_dir) : 
            raise errors_util.ProjectError(f"{repository_target_dir} is not a directory.")
        _logger.info(f"Deleting contents of {repository_target_dir}")
        file_util.deleteContents(repository_target_dir)
    else :
        _logger.info(f"Creating directory: {repository_target_dir}")
        file_util.mkdir(repository_target_dir)
        
        
def _prepareReleaseTargetDirectory(release_target_dir:str) :
    """
    Prepares the release target directory by creating it if it doesn't exist.

    Args:
        release_target_dir (str): The directory to prepare.

    Raises:
        errors_util.ProjectError: If the directory is not actually directory.
    """
    helpers.assertSet(_logger, "_prepareReleaseTargetDirectory::release_target_dir not set", release_target_dir)
    _logger.info(f"Preparing release target directory: {release_target_dir}")
    
    if file_util.exists(release_target_dir) :
        if not file_util.isDir(release_target_dir) : 
            raise errors_util.ProjectError(f"{release_target_dir} is not a directory.")
    else :
        _logger.info(f"Creating directory: {release_target_dir}")
        file_util.mkdir(release_target_dir)
    

def _cloneRepository(repository_url:str, repository_branch:str, repository_target_dir:str) -> git_util.GitRepository :
    """
    Clones the repository from the given path and initializes any submodules.

    Args:
        repository_url (str): The Url of the repository to clone.
        repository_branch (str): The branch of the repository to use.
        repository_target_dir (str): The directory to clone the repository to.

    Returns:
        git_util.GitRepository: The cloned repository.

    Raises:
        git_util.GitError: If the repository cannot be cloned.
    """
    _logger.info(f"Cloning repository from {repository_url}:{repository_branch} to {repository_target_dir}...")
    
    # Clone the repository from the given path
    repository:git_util.GitRepository = git_util.GitRepository.cloneRepositoryBranch(repo_url=repository_url, branch=repository_branch, clone_target_dir=repository_target_dir)
    
    # Initialize any submodules in the repository
    repository.initAnySubmodules()
    
    _logger.info(f"...cloned repository from {repository_url}:{repository_branch} to {repository_target_dir}")
    
    return repository
    

def _cleanRepository(repository_target_dir:str, patterns_file:str) :
    """
    Cleans the repository by removing the files of the given types.

    Args:
        repository_target_dir (str): The directory to clean.
        patterns_file (str): The file containing the patterns of files to remove.
    """
    _logger.info(f"Cleaning repository in {repository_target_dir}...")
    file_util.removeFilesOfTypes(repository_target_dir, file_util.readListFromFile(patterns_file))
    _logger.info(f"...cleaned repository in {repository_target_dir}")
    
    
def _zipRepository(repository_target_dir:str, release_target_dir:str, release_target_name:str) :
    """
    Zips the repository to the given directory and name.

    Args:
        repository_target_dir (str): The directory to zip.
        release_target_dir (str): The directory to place the zip file in.
        release_target_name (str): The name of the zip file.
    """
    _logger.info(f"Zipping repository in {repository_target_dir} to {release_target_dir}/{release_target_name}...")
    zip_util.zip(repository_target_dir, release_target_dir, release_target_name)
    _logger.info(f"...zipped repository in {repository_target_dir} to {release_target_dir}/{release_target_name}")
    
    
# the entry point
try :
    if __name__ == "__main__" :
        _init()
        _commandRunner()
except Exception :
    _logger.error(f"Command caught an exception (may not be harmful): {traceback.format_exc()}")
    raise
