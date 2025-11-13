from pathlib import Path
from typing import Union

from weasyprint import HTML

from .generator import Generator


class PDFGenerator(Generator):
    """Generate PDF documents from HTML content."""

    def __init__(self, html_string: str) -> None:
        """
        Initialize PDF generator with HTML content.

        Args:
            html_string: HTML content to convert to PDF
        """
        self.html = html_string

    def generate(self) -> None:
        """
        Generate PDF from HTML content.
        This is a no-op as PDF generation happens on demand during dump().
        """
        pass

    def dump(self, output_path: Union[str, Path]) -> None:
        """
        Write PDF to file.

        Args:
            output_path: Path where PDF file should be written
        """
        HTML(string=self.html).write_pdf(output_path)
