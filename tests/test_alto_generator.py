"""Tests for ALTOGenerator module."""

import pytest
from pathlib import Path
from lxml import etree
from generators.alto_generator import ALTOGenerator
from generators.html_generator import HTMLGenerator
from generators.pdf_generator import PDFGenerator


def test_alto_generator_initialization(sample_ceo_item, tmp_path):
    """Test that ALTOGenerator initializes correctly."""
    # First create a PDF
    html_gen = HTMLGenerator(sample_ceo_item)
    pdf_path = tmp_path / "test.pdf"
    pdf_gen = PDFGenerator(html_gen.html)
    pdf_gen.generate(pdf_path)

    # Initialize ALTO generator
    generator = ALTOGenerator(pdf_path, sample_ceo_item)

    assert generator.pdf_path == pdf_path
    assert generator.article_item == sample_ceo_item
    assert generator.ALTO_NAMESPACE == "http://www.loc.gov/standards/alto/ns-v4#"


def test_alto_generator_extracts_layout(sample_ceo_item, tmp_path):
    """Test that ALTOGenerator extracts layout from PDF."""
    # Create a PDF
    html_gen = HTMLGenerator(sample_ceo_item)
    pdf_path = tmp_path / "test.pdf"
    pdf_gen = PDFGenerator(html_gen.html)
    pdf_gen.generate(pdf_path)

    # Extract layout
    generator = ALTOGenerator(pdf_path)
    pages = generator.extract_layout_from_pdf()

    # Should have at least one page
    assert len(pages) > 0

    # First page should have dimensions
    page = pages[0]
    assert page.width > 0
    assert page.height > 0
    assert page.page_number == 1

    # Should have text blocks
    assert len(page.blocks) > 0


def test_alto_generator_creates_xml(sample_ceo_item, tmp_path):
    """Test that ALTOGenerator creates valid ALTO XML."""
    # Create a PDF
    html_gen = HTMLGenerator(sample_ceo_item)
    pdf_path = tmp_path / "test.pdf"
    pdf_gen = PDFGenerator(html_gen.html)
    pdf_gen.generate(pdf_path)

    # Generate ALTO XML
    generator = ALTOGenerator(pdf_path)
    alto_xml = generator.generate_alto_xml()

    # Check that it's an Element
    assert isinstance(alto_xml, etree._Element)

    # Check namespace
    assert "alto" in alto_xml.tag


def test_alto_generator_includes_description(sample_ceo_item, tmp_path):
    """Test that ALTO XML includes Description section."""
    html_gen = HTMLGenerator(sample_ceo_item)
    pdf_path = tmp_path / "test.pdf"
    pdf_gen = PDFGenerator(html_gen.html)
    pdf_gen.generate(pdf_path)

    generator = ALTOGenerator(pdf_path)
    alto_xml = generator.generate_alto_xml()
    xml_string = etree.tostring(alto_xml, encoding="unicode")

    # Check for Description elements
    assert "Description>" in xml_string
    assert "MeasurementUnit>" in xml_string
    assert "pixel" in xml_string
    assert "Processing" in xml_string


def test_alto_generator_includes_layout(sample_ceo_item, tmp_path):
    """Test that ALTO XML includes Layout section."""
    html_gen = HTMLGenerator(sample_ceo_item)
    pdf_path = tmp_path / "test.pdf"
    pdf_gen = PDFGenerator(html_gen.html)
    pdf_gen.generate(pdf_path)

    generator = ALTOGenerator(pdf_path)
    alto_xml = generator.generate_alto_xml()
    xml_string = etree.tostring(alto_xml, encoding="unicode")

    # Check for Layout elements
    assert "Layout>" in xml_string
    assert "Page" in xml_string
    assert "PrintSpace>" in xml_string


def test_alto_generator_includes_text_blocks(sample_ceo_item, tmp_path):
    """Test that ALTO XML includes TextBlock elements."""
    html_gen = HTMLGenerator(sample_ceo_item)
    pdf_path = tmp_path / "test.pdf"
    pdf_gen = PDFGenerator(html_gen.html)
    pdf_gen.generate(pdf_path)

    generator = ALTOGenerator(pdf_path)
    alto_xml = generator.generate_alto_xml()
    xml_string = etree.tostring(alto_xml, encoding="unicode")

    # Check for TextBlock elements
    assert "TextBlock" in xml_string
    assert "HPOS=" in xml_string
    assert "VPOS=" in xml_string
    assert "WIDTH=" in xml_string
    assert "HEIGHT=" in xml_string


def test_alto_generator_includes_text_lines(sample_ceo_item, tmp_path):
    """Test that ALTO XML includes TextLine elements."""
    html_gen = HTMLGenerator(sample_ceo_item)
    pdf_path = tmp_path / "test.pdf"
    pdf_gen = PDFGenerator(html_gen.html)
    pdf_gen.generate(pdf_path)

    generator = ALTOGenerator(pdf_path)
    alto_xml = generator.generate_alto_xml()
    xml_string = etree.tostring(alto_xml, encoding="unicode")

    # Check for TextLine elements
    assert "TextLine" in xml_string


def test_alto_generator_includes_strings(sample_ceo_item, tmp_path):
    """Test that ALTO XML includes String elements (words)."""
    html_gen = HTMLGenerator(sample_ceo_item)
    pdf_path = tmp_path / "test.pdf"
    pdf_gen = PDFGenerator(html_gen.html)
    pdf_gen.generate(pdf_path)

    generator = ALTOGenerator(pdf_path)
    alto_xml = generator.generate_alto_xml()
    xml_string = etree.tostring(alto_xml, encoding="unicode")

    # Check for String elements with CONTENT
    assert "String" in xml_string
    assert "CONTENT=" in xml_string
    assert "WC=" in xml_string  # word confidence


