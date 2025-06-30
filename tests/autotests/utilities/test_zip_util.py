import pytest
import tempfile
import os
import zipfile
from releaser.utilities import zip_util
from releaser.utilities.errors_util import ZipError

def create_test_directory_structure(base_dir):
    """Create a test directory structure with files and subdirectories."""
    # Create main directory
    main_dir = os.path.join(base_dir, "test_source")
    os.makedirs(main_dir)
    
    # Create files in main directory
    with open(os.path.join(main_dir, "file1.txt"), "w") as f:
        f.write("content1")
    with open(os.path.join(main_dir, "file2.txt"), "w") as f:
        f.write("content2")
    
    # Create subdirectory
    subdir = os.path.join(main_dir, "subdir")
    os.makedirs(subdir)
    
    # Create files in subdirectory
    with open(os.path.join(subdir, "file3.txt"), "w") as f:
        f.write("content3")
    
    # Create nested subdirectory
    nested_dir = os.path.join(subdir, "nested")
    os.makedirs(nested_dir)
    with open(os.path.join(nested_dir, "file4.txt"), "w") as f:
        f.write("content4")
    
    return main_dir

def test_zip_success():
    """Test successful zipping of a directory with subdirectories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        source_dir = create_test_directory_structure(tmpdir)
        zip_dir = os.path.join(tmpdir, "zip_output")
        os.makedirs(zip_dir)
        zip_name = "test.zip"
        
        zip_util.zip(source_dir, zip_dir, zip_name)
        
        zip_path = os.path.join(zip_dir, zip_name)
        assert os.path.exists(zip_path)
        
        # Verify zip contents
        with zipfile.ZipFile(zip_path, 'r') as zf:
            file_list = zf.namelist()
            assert "file1.txt" in file_list
            assert "file2.txt" in file_list
            assert "subdir/file3.txt" in file_list
            assert "subdir/nested/file4.txt" in file_list

def test_zip_source_not_directory():
    """Test zip function with source that is not a directory."""
    with tempfile.NamedTemporaryFile() as tmpfile:
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ZipError):
                zip_util.zip(tmpfile.name, tmpdir, "test.zip")

def test_zip_source_does_not_exist():
    """Test zip function with non-existent source directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(ZipError):
            zip_util.zip("does_not_exist", tmpdir, "test.zip")

def test_zip_target_not_directory():
    """Test zip function with target that is not a directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        source_dir = create_test_directory_structure(tmpdir)
        with tempfile.NamedTemporaryFile() as tmpfile:
            with pytest.raises(ZipError):
                zip_util.zip(source_dir, tmpfile.name, "test.zip")

def test_unzip_success():
    """Test successful unzipping of a zip file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test zip file
        source_dir = create_test_directory_structure(tmpdir)
        zip_path = os.path.join(tmpdir, "test.zip")
        
        with zipfile.ZipFile(zip_path, 'w') as zf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, source_dir)
                    zf.write(file_path, arc_name)
        
        # Test unzipping
        extract_dir = os.path.join(tmpdir, "extracted")
        zip_util.unzip(zip_path, extract_dir)
        
        # Verify extracted contents
        assert os.path.exists(os.path.join(extract_dir, "file1.txt"))
        assert os.path.exists(os.path.join(extract_dir, "file2.txt"))
        assert os.path.exists(os.path.join(extract_dir, "subdir", "file3.txt"))
        assert os.path.exists(os.path.join(extract_dir, "subdir", "nested", "file4.txt"))

def test_unzip_invalid_zip():
    """Test unzip function with invalid zip file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a file that's not a zip
        not_zip = os.path.join(tmpdir, "notzip.txt")
        with open(not_zip, "w") as f:
            f.write("not a zip file")
        
        extract_dir = os.path.join(tmpdir, "extracted")
        with pytest.raises(ZipError):
            zip_util.unzip(not_zip, extract_dir)

def test_unzip_missing_zip():
    """Test unzip function with non-existent zip file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        extract_dir = os.path.join(tmpdir, "extracted")
        with pytest.raises(ZipError):
            zip_util.unzip("does_not_exist.zip", extract_dir)

def test_unzip_target_is_file():
    """Test unzip function with target that is a file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test zip file
        zip_path = os.path.join(tmpdir, "test.zip")
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("test.txt", "content")
        
        # Create a file as target
        target_file = os.path.join(tmpdir, "target_file")
        with open(target_file, "w") as f:
            f.write("I am a file")
        
        with pytest.raises(ZipError):
            zip_util.unzip(zip_path, target_file)

def test_isValidZipPath_true():
    """Test isValidZipPath with valid zip file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "test.zip")
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("test.txt", "content")
        
        assert zip_util.isValidZipPath(zip_path)

def test_isValidZipPath_false():
    """Test isValidZipPath with non-zip file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        not_zip = os.path.join(tmpdir, "notzip.txt")
        with open(not_zip, "w") as f:
            f.write("not a zip file")
        
        assert not zip_util.isValidZipPath(not_zip)

def test_isValidZipPath_missing():
    """Test isValidZipPath with non-existent file."""
    assert not zip_util.isValidZipPath("does_not_exist.zip")

def test_isValidZipPath_empty():
    """Test isValidZipPath with empty path."""
    assert not zip_util.isValidZipPath("") 

