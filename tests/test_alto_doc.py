"""Tests for ALTO XML generator."""

from pathlib import Path

import pytest
from lxml import etree

from generators.alto_generator import (
    ALTOGenerator,
    ALTODoc,
    ALTOPage,
    ALTOString,
    ALTOTextBlock,
    ALTOTextLine,
)


@pytest.fixture
def generator_fixture(test_pdf_path):
    generator = ALTOGenerator()
    generator.pdf_path = test_pdf_path
    generator.generate()
    return generator

@pytest.fixture
def alto_page_fixture(generator_fixture):
    return generator_fixture.pages[0]

@pytest.fixture
def ALTODoc_fixture(alto_page_fixture):
    return ALTODoc(alto_page_fixture)



class TestALTODoc:
    """Test ALTODoc functionality."""


    def test_alto_xml_has_description(self, ALTODoc_fixture):
        """Test ALTO XML contains Description section."""

        alto_xml = ALTODoc_fixture.xml

        namespaces = {"alto": ALTOGenerator.ALTO_NAMESPACE}
        description = alto_xml.find("alto:Description", namespaces)
        assert description is not None

    def test_alto_xml_has_layout(self, ALTODoc_fixture):
        """Test ALTO XML contains Layout section."""

        alto_xml = ALTODoc_fixture.xml
        namespaces = {"alto": ALTOGenerator.ALTO_NAMESPACE}
        layout = alto_xml.find("alto:Layout", namespaces)

        assert layout is not None


    def test_alto_xml_page_attributes(self, ALTODoc_fixture):
        """Test Page elements have required attributes."""

        alto_xml = ALTODoc_fixture.xml
        namespaces = {"alto": ALTOGenerator.ALTO_NAMESPACE}
        page = alto_xml.find(".//alto:Page", namespaces)

        assert page is not None
        assert "ID" in page.attrib
        assert "HEIGHT" in page.attrib
        assert "WIDTH" in page.attrib
        assert "PHYSICAL_IMG_NR" in page.attrib
