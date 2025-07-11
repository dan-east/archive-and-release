# archive-and-release

! More detail is coming !
Imagine you have a number of scripts in a repository. Maybe they help to build an entire suite of servers. 
Perhaps they are written in bash, or just a collection of files that somehow work together to acheive your goals.
Importantly, they don't represent an application like a python cli appliction for example.
Perhaps there is method and structure to your madness and the repository is built up of a number of submodules (and some are private...).
Unless you want to put a personal token into your github actions (usually seen as a bad idea), these submodules can't be accessed in them.
So this cli can help. 

Locally, you can specify your personal token that can see all submodule repositories in a local virual environment, install this package into it and:
1. Package a remote repository (e.g. on github) and archive them (perhaps into a zip).
2. Package a remote repository (e.g. on github) and archive them (perhaps into a zip), tag (and push) the git repository, create a release from the tag and upload the archive to the release.

In both cases you can choose to 'clean' the repository before archiving it by removing a number of wildcarded files and folders (for example .git) that is not required in a target server.

Install:
pip install archive-and-release

Commands:
Full options/help:
archive-and-release -h

Command options/help:
archive-and-release <cmd> -h

To build a release file:
archive-and-release build_frontend
archive-and-release build_backend
archive-and-releasee build --repo "https://github.com/<repository_owner>/<repository_name>" --branch main --repo_target_dir "<clone_target_dir>" --release_target_dir "<created_release_target_dir>" --release_file_name "<created_release_file_name>"


To build, create a tag and create a release:
archive-and-release release_frontend --tag_version "<tag_version>" --tag_description "<tag_description>"
archive-and-release release_backend --tag_version "<tag_version>" --tag_description "<tag_description>" --release_version "<release_version>" --release_description "<release_description>"
archive-and-release release --repo "https://github.com/<repository_owner>/<repository_name>" --branch main --repo_target_dir "<clone_target_dir>" --release_target_dir "<created_release_target_dir>" --release_file_name "<created_release_file_name>" --tag_version "<tag_version>" --tag_description "<tag_description>"
