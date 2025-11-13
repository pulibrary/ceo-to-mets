"""Tests for HTMLGenerator module."""

from src.generators import HTMLGenerator


def test_html_generator_single_article(sample_ceo_item, tmp_path):
    """Test HTMLGenerator with a single article."""
    generator = HTMLGenerator()
    generator.items = [sample_ceo_item]
    generator.generate()

    # Check that HTML is generated
    assert generator.html is not None
    assert len(generator.html) > 0

    # Check that key elements are present
    assert sample_ceo_item.headline in generator.html
    assert sample_ceo_item.subhead in generator.html
    assert "Sample Article Headline" in generator.html
    assert "<!DOCTYPE html>" in generator.html
    assert "<html>" in generator.html

    # Test file generation
    output_path = tmp_path / "test_article.html"
    generator.dump(output_path)

    assert output_path.exists()
    content = output_path.read_text()
    assert sample_ceo_item.headline in content


def test_html_generator_multiple_articles(sample_ceo_items, tmp_path):
    """Test HTMLGenerator with multiple articles."""
    generator = HTMLGenerator()
    generator.items = sample_ceo_items
    generator.generate()

    # Check that HTML is generated
    assert generator.html is not None
    assert len(generator.html) > 0

    # Check that all articles are present
    for item in sample_ceo_items:
        assert item.headline in generator.html

    # Check for cover page elements
    assert "The Daily Princetonian" in generator.html
    assert "3 articles" in generator.html

    # Test file generation
    output_path = tmp_path / "test_articles.html"
    generator.dump(output_path)

    assert output_path.exists()


def test_html_generator_cleans_html_content(sample_ceo_item):
    """Test that HTMLGenerator cleans escaped HTML."""
    # Create item with escaped HTML
    sample_ceo_item.content = "<p>Test content<\\/p><a href='link'>Link<\\/a>"

    generator = HTMLGenerator()
    generator.items = [sample_ceo_item]
    generator.generate()

    # Check that escaped slashes are removed
    assert "<\\/p>" not in generator.html
    assert "<\\/a>" not in generator.html
    assert "</p>" in generator.html
    assert "</a>" in generator.html


def test_html_generator_formats_dates(sample_ceo_item):
    """Test that HTMLGenerator formats dates correctly."""

    generator = HTMLGenerator()
    generator.items = [sample_ceo_item]
    generator.generate()

    # Check that the date is formatted (not raw format)
    assert "2025-10-01 12:00:00" not in generator.html
    assert "October" in generator.html or "12:00" in generator.html


def test_html_generator_handles_flourish_charts(sample_ceo_item):
    """Test that HTMLGenerator handles Flourish chart embeds."""
    sample_ceo_item.content = """
        <figure><div class="embed-code">
        <noscript><img src="https://public.flourish.studio/visualisation/12345/thumbnail" alt="Chart">
        </noscript></div></figure>
    """

    generator = HTMLGenerator()
    generator.items = [sample_ceo_item]
    generator.generate(include_images=True)

    # Check that Flourish embed is converted to image
    assert (
        "https://public.flourish.studio/visualisation/12345/thumbnail" in generator.html
    )
    assert 'class="chart-image"' in generator.html


def test_html_generator_single_vs_multi_template(sample_ceo_item, sample_ceo_items):
    """Test that single article uses different template than multiple articles."""
    single_generator = HTMLGenerator()
    single_generator.items = [sample_ceo_item]

    multi_generator = HTMLGenerator()
    multi_generator.items = sample_ceo_items

    single_generator.generate()
    multi_generator.generate()

    single_html = single_generator.html
    multi_html = multi_generator.html

    # Single article shouldn't have cover page
    assert (
        "The Daily Princetonian" not in single_html
        or "Articles Archive" not in single_html
    )

    # Multiple articles should have cover page
    assert "The Daily Princetonian" in multi_html
    assert "Articles Archive" in multi_html


def test_html_generator_include_images_flag(sample_ceo_items):
    """Test that include_images flag is properly used."""

    generator = HTMLGenerator()
    generator.items = sample_ceo_items

    # Should generate HTML either way
    generator.generate(include_images=True)
    assert generator.html is not None

    generator.generate(include_images=False)
    assert generator.html is not None
