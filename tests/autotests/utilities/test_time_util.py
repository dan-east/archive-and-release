import pytest
from releaser.utilities import time_util
from datetime import datetime, timedelta
import time

def test_getCurrentDateTimeString_default():
    result = time_util.getCurrentDateTimeString()
    assert isinstance(result, str)
    # Should match the default format
    assert len(result) == len('dd/mm/yyyy hh:mm:ss')

def test_getCurrentDateTimeString_custom():
    fmt = '%Y-%m-%d'
    result = time_util.getCurrentDateTimeString(fmt)
    assert datetime.strptime(result, fmt)

def test_howOld_recent():
    now = time.time()
    delta = time_util.howOld(now)
    assert isinstance(delta, timedelta)
    assert delta.total_seconds() < 2

def test_howOld_past():
    past = time.time() - 86400  # 1 day ago
    delta = time_util.howOld(past)
    assert isinstance(delta, timedelta)
    assert 86300 < delta.total_seconds() < 86500

def test_howOldDays():
    past = int(time.time() - 3 * 86400)
    days = time_util.howOldDays(past)
    assert days == 3 