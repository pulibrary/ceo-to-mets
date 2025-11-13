"""Tests for PDFGenerator module."""

import pytest
from pathlib import Path
from generators.pdf_generator import PDFGenerator


def test_pdf_generator_creates_pdf(tmp_path):
    """Test that PDFGenerator creates a PDF file."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head><title>Test PDF</title></head>
    <body>
        <h1>Test PDF Content</h1>
        <p>This is a test paragraph.</p>
    </body>
    </html>
    """

    generator = PDFGenerator(html_content)
    output_path = tmp_path / "test_output.pdf"

    generator.dump(output_path)

    # Check that PDF file was created
    assert output_path.exists()
    assert output_path.stat().st_size > 0

    # Check that it's a PDF file (starts with PDF magic number)
    with open(output_path, "rb") as f:
        header = f.read(4)
        assert header == b"%PDF"


def test_pdf_generator_with_string_path(tmp_path):
    """Test that PDFGenerator works with string paths."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head><title>Test</title></head>
    <body><p>Test content</p></body>
    </html>
    """

    generator = PDFGenerator(html_content)
    output_path = str(tmp_path / "test_string_path.pdf")

    generator.dump(output_path)

    assert Path(output_path).exists()


def test_pdf_generator_with_pathlib_path(tmp_path):
    """Test that PDFGenerator works with pathlib Path objects."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head><title>Test</title></head>
    <body><p>Test content</p></body>
    </html>
    """

    generator = PDFGenerator(html_content)
    output_path = tmp_path / "test_pathlib.pdf"

    generator.dump(output_path)

    assert output_path.exists()


def test_pdf_generator_with_complex_html(tmp_path):
    """Test PDFGenerator with complex HTML content."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Complex Test PDF</title>
        <style>
            body { font-family: Georgia, serif; }
            h1 { color: #333; }
            .abstract {
                font-style: italic;
                padding: 10px;
                background: #f5f5f5;
            }
        </style>
    </head>
    <body>
        <h1>Article Title</h1>
        <div class="abstract">
            This is an abstract with <strong>bold text</strong>.
        </div>
        <p>This is a paragraph with a <a href="http://example.com">link</a>.</p>
        <ul>
            <li>List item 1</li>
            <li>List item 2</li>
        </ul>
    </body>
    </html>
    """

    generator = PDFGenerator(html_content)
    output_path = tmp_path / "test_complex.pdf"

    generator.dump(output_path)

    assert output_path.exists()
    # Complex HTML should still produce a valid PDF
    assert output_path.stat().st_size > 1000  # Should be reasonably sized


def test_pdf_generator_stores_html(tmp_path):
    """Test that PDFGenerator stores the HTML content."""
    html_content = "<html><body><p>Test</p></body></html>"

    generator = PDFGenerator(html_content)

    assert generator.html == html_content


def test_pdf_generator_minimal_html(tmp_path):
    """Test PDFGenerator with minimal HTML."""
    html_content = "<html><body>Minimal</body></html>"

    generator = PDFGenerator(html_content)
    output_path = tmp_path / "minimal.pdf"

    generator.dump(output_path)

    assert output_path.exists()
