import json
from datetime import datetime
from pathlib import Path
from typing import Union

import html2text

from clients import CeoItem

from .generator import Generator


class TXTGenerator(Generator):
    """Generate plain text documents from article data."""

    def __init__(self) -> None:
        """
        Initialize TXT generator with article data.

        Args:
            item: CeoItem containing article data
        """
        self.item: CeoItem | None = None
        self._text = None

    def _clean_content(self, content: str) -> str:
        """Clean up HTML content for text extraction."""
        return super()._clean_html_content(content)

    def generate(self) -> str:
        """Generate plain text content from the article."""
        if self.item is not None:
            if self._text is None:
                h = html2text.HTML2Text()
                h.ignore_links = False
                h.ignore_images = True
                h.ignore_emphasis = False
                h.body_width = 0  # Don't wrap lines

                # Build text content
                parts = []

                # Header
                if self.item.headline is not None:
                    parts.append(self.item.headline)
                    parts.append("=" * len(self.item.headline))
                    parts.append("")

                if self.item.subhead:
                    parts.append(self.item.subhead)
                    parts.append("")

                # Metadata
                if self.item.published_at:
                    try:
                        dt = datetime.strptime(
                            self.item.published_at, "%Y-%m-%d %H:%M:%S"
                        )
                        parts.append(
                            f"Published: {dt.strftime('%B %d, %Y at %I:%M %p')}"
                        )
                    except ValueError:
                        parts.append(f"Published: {self.item.published_at}")

                if self.item.authors:
                    # Handle authors whether it's a JSON string or list
                    authors = self.item.authors
                    if isinstance(authors, str):
                        # Try to parse JSON string
                        try:
                            authors = json.loads(authors)
                            author_names = [
                                a["name"] if isinstance(a, dict) else str(a)
                                for a in authors
                            ]
                            parts.append(f"By: {', '.join(author_names)}")
                        except (json.JSONDecodeError, ValueError):
                            # If parsing fails, use as plain string
                            parts.append(f"By: {authors}")
                    else:
                        author_names = [
                            a["name"] if isinstance(a, dict) else str(a)
                            for a in authors
                        ]
                        parts.append(f"By: {', '.join(author_names)}")

                parts.append("")

                # Abstract
                if self.item.abstract:
                    parts.append(h.handle(self.item.abstract))
                    parts.append("")

                # Content
                if self.item.content:
                    parts.append(h.handle(self._clean_content(self.item.content)))

                self._text = "\n".join(parts)

    @property
    def text(self):
        if self._text is None:
            self.generate()
        return self._text

    def dump(self, output_path: Union[str, Path]) -> None:
        """
        Write plain text content to file.

        Args:
            output_path: Path where text file should be written
        """
        if self.text:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(self.text)
