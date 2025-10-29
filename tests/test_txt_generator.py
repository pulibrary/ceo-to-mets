"""Tests for TXTGenerator module."""

import pytest
from pathlib import Path
from generators.txt_generator import TXTGenerator


def test_txt_generator_creates_text(sample_ceo_item, tmp_path):
    """Test that TXTGenerator creates a text file."""
    generator = TXTGenerator(sample_ceo_item)
    text = generator.text

    # Check that text is generated
    assert text is not None
    assert len(text) > 0

    # Check that key elements are present
    assert sample_ceo_item.headline in text
    assert sample_ceo_item.subhead in text

    # Test file generation
    output_path = tmp_path / "test_article.txt"
    generator.generate(output_path)

    assert output_path.exists()
    content = output_path.read_text()
    assert sample_ceo_item.headline in content


def test_txt_generator_includes_metadata(sample_ceo_item):
    """Test that TXTGenerator includes metadata."""
    generator = TXTGenerator(sample_ceo_item)
    text = generator.text

    # Check for metadata
    assert "Published:" in text
    assert "October" in text  # Date should be formatted


def test_txt_generator_includes_authors(sample_ceo_item):
    """Test that TXTGenerator includes author information."""
    generator = TXTGenerator(sample_ceo_item)
    text = generator.text

    # Check for authors
    assert "By:" in text


def test_txt_generator_strips_html(sample_ceo_item):
    """Test that TXTGenerator strips HTML tags."""
    sample_ceo_item.content = "<p>Test <strong>bold</strong> content</p>"

    generator = TXTGenerator(sample_ceo_item)
    text = generator.text

    # HTML tags should be stripped or converted
    assert "<p>" not in text
    assert "<strong>" not in text
    assert "Test" in text
    assert "bold" in text
    assert "content" in text


def test_txt_generator_cleans_escaped_html(sample_ceo_item):
    """Test that TXTGenerator cleans escaped HTML."""
    sample_ceo_item.content = "<p>Test content<\\/p><a href='link'>Link<\\/a>"

    generator = TXTGenerator(sample_ceo_item)
    text = generator.text

    # Should clean up escaped slashes
    assert "<\\/p>" not in text
    assert "<\\/a>" not in text


def test_txt_generator_includes_abstract(sample_ceo_item):
    """Test that TXTGenerator includes abstract."""
    generator = TXTGenerator(sample_ceo_item)
    text = generator.text

    # Abstract content should be present
    assert "abstract" in text.lower() or "HTML content" in text


def test_txt_generator_creates_header_underline(sample_ceo_item):
    """Test that TXTGenerator creates underline for headline."""
    generator = TXTGenerator(sample_ceo_item)
    text = generator.text

    # Should have equal signs under headline
    assert "=" * len(sample_ceo_item.headline) in text


def test_txt_generator_handles_empty_fields(sample_ceo_item):
    """Test that TXTGenerator handles empty fields gracefully."""
    sample_ceo_item.subhead = ""
    sample_ceo_item.abstract = ""

    generator = TXTGenerator(sample_ceo_item)
    text = generator.text

    # Should still generate text with headline
    assert sample_ceo_item.headline in text


def test_txt_generator_caches_text(sample_ceo_item):
    """Test that text is cached after first generation."""
    generator = TXTGenerator(sample_ceo_item)

    # Access text twice
    text1 = generator.text
    text2 = generator.text

    # Should be the same object (cached)
    assert text1 is text2


def test_txt_generator_with_string_path(sample_ceo_item, tmp_path):
    """Test that TXTGenerator works with string paths."""
    generator = TXTGenerator(sample_ceo_item)
    output_path = str(tmp_path / "test_string.txt")

    generator.generate(output_path)

    assert Path(output_path).exists()


def test_txt_generator_with_pathlib_path(sample_ceo_item, tmp_path):
    """Test that TXTGenerator works with pathlib Path objects."""
    generator = TXTGenerator(sample_ceo_item)
    output_path = tmp_path / "test_pathlib.txt"

    generator.generate(output_path)

    assert output_path.exists()


def test_txt_generator_handles_list_authors(sample_ceo_item):
    """Test that TXTGenerator handles authors as list."""
    # Authors are already in JSON string format in fixture
    generator = TXTGenerator(sample_ceo_item)
    text = generator.text

    # Should handle authors appropriately
    assert "By:" in text
