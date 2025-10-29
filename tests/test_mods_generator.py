"""Tests for MODSGenerator module."""

import pytest
from lxml import etree
from generators.mods_generator import MODSGenerator


def test_mods_generator_creates_element(sample_ceo_item):
    """Test that MODSGenerator creates a MODS XML element."""
    generator = MODSGenerator(sample_ceo_item)
    mods_element = generator.generate_element()

    # Check that it's an Element
    assert isinstance(mods_element, etree._Element)

    # Check that it's a MODS element
    assert "mods" in mods_element.tag


def test_mods_generator_includes_title(sample_ceo_item):
    """Test that MODSGenerator includes title information."""
    generator = MODSGenerator(sample_ceo_item)
    mods_element = generator.generate_element()

    # Convert to string to search
    xml_string = etree.tostring(mods_element, encoding="unicode")

    # Check for title elements (with namespace prefix)
    assert "title>" in xml_string  # Will match <mods:title>
    assert sample_ceo_item.headline in xml_string


def test_mods_generator_includes_subtitle(sample_ceo_item):
    """Test that MODSGenerator includes subtitle."""
    generator = MODSGenerator(sample_ceo_item)
    mods_element = generator.generate_element()

    xml_string = etree.tostring(mods_element, encoding="unicode")

    # Check for subtitle (with namespace prefix)
    assert "subTitle>" in xml_string  # Will match <mods:subTitle>
    assert sample_ceo_item.subhead in xml_string


def test_mods_generator_includes_authors(sample_ceo_item):
    """Test that MODSGenerator includes author information."""
    generator = MODSGenerator(sample_ceo_item)
    mods_element = generator.generate_element()

    xml_string = etree.tostring(mods_element, encoding="unicode")

    # Check for author elements (with namespace prefix)
    assert "name" in xml_string  # Will match <mods:name>
    assert "author" in xml_string
    assert "John Doe" in xml_string or "Jane Smith" in xml_string


def test_mods_generator_includes_publication_date(sample_ceo_item):
    """Test that MODSGenerator includes publication date."""
    generator = MODSGenerator(sample_ceo_item)
    mods_element = generator.generate_element()

    xml_string = etree.tostring(mods_element, encoding="unicode")

    # Check for date elements (with namespace prefix)
    assert "dateIssued" in xml_string  # Will match <mods:dateIssued>
    assert "2025-10-01" in xml_string


def test_mods_generator_includes_abstract(sample_ceo_item):
    """Test that MODSGenerator includes abstract."""
    generator = MODSGenerator(sample_ceo_item)
    mods_element = generator.generate_element()

    xml_string = etree.tostring(mods_element, encoding="unicode")

    # Check for abstract element (with namespace prefix)
    assert "abstract>" in xml_string  # Will match <mods:abstract>


def test_mods_generator_strips_html_from_abstract(sample_ceo_item):
    """Test that MODSGenerator strips HTML from abstract."""
    generator = MODSGenerator(sample_ceo_item)
    mods_element = generator.generate_element()

    xml_string = etree.tostring(mods_element, encoding="unicode")

    # HTML tags should be stripped from abstract
    # (abstract contains <p> tags in fixture)
    # Should not have HTML tags in MODS abstract
    abstract_start = xml_string.find("abstract>")
    abstract_end = xml_string.find("</", abstract_start)
    abstract_content = xml_string[abstract_start:abstract_end]

    # The content should exist but without HTML tags
    assert "<p>" not in abstract_content


def test_mods_generator_includes_genre(sample_ceo_item):
    """Test that MODSGenerator includes genre."""
    generator = MODSGenerator(sample_ceo_item)
    mods_element = generator.generate_element()

    xml_string = etree.tostring(mods_element, encoding="unicode")

    # Check for genre element (with namespace prefix)
    assert "genre>" in xml_string  # Will match <mods:genre>
    assert "article" in xml_string


