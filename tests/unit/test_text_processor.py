import pytest
from app.utils.text_processor import TextProcessor


def test_clean_text():
    """Test text cleaning"""
    processor = TextProcessor()
    
    dirty_text = "This   has    extra   spaces"
    clean = processor.clean_text(dirty_text)
    
    assert "  " not in clean


def test_split_into_sections():
    """Test section splitting"""
    processor = TextProcessor()
    
    text = "1. First section\n2. Second section\n3. Third section"
    sections = processor.split_into_sections(text)
    
    assert len(sections) >= 3