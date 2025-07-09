# script-release-builder

Todo!


Builds a frontend or backend release



Commands:
Full options/help:
python -m releaser.release -h

Command options/help:
python -m releaser.release <cmd> -h

To build a release file:
python -m releaser.release build_frontend
python -m releaser.release build_backend
python -m releaser.release build --repo "https://github.com/<repository_owner>/<repository_name>" --branch main --repo_target_dir "<clone_target_dir>" --release_target_dir "<created_release_target_dir>" --release_file_name "<created_release_file_name>"


To build, create a tag and create a release:
python -m releaser.release release_frontend --tag_version "<tag_version>" --tag_description "<tag_description>"
python -m releaser.release release_backend --tag_version "<tag_version>" --tag_description "<tag_description>" --release_version "<release_version>" --release_description "<release_description>"
python -m releaser.release release --repo "https://github.com/<repository_owner>/<repository_name>" --branch main --repo_target_dir "<clone_target_dir>" --release_target_dir "<created_release_target_dir>" --release_file_name "<created_release_file_name>" --tag_version "<tag_version>" --tag_description "<tag_description>"
