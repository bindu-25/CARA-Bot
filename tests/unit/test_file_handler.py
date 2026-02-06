import pytest
from pathlib import Path
from app.utils.file_handler import FileHandler


def test_file_handler_initialization():
    """Test FileHandler initializes correctly"""
    handler = FileHandler()
    assert handler.upload_dir.exists()


def test_extract_text_unsupported_format():
    """Test error handling for unsupported file types"""
    handler = FileHandler()
    
    with pytest.raises(ValueError):
        handler.extract_text(Path("test.xyz"))