#!/usr/bin/env python3

import argparse
import logging
import traceback
import dotenv

from releaser.utilities import github_util, helpers, log_util, git_util, file_util, zip_util, errors_util, time_util
import releaser.constants as constants

# Logging
_logger:logging.Logger = logging.getLogger(__name__)


# Sets up the whole shebang
def _init() :
    dotenv.load_dotenv()
    log_util.setupRootLogging(constants.LOG_TO_FILE)


# Deals with all the command-line interface
def _commandRunner() :
    parser = argparse.ArgumentParser(description="Fetch and resolve external dependencies for a project.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers()
    _buildFrontend(subparsers)
    _buildAndReleaseFrontend(subparsers)
    _buildBackend(subparsers)
    _buildAndReleaseBackend(subparsers)
    _buildRepository(subparsers)
    _buildAndRelease(subparsers)

    args:argparse.Namespace = parser.parse_args()
    args.func(args)


# Builds the frontend release.
def _buildFrontend(subparsers) :
    runner = subparsers.add_parser("build-frontend", help="Builds the frontend release.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    runner.add_argument("--repo", "-r", help='URL to the the repo to clone', default=constants.FRONTEND_REPO_URL)
    runner.add_argument("--branch", "-b", help='The branch to use', default=constants.FRONTEND_REPO_BRANCH)
    runner.add_argument("--repo_target_dir", "-c", help='Where to clone the repo to (warning: existing directories will be emptied first)', default=constants.FRONTEND_CLONE_DIR)
    runner.add_argument("--release_target_dir", "-t", help='Where to put the zipped release', default=constants.RELEASE_DIR)
    runner.add_argument("--release_file_name", "-f", help='The name to use.', default=constants.FRONTEND_RELEASE_NAME) 
    runner.add_argument("--clean_patterns", "-p", help='A path to a file containing a list of files to be removed from the repository prior to creating the release.', default=constants.CLEAN_PATTERNS_FILE)
    runner.set_defaults(func=_buildCommand)


# Builds and releases the frontend.
def _buildAndReleaseFrontend(subparsers) :
    runner = subparsers.add_parser("release-frontend", help="Builds and releases the frontend release.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    runner.add_argument("--repo", "-r", help='URL to the the repo to clone', default=constants.FRONTEND_REPO_URL)
    runner.add_argument("--branch", "-b", help='The branch to use', default=constants.FRONTEND_REPO_BRANCH)
    runner.add_argument("--repo_target_dir", "-c", help='Where to clone the repo to (warning: existing directories will be emptied first)', default=constants.FRONTEND_CLONE_DIR)
    runner.add_argument("--release_target_dir", "-t", help='Where to put the zipped release', default=constants.RELEASE_DIR)
    runner.add_argument("--release_file_name", "-f", help='The name to use.', default=constants.FRONTEND_RELEASE_NAME) 
    runner.add_argument("--clean_patterns", "-p", help='A path to a file containing a list of files to be removed from the repository prior to creating the release.', default=constants.CLEAN_PATTERNS_FILE)
    runner.add_argument("--tag_version", help='The name of the tag to create. E.g. v1.0.1. Cannot be the same as a previous tag version.', required=True)
    runner.add_argument("--tag_description", help='The description of the tag to create.', required=True)
    runner.add_argument("--release_version", help='The name of the release to create E.g. v1.11.0. Cannot be the same as a previous release version. Defaults to the tag version.', required=False)
    runner.add_argument("--release_description", help='The description of the release to create Defaults to the tag version.', required=False)
    runner.set_defaults(func=_buildAndReleaseCommand)


# Builds the backend release.
def _buildBackend(subparsers) :
    runner = subparsers.add_parser("build-backend", help="Builds the backend release.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    runner.add_argument("--repo", "-r", help='URL to the the repo to clone', default=constants.BACKEND_REPO_URL)
    runner.add_argument("--branch", "-b", help='The branch to use', default=constants.BACKEND_REPO_BRANCH)
    runner.add_argument("--repo_target_dir", "-c", help='Where to clone the repo to (warning: existing directories will be emptied first)', default=constants.BACKEND_CLONE_DIR)
    runner.add_argument("--release_target_dir", "-t", help='Where to put the zipped release', default=constants.RELEASE_DIR)
    runner.add_argument("--release_file_name", "-f", help='The name to use.', default=constants.FRONTEND_RELEASE_NAME) 
    runner.add_argument("--clean_patterns", "-p", help='A path to a file containing a list of files to be removed from the repository prior to creating the release.', default=constants.CLEAN_PATTERNS_FILE)
    runner.set_defaults(func=_buildCommand)


# Builds and releases the backend.
def _buildAndReleaseBackend(subparsers) :
    runner = subparsers.add_parser("release-backend", help="Builds and releases the backend release.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    runner.add_argument("--repo", "-r", help='URL to the the repo to clone', default=constants.BACKEND_REPO_URL)
    runner.add_argument("--branch", "-b", help='The branch to use', default=constants.BACKEND_REPO_BRANCH)
    runner.add_argument("--repo_target_dir", "-c", help='Where to clone the repo to (warning: existing directories will be emptied first)', default=constants.BACKEND_CLONE_DIR)
    runner.add_argument("--release_target_dir", "-t", help='Where to put the zipped release', default=constants.RELEASE_DIR)
    runner.add_argument("--release_file_name", "-f", help='The name to use.', default=constants.FRONTEND_RELEASE_NAME)  
    runner.add_argument("--clean_patterns", "-p", help='A path to a file containing a list of files to be removed from the repository prior to creating the release.', default=constants.CLEAN_PATTERNS_FILE)
    runner.add_argument("--tag_version", help='The name of the tag to create. E.g. v1.0.1. Cannot be the same as a previous tag version.', required=True)
    runner.add_argument("--tag_description", help='The description of the tag to create.', required=True)
    runner.add_argument("--release_version", help='The name of the release to create E.g. v1.11.0. Cannot be the same as a previous release version. Defaults to the tag version.', required=False)
    runner.add_argument("--release_description", help='The description of the release to create Defaults to the tag version.', required=False)
    runner.set_defaults(func=_buildAndReleaseCommand)


# Builds a release for the specified repository.
def _buildRepository(subparsers) :
    runner = subparsers.add_parser("build", help="Builds a release for the specified repository.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    runner.add_argument("--repo", "-r", help='URL to the the repo to clone')
    runner.add_argument("--branch", "-b", help='The branch to use', default="main")
    runner.add_argument("--repo_target_dir", "-c", help='Where to clone the repo to (warning: existing directories will be emptied first)', default=constants.CLONE_DIR)
    runner.add_argument("--release_target_dir", "-t", help='Where to put the zipped release', default=constants.RELEASE_DIR)
    runner.add_argument("--release_file_name", "-f", help='The name to use.', default=f"archive-{time_util.getCurrentDateTimeString(date_format='%Y%m%d')}.zip")
    runner.add_argument("--clean_patterns", "-p", help='A path to a file containing a list of files to be removed from the repository prior to creating the release.', default=constants.CLEAN_PATTERNS_FILE)
    runner.set_defaults(func=_buildCommand)


# Builds and releases the backend.
def _buildAndRelease(subparsers) :
    runner = subparsers.add_parser("release", help="Build and release the specified repository.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    runner.add_argument("--repo", "-r", help='URL to the the repo to clone')
    runner.add_argument("--branch", "-b", help='The branch to use', default="main")
    runner.add_argument("--repo_target_dir", "-c", help='Where to clone the repo to (warning: existing directories will be emptied first)', default=constants.CLONE_DIR)
    runner.add_argument("--release_target_dir", "-t", help='Where to put the zipped release', default=constants.RELEASE_DIR)
    runner.add_argument("--release_file_name", "-f", help='The name to use.', default=f"archive-{time_util.getCurrentDateTimeString(date_format='%Y%m%d')}.zip")
    runner.add_argument("--clean_patterns", "-p", help='A path to a file containing a list of files to be removed from the repository prior to creating the release.', default=constants.CLEAN_PATTERNS_FILE)
    runner.add_argument("--tag_version", help='The name of the tag to create. E.g. v1.0.1. Cannot be the same as a previous tag version.', required=True)
    runner.add_argument("--tag_description", help='The description of the tag to create.', required=True)
    runner.add_argument("--release_version", help='The name of the release to create E.g. v1.11.0. Cannot be the same as a previous release version. Defaults to the tag version.', required=False)
    runner.add_argument("--release_description", help='The description of the release to create Defaults to the tag version.', required=False)
    runner.set_defaults(func=_buildAndReleaseCommand)


def _buildCommand(args:argparse.Namespace) :
    """
    Builds the release from the given repository and branch to the given directory and name.

    Args:
        args (argparse.Namespace): The arguments passed to the command.
    """
    _build(args.repo, args.branch, args.repo_target_dir, args.clean_patterns, args.release_target_dir, args.release_file_name)


def _build(repository_url:str, repository_branch:str, repository_target_dir:str, patterns_file:str, release_target_dir:str, release_target_file_name:str):
    """
    Builds the release from the given repository and branch to the given directory and name.

    Args:
        repository_url (str): The Url of the repository to create the release for.
        repository_branch (str): The branch of the repository to use.
        repository_target_dir (str): The directory to clone the repository to.
        patterns_file (str): Path to a file containing patterns of files to remove before creating the release.
        release_target_dir (str): The directory to place the release in.
        release_target_file_name (str): The name of the release file.
    """
    helpers.assertSet(_logger, "_build::repository_url not set", repository_url)
    _validateRepositoryUrl(repository_url)
    helpers.assertSet(_logger, "_build::repository_branch not set", repository_branch)
    helpers.assertSet(_logger, "_build::repository_target_dir not set", repository_target_dir)
    helpers.assertSet(_logger, "_build::patterns_file not set", patterns_file)
    helpers.assertSet(_logger, "_build::release_target_dir not set", release_target_dir)
    helpers.assertSet(_logger, "_build::release_target_file_name not set", release_target_file_name)

    _logger.info(f"Building {release_target_file_name} for {repository_url}:{repository_branch}")

    # Clone the repository from the given path
    _cloneRepository(repository_url=repository_url, repository_branch=repository_branch, repository_target_dir=repository_target_dir)

    # Build the release
    _buildRelease(repository_target_dir=repository_target_dir, patterns_file=patterns_file, release_target_dir=release_target_dir, release_target_name=release_target_file_name)

    _logger.info(f"{release_target_file_name} built successfully.")


def _buildAndReleaseCommand(args:argparse.Namespace) :
    """
    Builds and releases the frontend release.

    Args:
        args (argparse.Namespace): The arguments passed to the command.
    """
    # If the release version or description is not set, use the tag's information
    release_version:str = args.release_version if helpers.hasValue(args.release_version) else args.tag_version
    release_description:str = args.release_description if helpers.hasValue(args.release_description) else args.tag_description

    _buildAndReleaseToGitHub(args.repo, args.branch, args.repo_target_dir, args.clean_patterns, args.release_target_dir, args.release_file_name, args.tag_version, args.tag_description, release_version, release_description)


def _buildAndReleaseToGitHub(repository_url:str, repository_branch:str, repository_target_dir:str, patterns_file:str, release_target_dir:str, release_target_file_name:str, tag_version:str, tag_description:str, release_version:str, release_description:str) :
    """
    Builds the release from the given repository and branch to the given directory and name.

    Args:
        repository_url (str): The Url of the repository to create the release for.
        repository_branch (str): The branch of the repository to use.
        repository_target_dir (str): The directory to clone the repository to.
        patterns_file (str): Path to a file containing patterns of files to remove before creating the release.
        release_target_dir (str): The directory to place the release in.
        release_target_file_name (str): The name of the release file.
        tag_version (str): The name of the tag to create.
        tag_description (str): The description of the tag to create.
        release_version (str): The name of the release to create.
        release_description (str): The description of the release to create.
    """
    helpers.assertSet(_logger, "_buildAndReleaseToGitHub::repository_url not set", repository_url)
    _validateRepositoryUrl(repository_url)
    helpers.assertSet(_logger, "_buildAndReleaseToGitHub::repository_branch not set", repository_branch)
    helpers.assertSet(_logger, "_buildAndReleaseToGitHub::repository_target_dir not set", repository_target_dir)
    helpers.assertSet(_logger, "_buildAndReleaseToGitHub::patterns_file not set", patterns_file)
    helpers.assertSet(_logger, "_buildAndReleaseToGitHub::release_target_dir not set", release_target_dir)
    helpers.assertSet(_logger, "_buildAndReleaseToGitHub::release_target_file_name not set", release_target_file_name)
    helpers.assertSet(_logger, "_buildAndReleaseToGitHub::tag_version not set", tag_version)
    helpers.assertSet(_logger, "_buildAndReleaseToGitHub::tag_description not set", tag_description)
    helpers.assertSet(_logger, "_buildAndReleaseToGitHub::release_version not set", release_version)
    helpers.assertSet(_logger, "_buildAndReleaseToGitHub::release_description not set", release_description)

    _logger.info(f"Building release for {repository_url}:{repository_branch}")
    
    # Clone the repository from the given path
    repository:git_util.GitRepository = _cloneRepository(repository_url=repository_url, repository_branch=repository_branch, repository_target_dir=repository_target_dir)

    # Create the tag
    _createTag(repository=repository, tag_name=tag_version, tag_description=tag_description)

    # Create the release - the build cleans the repository, potentially including the .git directory, so create the release while we still can
    github:github_util.GitHubRepository = github_util.GitHubRepository(repository.getRepository())
    release:github_util.GitRelease = github.createRelease(release_name=release_version, release_description=release_description, tagName=tag_version)

    # Build the release
    release_path:str = _buildRelease(repository_target_dir=repository_target_dir, patterns_file=patterns_file, release_target_dir=release_target_dir, release_target_name=release_target_file_name)

    # Upload the release build to the release
    github.uploadFileToRelease(release=release, file_name=release_target_file_name, file_path=release_path, content_type="application/zip")

    _logger.info("Release build completed successfully.")


def _validateRepositoryUrl(repository_url:str):
    """
    Validates the repository URL. Exits if the URL is not valid

    Args:
        repository_url (str): The URL of the repository to validate.
    """
    if not repository_url or not isinstance(repository_url, str) or not helpers.isValidUrl(repository_url) :
        _logger.error(f"Invalid repository URL provided: {repository_url}")
        return exit(1)


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

    # Prepare the repository target directory
    _prepareRepositoryTargetDirectory(repository_target_dir)

    # Clone the repository from the given path
    repository:git_util.GitRepository = git_util.GitRepository.cloneRepositoryBranch(repo_url=repository_url, branch=repository_branch, clone_target_dir=repository_target_dir)

    # Initialize any submodules in the repository
    repository.initAnySubmodules()

    _logger.info(f"...cloned repository from {repository_url}:{repository_branch} to {repository_target_dir}")

    # Return the repository
    return repository


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


def _buildRelease(repository_target_dir:str, patterns_file:str, release_target_dir:str, release_target_name:str) -> str :
    """
    Builds the release from the given repository to the given directory and name.
    Simply cleans the repository of unwanted files and zips it up.
    Useful for repositories which are essentially a number of scripts rather than a single buildable application.

    Args:
        repository_target_dir (str): The directory to clone the repository to.
        patterns_file (str): Path to a file containing patterns of files to remove before creating the release.
        release_target_dir (str): The directory to place the release in.
        release_target_name (str): The name of the release file.
        
    Returns:
        str: The path to the zip file.
    """
    _logger.info(f"Building release in {repository_target_dir} to {release_target_dir}/{release_target_name}...")

    # Prepare the release target directory
    _prepareReleaseTargetDirectory(release_target_dir)

    # Clean the repository
    _cleanRepository(repository_target_dir=repository_target_dir, patterns_file=patterns_file)
    
    # Zip the repository - this is where the actual build happens
    return _zipRepository(repository_target_dir=repository_target_dir, release_target_dir=release_target_dir, release_target_name=release_target_name)


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


def _zipRepository(repository_target_dir:str, release_target_dir:str, release_target_name:str) -> str :
    """
    Zips the repository to the given directory and name.

    Args:
        repository_target_dir (str): The directory to zip.
        release_target_dir (str): The directory to place the zip file in.
        release_target_name (str): The name of the zip file.
        
    Returns:
        str: The path to the zip file.
    """
    _logger.info(f"Zipping repository in {repository_target_dir} to {release_target_dir}/{release_target_name}...")
    return zip_util.zip(repository_target_dir, release_target_dir, release_target_name)


def _createTag(repository:git_util.GitRepository, tag_name:str, tag_description:str) :
    """
    Creates a tag in the repository.

    Args:
        repository (git_util.GitRepository): The repository to create the tag in.
        tag_name (str): The name of the tag to create.
        tag_description (str): The description of the tag to create.
    """
    _logger.info(f"Creating tag {tag_name} in {repository.getRepository().working_dir}...")
    repository.createTag(tag_name=tag_name, tag_description=tag_description)
    _logger.info(f"...created tag {tag_name} in {repository.getRepository().working_dir}")


def main() :
    try :
        _init()
        _commandRunner()
    except Exception :
        _logger.error(f"Command caught an exception (may not be harmful): {traceback.format_exc()}")
        raise


# the entry point
if __name__ == "__main__" :
    main()