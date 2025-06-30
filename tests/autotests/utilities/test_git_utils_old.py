import pytest
from releaser.utilities import git_utils
from releaser.utilities.errors_util import GitError

def test_cloneRepository_raises_on_invalid_url():
    # This should raise GitError due to invalid repo URL
    with pytest.raises(GitError):
        git_utils.cloneRepository('invalid_url', 'main', '/tmp/should_not_exist')

def test_initAnySubmodules_noop():
    # We cannot test actual submodule init without a real repo, so just check it does not raise if passed a mock
    class DummyRepo:
        def submodule_update(self, init, recursive):
            self.called = True
    repo = DummyRepo()
    git_utils.initAnySubmodules(repo)  # type: ignore
    assert hasattr(repo, 'called') 