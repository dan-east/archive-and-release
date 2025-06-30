import pytest
import tempfile
import os
from releaser.utilities import file_util

def test_mkdir_and_exists():
    with tempfile.TemporaryDirectory() as tmpdir:
        newdir = os.path.join(tmpdir, 'subdir')
        file_util.mkdir(newdir)
        assert os.path.exists(newdir)
        assert file_util.exists(newdir)
        assert file_util.isDir(newdir)

def test_isFile():
    with tempfile.NamedTemporaryFile() as tmpfile:
        assert file_util.isFile(tmpfile.name)
        assert not file_util.isDir(tmpfile.name)

def test_buildPath():
    assert file_util.buildPath('a', 'b', 'c') == os.path.join('a', 'b', 'c')
    assert file_util.buildPath('', 'b', None, 'c') == os.path.join('b', 'c') # this lint error is something that happen in real life, so we should test it.
    assert file_util.buildPath() == ''

def test_returnLastPartOfPath():
    assert file_util.returnLastPartOfPath('/foo/bar/baz.txt') == 'baz.txt'
    assert file_util.returnLastPartOfPath('foo') == 'foo'

def test_getParentDirectory():
    assert file_util.getParentDirectory('/foo/bar/baz.txt') == '/foo/bar'
    assert file_util.getParentDirectory('foo') == ''

def test_getUserDirectory():
    home = file_util.getUserDirectory()
    assert os.path.exists(home)
    assert os.path.isdir(home)

def test_copy_and_copyContents():
    with tempfile.TemporaryDirectory() as tmpdir:
        src = os.path.join(tmpdir, 'src')
        dst = os.path.join(tmpdir, 'dst')
        os.mkdir(src)
        with open(os.path.join(src, 'file.txt'), 'w') as f:
            f.write('hello')
        assert file_util.copy(src, dst)
        assert os.path.exists(os.path.join(dst, 'file.txt'))
        # Test copyContents
        dst2 = os.path.join(tmpdir, 'dst2')
        os.mkdir(dst2)
        assert file_util.copyContents(src, dst2)
        assert os.path.exists(os.path.join(dst2, 'file.txt'))

def test_delete_and_deleteContents():
    with tempfile.TemporaryDirectory() as tmpdir:
        d = os.path.join(tmpdir, 'd')
        os.mkdir(d)
        f = os.path.join(d, 'f.txt')
        with open(f, 'w') as file:
            file.write('x')
        file_util.deleteContents(d)
        assert not os.path.exists(f)
        with open(f, 'w') as file:
            file.write('x')
        file_util.delete(f)
        assert not os.path.exists(f)

def test_emptyFileContents_and_createFile():
    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        tmpfile.write(b'abc')
        tmpfile.flush()
        file_util.emptyFileContents(tmpfile.name)
        with open(tmpfile.name) as f:
            assert f.read() == ''
        os.unlink(tmpfile.name)
    with tempfile.NamedTemporaryFile(delete=True) as tmpfile:
        pass
    file_util.createFile(tmpfile.name)
    assert os.path.exists(tmpfile.name)

def test_findNewestFileInDirectory():
    with tempfile.TemporaryDirectory() as tmpdir:
        f1 = os.path.join(tmpdir, 'a.txt')
        f2 = os.path.join(tmpdir, 'b.txt')
        with open(f1, 'w') as f:
            f.write('1')
        with open(f2, 'w') as f:
            f.write('2')
        os.utime(f1, (1, 1))
        os.utime(f2, None)  # set to now
        newest = file_util.findNewestFileInDirectory(tmpdir, '*.txt')
        assert newest == f2

def test_readFile_success():
    with tempfile.NamedTemporaryFile('w+', delete=False) as tmpfile:
        tmpfile.write('hello')
        tmpfile.flush()
        assert file_util.readFile(tmpfile.name) == 'hello'
        os.unlink(tmpfile.name)

def test_readFile_error():
    with pytest.raises(file_util.FileError):
        file_util.readFile('does_not_exist.txt')

def test_readListFromFile_normal():
    with tempfile.NamedTemporaryFile('w+', delete=False) as tmpfile:
        tmpfile.write('foo\nbar\n# comment\n   \nbaz\n')
        tmpfile.flush()
        result = file_util.readListFromFile(tmpfile.name)
        assert result == ['foo', 'bar', 'baz']
        os.unlink(tmpfile.name)

def test_readListFromFile_empty():
    with tempfile.NamedTemporaryFile('w+', delete=False) as tmpfile:
        tmpfile.write('   \n# comment\n')
        tmpfile.flush()
        result = file_util.readListFromFile(tmpfile.name)
        assert result == []
        os.unlink(tmpfile.name)

def test_readListFromFile_error():
    with pytest.raises(file_util.FileError):
        file_util.readListFromFile('does_not_exist.txt') 

def test_removeFilesOfTypes():
    with tempfile.TemporaryDirectory() as tmpdir:
        f1 = os.path.join(tmpdir, 'a.log')
        f2 = os.path.join(tmpdir, 'b.txt')
        with open(f1, 'w') as f:
            f.write('1')
        with open(f2, 'w') as f:
            f.write('2')
        file_util.removeFilesOfTypes(tmpdir, ['*.log'])
        assert not os.path.exists(f1)
        assert os.path.exists(f2)