def test_alto_generator_extracts_headline_text(sample_ceo_item, tmp_path):
    """Test that ALTO extracts actual text from PDF."""
    html_gen = HTMLGenerator(sample_ceo_item)
    pdf_path = tmp_path / "test.pdf"
    pdf_gen = PDFGenerator(html_gen.html)
    pdf_gen.generate(pdf_path)

    generator = ALTOGenerator(pdf_path)
    pages = generator.extract_layout_from_pdf()

    # Collect all text content
    all_text = []
    for page in pages:
        for block in page.blocks:
            for line in block.lines:
                for string in line.strings:
                    all_text.append(string.content)

    # Should contain some words from the headline
    all_text_combined = " ".join(all_text)
    headline_words = sample_ceo_item.headline.split()

    # At least some headline words should be present
    matches = sum(1 for word in headline_words if word in all_text_combined)
    assert matches > 0


def test_alto_generator_generates_file(sample_ceo_item, tmp_path):
    """Test that ALTOGenerator writes to file."""
    html_gen = HTMLGenerator(sample_ceo_item)
    pdf_path = tmp_path / "test.pdf"
    pdf_gen = PDFGenerator(html_gen.html)
    pdf_gen.generate(pdf_path)

    generator = ALTOGenerator(pdf_path)
    alto_path = tmp_path / "test.alto.xml"
    generator.generate(alto_path)

    # File should exist
    assert alto_path.exists()

    # Should be valid XML
    tree = etree.parse(str(alto_path))
    root = tree.getroot()
    assert "alto" in root.tag


def test_alto_generator_to_string(sample_ceo_item, tmp_path):
    """Test that ALTOGenerator can convert to string."""
    html_gen = HTMLGenerator(sample_ceo_item)
    pdf_path = tmp_path / "test.pdf"
    pdf_gen = PDFGenerator(html_gen.html)
    pdf_gen.generate(pdf_path)

    generator = ALTOGenerator(pdf_path)
    xml_string = generator.to_string()

    # Should be a string
    assert isinstance(xml_string, str)

    # Should have XML declaration
    assert "<?xml" in xml_string

    # Should have ALTO elements
    assert "alto" in xml_string
    assert "Layout" in xml_string


def test_alto_generator_to_string_pretty_print(sample_ceo_item, tmp_path):
    """Test pretty printing option."""
    html_gen = HTMLGenerator(sample_ceo_item)
    pdf_path = tmp_path / "test.pdf"
    pdf_gen = PDFGenerator(html_gen.html)
    pdf_gen.generate(pdf_path)

    generator = ALTOGenerator(pdf_path)
    xml_string = generator.to_string(pretty_print=True)

    # Pretty printed should have newlines
    assert "\n" in xml_string


def test_alto_generator_with_string_path(sample_ceo_item, tmp_path):
    """Test that ALTOGenerator works with string paths."""
    html_gen = HTMLGenerator(sample_ceo_item)
    pdf_path = tmp_path / "test.pdf"
    pdf_gen = PDFGenerator(html_gen.html)
    pdf_gen.generate(pdf_path)

    # Use string path
    generator = ALTOGenerator(str(pdf_path))
    alto_path = str(tmp_path / "test.alto.xml")
    generator.generate(alto_path)

    assert Path(alto_path).exists()


def test_alto_generator_with_pathlib_path(sample_ceo_item, tmp_path):
    """Test that ALTOGenerator works with pathlib Path objects."""
    html_gen = HTMLGenerator(sample_ceo_item)
    pdf_path = tmp_path / "test.pdf"
    pdf_gen = PDFGenerator(html_gen.html)
    pdf_gen.generate(pdf_path)

    # Use Path object
    generator = ALTOGenerator(pdf_path)
    alto_path = tmp_path / "test.alto.xml"
    generator.generate(alto_path)

    assert alto_path.exists()


def test_alto_generator_has_page_dimensions(sample_ceo_item, tmp_path):
    """Test that ALTO includes page dimensions."""
    html_gen = HTMLGenerator(sample_ceo_item)
    pdf_path = tmp_path / "test.pdf"
    pdf_gen = PDFGenerator(html_gen.html)
    pdf_gen.generate(pdf_path)

    generator = ALTOGenerator(pdf_path)
    alto_xml = generator.generate_alto_xml()
    xml_string = etree.tostring(alto_xml, encoding="unicode")

    # Should have WIDTH and HEIGHT attributes
    assert 'WIDTH="' in xml_string
    assert 'HEIGHT="' in xml_string


def test_alto_generator_has_processing_metadata(sample_ceo_item, tmp_path):
    """Test that ALTO includes processing metadata."""
    html_gen = HTMLGenerator(sample_ceo_item)
    pdf_path = tmp_path / "test.pdf"
    pdf_gen = PDFGenerator(html_gen.html)
    pdf_gen.generate(pdf_path)

    generator = ALTOGenerator(pdf_path)
    alto_xml = generator.generate_alto_xml()
    xml_string = etree.tostring(alto_xml, encoding="unicode")

    # Should have processing information
    assert "processingDateTime" in xml_string
    assert "processingSoftware" in xml_string
    assert "ALTOGenerator" in xml_string
    assert "PyMuPDF" in xml_string
