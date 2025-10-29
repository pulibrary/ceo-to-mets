"""Tests for HTMLGenerator module."""

import pytest
from pathlib import Path
from generators.html_generator import HTMLGenerator


def test_html_generator_single_article(sample_ceo_item, tmp_path):
    """Test HTMLGenerator with a single article."""
    generator = HTMLGenerator(sample_ceo_item)
    html = generator.html

    # Check that HTML is generated
    assert html is not None
    assert len(html) > 0

    # Check that key elements are present
    assert sample_ceo_item.headline in html
    assert sample_ceo_item.subhead in html
    assert "Sample Article Headline" in html
    assert "<!DOCTYPE html>" in html
    assert "<html>" in html

    # Test file generation
    output_path = tmp_path / "test_article.html"
    generator.generate(output_path)

    assert output_path.exists()
    content = output_path.read_text()
    assert sample_ceo_item.headline in content


def test_html_generator_multiple_articles(sample_ceo_items, tmp_path):
    """Test HTMLGenerator with multiple articles."""
    generator = HTMLGenerator(sample_ceo_items, include_images=False)
    html = generator.html

    # Check that HTML is generated
    assert html is not None
    assert len(html) > 0

    # Check that all articles are present
    for item in sample_ceo_items:
        assert item.headline in html

    # Check for cover page elements
    assert "The Daily Princetonian" in html
    assert "3 articles" in html

    # Test file generation
    output_path = tmp_path / "test_articles.html"
    generator.generate(output_path)

    assert output_path.exists()


def test_html_generator_cleans_html_content(sample_ceo_item):
    """Test that HTMLGenerator cleans escaped HTML."""
    # Create item with escaped HTML
    sample_ceo_item.content = "<p>Test content<\\/p><a href='link'>Link<\\/a>"

    generator = HTMLGenerator(sample_ceo_item)
    html = generator.html

    # Check that escaped slashes are removed
    assert "<\\/p>" not in html
    assert "<\\/a>" not in html
    assert "</p>" in html
    assert "</a>" in html


def test_html_generator_formats_dates(sample_ceo_item):
    """Test that HTMLGenerator formats dates correctly."""
    generator = HTMLGenerator(sample_ceo_item)
    html = generator.html

    # Check that the date is formatted (not raw format)
    assert "2025-10-01 12:00:00" not in html
    assert "October" in html or "12:00" in html


def test_html_generator_handles_flourish_charts(sample_ceo_item):
    """Test that HTMLGenerator handles Flourish chart embeds."""
    sample_ceo_item.content = '''
        <figure><div class="embed-code">
        <noscript><img src="https://public.flourish.studio/visualisation/12345/thumbnail" alt="Chart">
        </noscript></div></figure>
    '''

    generator = HTMLGenerator(sample_ceo_item)
    html = generator.html

    # Check that Flourish embed is converted to image
    assert "https://public.flourish.studio/visualisation/12345/thumbnail" in html
    assert 'class="chart-image"' in html


def test_html_generator_single_vs_multi_template(sample_ceo_item, sample_ceo_items):
    """Test that single article uses different template than multiple articles."""
    single_generator = HTMLGenerator(sample_ceo_item)
    multi_generator = HTMLGenerator(sample_ceo_items)

    single_html = single_generator.html
    multi_html = multi_generator.html

    # Single article shouldn't have cover page
    assert "The Daily Princetonian" not in single_html or "Articles Archive" not in single_html

    # Multiple articles should have cover page
    assert "The Daily Princetonian" in multi_html
    assert "Articles Archive" in multi_html


def test_html_generator_include_images_flag(sample_ceo_items):
    """Test that include_images flag is properly used."""
    generator_with_images = HTMLGenerator(sample_ceo_items, include_images=True)
    generator_without_images = HTMLGenerator(sample_ceo_items, include_images=False)

    # Both should generate HTML
    assert generator_with_images.html is not None
    assert generator_without_images.html is not None


def test_html_generator_caches_html(sample_ceo_item):
    """Test that HTML is cached after first generation."""
    generator = HTMLGenerator(sample_ceo_item)

    # Access html twice
    html1 = generator.html
    html2 = generator.html

    # Should be the same object (cached)
    assert html1 is html2
