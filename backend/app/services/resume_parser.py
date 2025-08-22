"""
Resume Parser Service

This module handles parsing of resume files (PDF and DOCX) to extract text content.
"""

import io
import logging
from typing import Optional
from docx import Document
from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)


class ResumeParser:
    """Handles parsing of resume files to extract text content."""
    
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> str:
        """
        Extract text from PDF file content.
        
        Args:
            file_content: Raw bytes of the PDF file
            
        Returns:
            Extracted text as string
            
        Raises:
            Exception: If PDF parsing fails
        """
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            logger.error(f"Error parsing PDF: {str(e)}")
            raise Exception(f"Failed to parse PDF file: {str(e)}")
    
    @staticmethod
    def extract_text_from_docx(file_content: bytes) -> str:
        """
        Extract text from DOCX file content.
        
        Args:
            file_content: Raw bytes of the DOCX file
            
        Returns:
            Extracted text as string
            
        Raises:
            Exception: If DOCX parsing fails
        """
        try:
            docx_file = io.BytesIO(file_content)
            doc = Document(docx_file)
            
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
        except Exception as e:
            logger.error(f"Error parsing DOCX: {str(e)}")
            raise Exception(f"Failed to parse DOCX file: {str(e)}")
    
    @staticmethod
    def parse_resume(file_content: bytes, filename: str) -> str:
        """
        Parse resume file and extract text based on file extension.
        
        Args:
            file_content: Raw bytes of the file
            filename: Name of the file (used to determine file type)
            
        Returns:
            Extracted text as string
            
        Raises:
            Exception: If file type is unsupported or parsing fails
        """
        filename_lower = filename.lower()
        
        if filename_lower.endswith('.pdf'):
            return ResumeParser.extract_text_from_pdf(file_content)
        elif filename_lower.endswith('.docx'):
            return ResumeParser.extract_text_from_docx(file_content)
        else:
            raise Exception(f"Unsupported file type. Please upload a PDF or DOCX file.")
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace and normalize line breaks
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)

