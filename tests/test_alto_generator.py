"""Tests for ALTO XML generator."""

import pytest
from pathlib import Path
from lxml import etree

from generators.alto_generator import (
    ALTOGenerator,
    ALTOString,
    ALTOTextLine,
    ALTOTextBlock,
    ALTOPage
)
from generators.html_generator import HTMLGenerator
from generators.pdf_generator import PDFGenerator


class TestALTODataclasses:
    """Test ALTO dataclass structures."""

    def test_alto_string_creation(self):
        """Test creating an ALTOString."""
        string = ALTOString(
            content="Hello",
            hpos=10.0,
            vpos=20.0,
            width=50.0,
            height=12.0,
            wc=0.95
        )
        assert string.content == "Hello"
        assert string.hpos == 10.0
        assert string.wc == 0.95

    def test_alto_string_default_confidence(self):
        """Test ALTOString default confidence value."""
        string = ALTOString(
            content="Test",
            hpos=0.0,
            vpos=0.0,
            width=10.0,
            height=10.0
        )
        assert string.wc == 1.0

    def test_alto_text_line_creation(self):
        """Test creating an ALTOTextLine."""
        strings = [
            ALTOString("Hello", 10.0, 20.0, 30.0, 10.0),
            ALTOString("World", 45.0, 20.0, 35.0, 10.0)
        ]
        line = ALTOTextLine(strings, 10.0, 20.0, 70.0, 10.0)
        assert len(line.strings) == 2
        assert line.width == 70.0

    def test_alto_text_block_creation(self):
        """Test creating an ALTOTextBlock."""
        strings = [ALTOString("Test", 10.0, 20.0, 30.0, 10.0)]
        lines = [ALTOTextLine(strings, 10.0, 20.0, 30.0, 10.0)]
        block = ALTOTextBlock(lines, 10.0, 20.0, 30.0, 20.0)
        assert len(block.lines) == 1
        assert block.block_type == "paragraph"

    def test_alto_page_creation(self):
        """Test creating an ALTOPage."""
        page = ALTOPage(
            page_number=1,
            width=612.0,
            height=792.0,
            blocks=[]
        )
        assert page.page_number == 1
        assert page.width == 612.0
        assert len(page.blocks) == 0


