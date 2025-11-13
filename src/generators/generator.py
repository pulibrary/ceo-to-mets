import abc
from pathlib import Path
from typing import Union


class Generator(abc.ABC):
    @abc.abstractmethod
    def generate(self) -> None: ...

    @abc.abstractmethod
    def dump(self, output_path: Union[str, Path]) -> None: ...

    def _clean_html_content(self, html_content: str) -> str:
        """Clean up HTML content for text extraction."""
        if not html_content:
            return ""

        # The API returns HTML with escaped slashes in closing tags
        html_content = html_content.replace("<\\/p>", "</p>")
        html_content = html_content.replace("<\\/a>", "</a>")
        html_content = html_content.replace("<\\/h5>", "</h5>")
        html_content = html_content.replace("<\\/h6>", "</h6>")
        html_content = html_content.replace("<\\/i>", "</i>")
        html_content = html_content.replace("<\\/script>", "</script>")
        html_content = html_content.replace("<\\/div>", "</div>")
        html_content = html_content.replace("<\\/figure>", "</figure>")
        html_content = html_content.replace("<\\/noscript>", "</noscript>")

        return html_content
