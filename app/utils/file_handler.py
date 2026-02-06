from typing import Optional
import PyPDF2
from docx import Document
import io


class FileHandler:
    """Handle file uploads and text extraction"""
    
    def extract_text(self, uploaded_file) -> Optional[str]:
        """
        Extract text from uploaded file
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            Extracted text or None
        """
        try:
            # Get file extension from name
            file_name = uploaded_file.name.lower()
            
            if file_name.endswith('.pdf'):
                return self._extract_from_pdf(uploaded_file)
            elif file_name.endswith('.docx'):
                return self._extract_from_docx(uploaded_file)
            elif file_name.endswith('.txt'):
                return self._extract_from_txt(uploaded_file)
            else:
                raise ValueError(f"Unsupported file type: {file_name}")
                
        except Exception as e:
            print(f"Error extracting text: {e}")
            return None
    
    def _extract_from_pdf(self, file) -> str:
        """Extract text from PDF"""
        try:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
            
        except Exception as e:
            print(f"PDF extraction error: {e}")
            return ""
    
    def _extract_from_docx(self, file) -> str:
        """Extract text from DOCX"""
        try:
            doc = Document(io.BytesIO(file.read()))
            
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
            
        except Exception as e:
            print(f"DOCX extraction error: {e}")
            return ""
    
    def _extract_from_txt(self, file) -> str:
        """Extract text from TXT"""
        try:
            # Read and decode text
            text = file.read().decode('utf-8')
            return text.strip()
            
        except Exception as e:
            print(f"TXT extraction error: {e}")
            return ""