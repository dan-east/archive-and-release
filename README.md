# archive-and-release

## Description
Imagine you have a number of scripts in a repository. 

Perhaps they a load of bash script and other files that build a suite of services on a number of services.

Importantly, they don't represent a buildable application in the usual sense (like a python cli application for example.)

Perhaps there is method and structure to your madness and the repository is built up of a number of submodules (and some are private...).

Things like GitActions can't access other private repositories, unless you add a GitHub Token to them (usually seen as a bad idea).

This cli can help with this.

Locally, you can specify a github token that can see all submodule repositories in a local virtual environment, install this package into it and:

1. Locally create an archive (e.g. zip) of a remote repository containing any number of nested submodules.
2. Create an archive of a remote repository, tag (and push) the git repository, create a GitHub release from the tag and upload the archive to the release.

In both cases you can choose to 'clean' (i.e. remove files and folders matching a pattern, for example '.git') the repository prior to creating the archive.

## Installation
### Create a virtual environment (optional)
`python3 -m venv .env/archive-and-release` (or any directory location you like)</br>
`. .env/archive-and-release/bin/activate`

### Install archive-and-release
`pip install archive-and-release`

### Exit the virtual environment
`deactivate`

## Commands

### Full options/help
`archive-and-release -h`

### Command options/help
`archive-and-release <cmd> -h`

### Examples to build an archive
`archive-and-release build_frontend`

`archive-and-release build_backend`

`archive-and-release build --repo "https://github.com/<repository_owner>/<repository_name>" --branch main --repo_target_dir "<clone_target_dir>" --release_target_dir "<created_release_target_dir>" --release_file_name "<created_release_file_name>" --clean_patterns "<path_to_patterns_file>"` 

### Examples to build, tag and create a github release:
`archive-and-release release_frontend --tag_version "<tag_version>" --tag_description "<tag_description>"`

`archive-and-release release_backend --tag_version "<tag_version>" --tag_description "<tag_description>" --release_version "<release_version>" --release_description "<release_description>"`

`archive-and-release release --repo "https://github.com/<repository_owner>/<repository_name>" --branch main --repo_target_dir "<clone_target_dir>" --release_target_dir "<created_release_target_dir>" --release_file_name "<created_release_file_name>" --clean_patterns "<path_to_patterns_file>" --tag_version "<tag_version>" --tag_description "<tag_description>"`


## Configuration
There are a number of environment variables that can be used to control the app, or simply create a .env in the directory where you run archive-and-release from.

See the [.env.example](https://github.com/dan-east/archive-and-release/blob/main/.env.example) for more details.


## Frontend and Backend
There are commands that build the 'frontend' and 'backend' (for example `build_frontend` and `release_backend`). These are short cuts for the `build` and `release` commands and don't do anything special.