def test_mods_generator_includes_identifier(sample_ceo_item):
    """Test that MODSGenerator includes identifier."""
    generator = MODSGenerator(sample_ceo_item)
    mods_element = generator.generate_element()

    xml_string = etree.tostring(mods_element, encoding="unicode")

    # Check for identifier element (with namespace prefix)
    assert "identifier" in xml_string  # Will match <mods:identifier>
    assert sample_ceo_item.id in xml_string


def test_mods_generator_includes_url(sample_ceo_item):
    """Test that MODSGenerator includes article URL."""
    generator = MODSGenerator(sample_ceo_item)
    mods_element = generator.generate_element()

    xml_string = etree.tostring(mods_element, encoding="unicode")

    # Check for URL element (with namespace prefix)
    assert "url>" in xml_string  # Will match <mods:url>
    assert "dailyprincetonian.com" in xml_string
    assert sample_ceo_item.slug in xml_string


def test_mods_generator_includes_subjects(sample_ceo_item):
    """Test that MODSGenerator includes subject/tag information."""
    generator = MODSGenerator(sample_ceo_item)
    mods_element = generator.generate_element()

    xml_string = etree.tostring(mods_element, encoding="unicode")

    # Check for subject elements (from tags, with namespace prefix)
    assert "subject>" in xml_string  # Will match <mods:subject>
    assert "topic>" in xml_string  # Will match <mods:topic>
    assert "News" in xml_string or "Campus" in xml_string


def test_mods_generator_to_string(sample_ceo_item):
    """Test that MODSGenerator can convert to string."""
    generator = MODSGenerator(sample_ceo_item)
    xml_string = generator.to_string()

    # Check that it's valid XML string
    assert isinstance(xml_string, str)
    assert "mods" in xml_string  # Will have mods element
    assert sample_ceo_item.headline in xml_string


def test_mods_generator_to_string_pretty_print(sample_ceo_item):
    """Test that MODSGenerator pretty prints XML."""
    generator = MODSGenerator(sample_ceo_item)
    xml_string = generator.to_string(pretty_print=True)

    # Pretty printed XML should have newlines
    assert "\n" in xml_string


def test_mods_generator_to_string_no_pretty_print(sample_ceo_item):
    """Test that MODSGenerator can skip pretty printing."""
    generator = MODSGenerator(sample_ceo_item)
    xml_string = generator.to_string(pretty_print=False)

    # Should still be valid but more compact
    assert "mods" in xml_string


def test_mods_generator_handles_missing_subtitle(sample_ceo_item):
    """Test that MODSGenerator handles missing subtitle."""
    sample_ceo_item.subhead = ""

    generator = MODSGenerator(sample_ceo_item)
    mods_element = generator.generate_element()

    xml_string = etree.tostring(mods_element, encoding="unicode")

    # Should still generate valid MODS
    assert "mods" in xml_string
    assert sample_ceo_item.headline in xml_string


def test_mods_generator_handles_missing_abstract(sample_ceo_item):
    """Test that MODSGenerator handles missing abstract."""
    sample_ceo_item.abstract = ""

    generator = MODSGenerator(sample_ceo_item)
    mods_element = generator.generate_element()

    xml_string = etree.tostring(mods_element, encoding="unicode")

    # Should still generate valid MODS without abstract
    assert "mods" in xml_string
    # Abstract element should not be present or be empty
    if "abstract>" in xml_string:
        assert "abstract></mods:abstract>" in xml_string or "abstract/>" in xml_string


def test_mods_generator_namespace(sample_ceo_item):
    """Test that MODSGenerator uses correct namespace."""
    generator = MODSGenerator(sample_ceo_item)

    # Check namespace
    assert "http://www.loc.gov/mods/v3" in generator.nsmap["mods"]

    mods_element = generator.generate_element()
    xml_string = etree.tostring(mods_element, encoding="unicode")

    # Namespace should be in the XML
    assert "http://www.loc.gov/mods/v3" in xml_string
