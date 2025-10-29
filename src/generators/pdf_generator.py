from pathlib import Path
from typing import Union

from weasyprint import HTML


class PDFGenerator:
    """Generate PDF documents from HTML content."""

    def __init__(self, html_string: str) -> None:
        """
        Initialize PDF generator with HTML content.

        Args:
            html_string: HTML content to convert to PDF
        """
        self.html = html_string

    def generate(self, output_path: Union[str, Path]) -> None:
        """
        Write PDF to file.

        Args:
            output_path: Path where PDF file should be written
        """
        HTML(string=self.html).write_pdf(output_path)

