"""
Source processing services for KnowBook.

Each processor handles a specific file type:
- text_processor: Plain text files (.txt, .md)
- docx_processor: Word documents (.docx)
- pdf_processor: PDF documents (.pdf)
- pptx_processor: PowerPoint presentations (.pptx)
- image_processor: Images (.png, .jpg, etc.)
- audio_processor: Audio files (.mp3, .wav, etc.)
- csv_processor: CSV data files (.csv)
- link_processor: Web URLs and YouTube links (.link)
- youtube_processor: YouTube video transcripts
- research_processor: AI-powered research documents (.research)
"""

from app.services.source_processing.text_processor import process_text
from app.services.source_processing.docx_processor import process_docx
from app.services.source_processing.youtube_processor import process_youtube

__all__ = [
    'process_text',
    'process_docx',
    'process_youtube',
]
