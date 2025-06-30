import pytest
import tempfile
import os
import logging
from releaser.utilities import log_util

def test_setupRootLogging_adds_handlers():
    with tempfile.TemporaryDirectory() as tmpdir:
        logfile = os.path.join(tmpdir, 'test.log')
        log_util.setupRootLogging(logfile)
        root = logging.getLogger(None)
        # Should have at least two handlers (stdout and file)
        assert len(root.handlers) >= 2 