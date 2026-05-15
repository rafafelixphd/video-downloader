import pytest
import os
import tempfile
import shutil
from pathlib import Path
from config import load_config, get_default_download_path, set_download_path


def test_get_default_download_path_valid():
    """Test that get_default_download_path returns valid path"""
    path = get_default_download_path()
    assert isinstance(path, str)
    assert '~' not in path  # Should be expanded
    assert os.path.exists(path)
    assert os.path.isdir(path)


def test_set_download_path_invalid_nonexistent():
    """Test that set_download_path rejects non-existent paths"""
    with pytest.raises(ValueError, match="Path does not exist"):
        set_download_path("/nonexistent/invalid/path/12345/xyz")


def test_set_download_path_not_directory():
    """Test that set_download_path rejects non-directory paths"""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_file = tmp.name
    try:
        with pytest.raises(ValueError, match="is not a directory"):
            set_download_path(tmp_file)
    finally:
        os.unlink(tmp_file)


def test_set_download_path_valid():
    """Test that set_download_path accepts valid paths"""
    # Store original config
    original_config = load_config()
    original_path = original_config.get('download_path')

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Should not raise an exception
            set_download_path(tmpdir)

            # Verify the config was updated
            config = load_config()
            assert config['download_path'] == tmpdir
    finally:
        # Restore original config
        if original_path:
            set_download_path(original_path)


def test_load_config():
    """Test that load_config returns a dict"""
    config = load_config()
    assert isinstance(config, dict)
    assert 'download_path' in config


def test_load_config_has_valid_structure():
    """Test that config has expected keys and types"""
    config = load_config()
    assert isinstance(config['download_path'], str)
    assert len(config['download_path']) > 0


def test_get_default_download_path_expansion():
    """Test that tilde expansion works correctly"""
    path = get_default_download_path()
    home = os.path.expanduser("~")
    # Path should be expanded and absolute
    assert path.startswith(home) or path.startswith("/")