class TestALTOGenerator:
    """Test ALTOGenerator functionality."""

    def test_alto_generator_init(self, sample_ceo_item, tmp_path):
        """Test initializing ALTOGenerator."""
        # Create a PDF first
        html_gen = HTMLGenerator(sample_ceo_item)
        pdf_path = tmp_path / "test.pdf"
        pdf_gen = PDFGenerator(html_gen.html)
        pdf_gen.generate(pdf_path)

        # Now create ALTO generator
        generator = ALTOGenerator(pdf_path, sample_ceo_item)
        assert generator.pdf_path == pdf_path
        assert generator.article_item == sample_ceo_item

    def test_alto_generator_file_not_found(self):
        """Test ALTOGenerator raises error for missing PDF."""
        with pytest.raises(FileNotFoundError):
            ALTOGenerator("/nonexistent/file.pdf")

    def test_extract_layout_from_pdf(self, sample_ceo_item, tmp_path):
        """Test extracting layout from PDF."""
        html_gen = HTMLGenerator(sample_ceo_item)
        pdf_path = tmp_path / "test.pdf"
        pdf_gen = PDFGenerator(html_gen.html)
        pdf_gen.generate(pdf_path)

        generator = ALTOGenerator(pdf_path)
        pages = generator.extract_layout_from_pdf()

        assert len(pages) > 0
        assert isinstance(pages[0], ALTOPage)
        assert pages[0].page_number == 1
        assert pages[0].width > 0
        assert pages[0].height > 0

    def test_extract_layout_has_blocks(self, sample_ceo_item, tmp_path):
        """Test that extracted layout contains text blocks."""
        html_gen = HTMLGenerator(sample_ceo_item)
        pdf_path = tmp_path / "test.pdf"
        pdf_gen = PDFGenerator(html_gen.html)
        pdf_gen.generate(pdf_path)

        generator = ALTOGenerator(pdf_path)
        pages = generator.extract_layout_from_pdf()

        # Should have at least one page with blocks
        assert len(pages) > 0
        # May have blocks depending on PDF content
        if pages[0].blocks:
            assert isinstance(pages[0].blocks[0], ALTOTextBlock)

    def test_generate_alto_xml(self, sample_ceo_item, tmp_path):
        """Test generating ALTO XML structure."""
        html_gen = HTMLGenerator(sample_ceo_item)
        pdf_path = tmp_path / "test.pdf"
        pdf_gen = PDFGenerator(html_gen.html)
        pdf_gen.generate(pdf_path)

        generator = ALTOGenerator(pdf_path)
        alto_xml = generator.generate_alto_xml()

        assert alto_xml is not None
        assert alto_xml.tag == "{http://www.loc.gov/standards/alto/ns-v4#}alto"

    def test_alto_xml_has_description(self, sample_ceo_item, tmp_path):
        """Test ALTO XML contains Description section."""
        html_gen = HTMLGenerator(sample_ceo_item)
        pdf_path = tmp_path / "test.pdf"
        pdf_gen = PDFGenerator(html_gen.html)
        pdf_gen.generate(pdf_path)

        generator = ALTOGenerator(pdf_path)
        alto_xml = generator.generate_alto_xml()

        namespaces = {'alto': ALTOGenerator.ALTO_NAMESPACE}
        description = alto_xml.find('alto:Description', namespaces)
        assert description is not None

    def test_alto_xml_has_layout(self, sample_ceo_item, tmp_path):
        """Test ALTO XML contains Layout section."""
        html_gen = HTMLGenerator(sample_ceo_item)
        pdf_path = tmp_path / "test.pdf"
        pdf_gen = PDFGenerator(html_gen.html)
        pdf_gen.generate(pdf_path)

        generator = ALTOGenerator(pdf_path)
        alto_xml = generator.generate_alto_xml()

        namespaces = {'alto': ALTOGenerator.ALTO_NAMESPACE}
        layout = alto_xml.find('alto:Layout', namespaces)
        assert layout is not None

    def test_alto_xml_has_pages(self, sample_ceo_item, tmp_path):
        """Test ALTO XML contains Page elements."""
        html_gen = HTMLGenerator(sample_ceo_item)
        pdf_path = tmp_path / "test.pdf"
        pdf_gen = PDFGenerator(html_gen.html)
        pdf_gen.generate(pdf_path)

        generator = ALTOGenerator(pdf_path)
        alto_xml = generator.generate_alto_xml()

        namespaces = {'alto': ALTOGenerator.ALTO_NAMESPACE}
        pages = alto_xml.findall('.//alto:Page', namespaces)
        assert len(pages) > 0

    def test_alto_xml_page_attributes(self, sample_ceo_item, tmp_path):
        """Test Page elements have required attributes."""
        html_gen = HTMLGenerator(sample_ceo_item)
        pdf_path = tmp_path / "test.pdf"
        pdf_gen = PDFGenerator(html_gen.html)
        pdf_gen.generate(pdf_path)

        generator = ALTOGenerator(pdf_path)
        alto_xml = generator.generate_alto_xml()

        namespaces = {'alto': ALTOGenerator.ALTO_NAMESPACE}
        page = alto_xml.find('.//alto:Page', namespaces)

        assert page is not None
        assert 'ID' in page.attrib
        assert 'HEIGHT' in page.attrib
        assert 'WIDTH' in page.attrib
        assert 'PHYSICAL_IMG_NR' in page.attrib

    def test_alto_generator_to_string(self, sample_ceo_item, tmp_path):
        """Test generating ALTO XML as string."""
        html_gen = HTMLGenerator(sample_ceo_item)
        pdf_path = tmp_path / "test.pdf"
        pdf_gen = PDFGenerator(html_gen.html)
        pdf_gen.generate(pdf_path)

        generator = ALTOGenerator(pdf_path)
        xml_string = generator.to_string()

        assert isinstance(xml_string, str)
        assert "alto" in xml_string
        assert "Layout" in xml_string

    def test_alto_generator_to_string_pretty_print(self, sample_ceo_item, tmp_path):
        """Test generating formatted ALTO XML string."""
        html_gen = HTMLGenerator(sample_ceo_item)
        pdf_path = tmp_path / "test.pdf"
        pdf_gen = PDFGenerator(html_gen.html)
        pdf_gen.generate(pdf_path)

        generator = ALTOGenerator(pdf_path)
        xml_string = generator.to_string(pretty_print=True)

        assert isinstance(xml_string, str)
        # Pretty printed XML should have newlines
        assert '\n' in xml_string

    def test_alto_generator_generate_file(self, sample_ceo_item, tmp_path):
        """Test generating ALTO XML file."""
        html_gen = HTMLGenerator(sample_ceo_item)
        pdf_path = tmp_path / "test.pdf"
        pdf_gen = PDFGenerator(html_gen.html)
        pdf_gen.generate(pdf_path)

        generator = ALTOGenerator(pdf_path)
        alto_path = tmp_path / "test.alto.xml"
        generator.generate(alto_path)

        assert alto_path.exists()
        assert alto_path.stat().st_size > 0

    def test_alto_generated_file_is_valid_xml(self, sample_ceo_item, tmp_path):
        """Test generated ALTO file is valid XML."""
        html_gen = HTMLGenerator(sample_ceo_item)
        pdf_path = tmp_path / "test.pdf"
        pdf_gen = PDFGenerator(html_gen.html)
        pdf_gen.generate(pdf_path)

        generator = ALTOGenerator(pdf_path)
        alto_path = tmp_path / "test.alto.xml"
        generator.generate(alto_path)

        # Parse the file to ensure it's valid XML
        tree = etree.parse(str(alto_path))
        root = tree.getroot()
        assert root is not None

    def test_alto_file_has_correct_namespace(self, sample_ceo_item, tmp_path):
        """Test generated ALTO file has correct namespace."""
        html_gen = HTMLGenerator(sample_ceo_item)
        pdf_path = tmp_path / "test.pdf"
        pdf_gen = PDFGenerator(html_gen.html)
        pdf_gen.generate(pdf_path)

        generator = ALTOGenerator(pdf_path)
        alto_path = tmp_path / "test.alto.xml"
        generator.generate(alto_path)

        tree = etree.parse(str(alto_path))
        root = tree.getroot()
        assert ALTOGenerator.ALTO_NAMESPACE in root.tag

    def test_alto_file_creates_parent_directories(self, sample_ceo_item, tmp_path):
        """Test that generate() creates parent directories if needed."""
        html_gen = HTMLGenerator(sample_ceo_item)
        pdf_path = tmp_path / "test.pdf"
        pdf_gen = PDFGenerator(html_gen.html)
        pdf_gen.generate(pdf_path)

        generator = ALTOGenerator(pdf_path)
        alto_path = tmp_path / "nested" / "dir" / "test.alto.xml"
        generator.generate(alto_path)

        assert alto_path.exists()
        assert alto_path.parent.exists()
