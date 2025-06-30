import pytest
import logging
from releaser.utilities import helpers

def get_dummy_logger():
    logger = logging.getLogger('dummy')
    logger.setLevel(logging.ERROR)
    return logger

def test_isSet_true():
    logger = get_dummy_logger()
    assert helpers.isSet(logger, 'should not log', 123)

def test_isSet_false_logs():
    logger = get_dummy_logger()
    assert not helpers.isSet(logger, 'should log', None)

def test_assertSet_exits():
    logger = get_dummy_logger()
    with pytest.raises(SystemExit):
        helpers.assertSet(logger, 'should exit', None)

def test_isEmpty():
    assert helpers.isEmpty(None)
    assert helpers.isEmpty('')
    assert not helpers.isEmpty('abc')

def test_hasValue():
    assert not helpers.hasValue(None)
    assert not helpers.hasValue('')
    assert helpers.hasValue('abc')

def test_addIfNotNone():
    l = []
    helpers.addIfNotNone(l, None)
    assert l == []
    helpers.addIfNotNone(l, '')
    assert l == []
    helpers.addIfNotNone(l, 'foo')
    assert l == ['foo']

def test_getKey():
    d = {'a': 1}
    assert helpers.getKey(d, 'a') == 1
    assert helpers.getKey(d, 'b') is None 