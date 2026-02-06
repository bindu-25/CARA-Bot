import re
from typing import List


class TextProcessor:
    """Text preprocessing utilities"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep legal punctuation
        text = re.sub(r'[^\w\s.,;:()\-\'"/$%]', '', text)
        
        return text.strip()
    
    @staticmethod
    def split_into_sections(text: str) -> List[str]:
        """Split contract into sections"""
        # Split by common section markers
        sections = re.split(r'\n(?=\d+\.|SECTION|ARTICLE|CLAUSE)', text)
        return [s.strip() for s in sections if s.strip()]
    
    @staticmethod
    def extract_sentences(text: str) -> List[str]:
        """Extract sentences from text"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+\s+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]
