import os
from .utilities import file_util, time_util

# A repository is needed, but not defined.
UNDEFINED_REPOSITORY:str = "Repository undefined."

# Constants for the Resolver application
HOME_DIR:str = os.getenv("RELEASER_HOME", os.getcwd())

# Default runtime directory
RUNTIME_DIR:str = os.getenv("RELEASER_RUNTIME_DIR", f"{HOME_DIR}/archive-and-release-runtime")

# Logging configuration
LOG_DIR:str = os.getenv("RELEASER_LOG_DIR", RUNTIME_DIR)
LOG_TO_FILE:str =f"{LOG_DIR}/releaser.log"

# Repository URLs and branches for the releaser.
BACKEND_REPO_URL:str = os.getenv("RELEASER_BACKEND_REPO_URL", UNDEFINED_REPOSITORY)
BACKEND_REPO_BRANCH:str = os.getenv("RELEASER_BACKEND_REPO_BRANCH", "main")
FRONTEND_REPO_URL:str = os.getenv("RELEASER_FRONTEND_REPO_URL", UNDEFINED_REPOSITORY)
FRONTEND_REPO_BRANCH:str = os.getenv("RELEASER_FRONTEND_REPO_BRANCH", "main")

# Directory to clone the repository to
CLONE_DIR:str =os.getenv("RELEASER_CLONE_DIR", f"{RUNTIME_DIR}/clonedRepository")
FRONTEND_CLONE_DIR:str =os.getenv("RELEASER_FRONTEND_CLONE_DIR", f"{CLONE_DIR}/frontend")
BACKEND_CLONE_DIR:str =os.getenv("RELEASER_BACKEND_CLONE_DIR", f"{CLONE_DIR}/backend")


# Directory to build the release to
RELEASE_DIR:str =os.getenv("RELEASER_RELEASE_DIR", f"{RUNTIME_DIR}/release")

# Default release names
FRONTEND_RELEASE_NAME:str = os.getenv("RELEASER_FRONTEND_RELEASE_NAME", f"frontend-{time_util.getCurrentDateTimeString(date_format='%Y%m%d')}.zip")
BACKEND_RELEASE_NAME:str = os.getenv("RELEASER_BACKEND_RELEASE_NAME", f"backend-{time_util.getCurrentDateTimeString(date_format='%Y%m%d')}.zip")

# Pattern file - clean.txt is a sibling to constants.py
CLEAN_PATTERNS_FILE:str = os.getenv("RELEASER_CLEAN_PATTERNS_FILE", file_util.buildPath(file_util.getParentDirectory(__file__), "clean.txt"))
