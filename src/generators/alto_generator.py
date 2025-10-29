"""
ALTO XML Generator for newspaper articles.

Generates ALTO (Analyzed Layout and Text Object) XML from PDF files.
ALTO is a standard format for describing the layout and content of scanned or
generated documents, commonly used in digital library workflows.

This implementation extracts text and coordinate information from PDFs generated
by WeasyPrint and creates ALTO v4 compliant XML.
"""

from datetime import datetime
from pathlib import Path
from typing import Union, Optional, List, Dict, Any
from dataclasses import dataclass

import fitz  # PyMuPDF
from lxml import etree

from clients import CeoItem


@dataclass
class ALTOString:
    """Represents a word/string in ALTO."""
    content: str
    hpos: float
    vpos: float
    width: float
    height: float
    wc: float = 1.0  # word confidence (0-1)


@dataclass
class ALTOTextLine:
    """Represents a line of text in ALTO."""
    strings: List[ALTOString]
    hpos: float
    vpos: float
    width: float
    height: float


@dataclass
class ALTOTextBlock:
    """Represents a block of text in ALTO."""
    lines: List[ALTOTextLine]
    hpos: float
    vpos: float
    width: float
    height: float
    block_type: str = "paragraph"  # paragraph, heading, etc.


@dataclass
class ALTOPage:
    """Represents a page in ALTO."""
    page_number: int
    width: float
    height: float
    blocks: List[ALTOTextBlock]


class ALTOGenerator:
    """
    Generate ALTO XML from PDF files.

    ALTO (Analyzed Layout and Text Object) is an XML schema for describing
    the layout and content of physical text resources, such as pages of a book
    or newspaper. It's commonly used in digital library workflows.

    This generator extracts text with coordinate information from PDFs and
    creates ALTO v4 compliant XML.
    """

    ALTO_NAMESPACE = "http://www.loc.gov/standards/alto/ns-v4#"
    ALTO_VERSION = "4.4"

    def __init__(
        self,
        pdf_path: Union[str, Path],
        article_item: Optional[CeoItem] = None
    ) -> None:
        """
        Initialize ALTO generator.

        Args:
            pdf_path: Path to the PDF file to process
            article_item: Optional CeoItem for additional metadata
        """
        self.pdf_path = Path(pdf_path)
        self.article_item = article_item
        self._pages: Optional[List[ALTOPage]] = None

    def extract_layout_from_pdf(self) -> List[ALTOPage]:
        """
        Extract text layout and coordinates from PDF using PyMuPDF.

        Returns:
            List of ALTOPage objects containing layout information
        """
        pages = []

        # Open PDF with PyMuPDF
        doc = fitz.open(self.pdf_path)

        for page_num, page in enumerate(doc, start=1):
            # Get page dimensions
            page_rect = page.rect
            page_width = page_rect.width
            page_height = page_rect.height

            # Extract text as dictionary with position information
            text_dict = page.get_text("dict")

            # Process blocks
            blocks = self._process_blocks(text_dict.get("blocks", []))

            alto_page = ALTOPage(
                page_number=page_num,
                width=page_width,
                height=page_height,
                blocks=blocks
            )
            pages.append(alto_page)

        doc.close()
        return pages

    def _process_blocks(self, blocks: List[Dict]) -> List[ALTOTextBlock]:
        """
        Process PyMuPDF blocks into ALTO TextBlocks.

        Args:
            blocks: List of block dictionaries from PyMuPDF

        Returns:
            List of ALTOTextBlock objects
        """
        alto_blocks = []

        for block in blocks:
            # Skip non-text blocks (images, etc.)
            if block.get("type") != 0:  # 0 = text block
                continue

            lines = block.get("lines", [])
            if not lines:
                continue

            # Process lines in the block
            alto_lines = []
            for line in lines:
                alto_line = self._process_line(line)
                if alto_line:
                    alto_lines.append(alto_line)

            if not alto_lines:
                continue

            # Calculate block bounding box from lines
            block_bbox = block.get("bbox", [0, 0, 0, 0])
            block_hpos = block_bbox[0]
            block_vpos = block_bbox[1]
            block_width = block_bbox[2] - block_bbox[0]
            block_height = block_bbox[3] - block_bbox[1]

            alto_block = ALTOTextBlock(
                lines=alto_lines,
                hpos=block_hpos,
                vpos=block_vpos,
                width=block_width,
                height=block_height
            )
            alto_blocks.append(alto_block)

        return alto_blocks

    def _process_line(self, line: Dict) -> Optional[ALTOTextLine]:
        """
        Process PyMuPDF line into ALTO TextLine.

        Args:
            line: Line dictionary from PyMuPDF

        Returns:
            ALTOTextLine object or None if line has no content
        """
        spans = line.get("spans", [])
        if not spans:
            return None

        # Process spans (words/text runs) in the line
        strings = []
        for span in spans:
            text = span.get("text", "").strip()
            if not text:
                continue

            bbox = span.get("bbox", [0, 0, 0, 0])

            # Split span into words for more granular ALTO
            words = text.split()
            if not words:
                continue

            # Estimate word positions within span
            # (This is approximate - true word positions would require more analysis)
            span_width = bbox[2] - bbox[0]
            word_width = span_width / len(words) if words else span_width

            for i, word in enumerate(words):
                word_hpos = bbox[0] + (i * word_width)

                alto_string = ALTOString(
                    content=word,
                    hpos=word_hpos,
                    vpos=bbox[1],
                    width=word_width,
                    height=bbox[3] - bbox[1]
                )
                strings.append(alto_string)

        if not strings:
            return None

        # Calculate line bounding box
        line_bbox = line.get("bbox", [0, 0, 0, 0])
        line_hpos = line_bbox[0]
        line_vpos = line_bbox[1]
        line_width = line_bbox[2] - line_bbox[0]
        line_height = line_bbox[3] - line_bbox[1]

        return ALTOTextLine(
            strings=strings,
            hpos=line_hpos,
            vpos=line_vpos,
            width=line_width,
            height=line_height
        )

    def generate_alto_xml(self) -> etree.Element:
        """
        Generate ALTO XML from extracted layout.

        Returns:
            lxml Element containing ALTO XML
        """
        # Extract layout if not already done
        if self._pages is None:
            self._pages = self.extract_layout_from_pdf()

        # Create ALTO root element
        alto = etree.Element(
            "alto",
            nsmap={None: self.ALTO_NAMESPACE},
            attrib={
                "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation":
                    f"{self.ALTO_NAMESPACE} "
                    f"https://www.loc.gov/standards/alto/v4/alto-{self.ALTO_VERSION.replace('.', '-')}.xsd"
            }
        )

        # Add Description section
        description = self._create_description()
        alto.append(description)

        # Add Layout section
        layout = self._create_layout()
        alto.append(layout)

        return alto

    def _create_description(self) -> etree.Element:
        """Create ALTO Description section with metadata."""
        description = etree.Element("Description")

        # MeasurementUnit
        measurement_unit = etree.SubElement(description, "MeasurementUnit")
        measurement_unit.text = "pixel"

        # sourceImageInformation (optional)
        source_info = etree.SubElement(description, "sourceImageInformation")
        file_name = etree.SubElement(source_info, "fileName")
        file_name.text = self.pdf_path.name

        # OCR Processing (even though we're not doing OCR, ALTO expects this)
        processing = etree.SubElement(description, "Processing", ID="PROC1")

        processing_datetime = etree.SubElement(processing, "processingDateTime")
        processing_datetime.text = datetime.now().isoformat()

        processing_software = etree.SubElement(
            processing,
            "processingSoftware"
        )
        software_creator = etree.SubElement(processing_software, "softwareCreator")
        software_creator.text = "ALTOGenerator"
        software_name = etree.SubElement(processing_software, "softwareName")
        software_name.text = "Daily Princetonian ALTO Generator"
        software_version = etree.SubElement(processing_software, "softwareVersion")
        software_version.text = "1.0"

        processing_step = etree.SubElement(
            processing,
            "processingStepDescription"
        )
        processing_step.text = "Extracted text and coordinates from PDF using PyMuPDF"

        return description

    def _create_layout(self) -> etree.Element:
        """Create ALTO Layout section with page content."""
        layout = etree.Element("Layout")

        for page_idx, page in enumerate(self._pages, start=1):
            page_elem = self._create_page_element(page, page_idx)
            layout.append(page_elem)

        return layout

    def _create_page_element(self, page: ALTOPage, page_idx: int) -> etree.Element:
        """Create Page element with all content."""
        page_elem = etree.Element(
            "Page",
            ID=f"P{page_idx}",
            PHYSICAL_IMG_NR=str(page.page_number),
            HEIGHT=f"{page.height:.0f}",
            WIDTH=f"{page.width:.0f}"
        )

        # PrintSpace contains the actual content
        print_space = etree.SubElement(
            page_elem,
            "PrintSpace",
            HEIGHT=f"{page.height:.0f}",
            WIDTH=f"{page.width:.0f}",
            HPOS="0",
            VPOS="0"
        )

        # Add text blocks
        for block_idx, block in enumerate(page.blocks, start=1):
            block_elem = self._create_textblock_element(
                block,
                f"P{page_idx}_B{block_idx}"
            )
            print_space.append(block_elem)

        return page_elem

    def _create_textblock_element(
        self,
        block: ALTOTextBlock,
        block_id: str
    ) -> etree.Element:
        """Create TextBlock element."""
        text_block = etree.Element(
            "TextBlock",
            ID=block_id,
            HPOS=f"{block.hpos:.2f}",
            VPOS=f"{block.vpos:.2f}",
            HEIGHT=f"{block.height:.2f}",
            WIDTH=f"{block.width:.2f}"
        )

        # Add text lines
        for line_idx, line in enumerate(block.lines, start=1):
            line_elem = self._create_textline_element(
                line,
                f"{block_id}_L{line_idx}"
            )
            text_block.append(line_elem)

        return text_block

    def _create_textline_element(
        self,
        line: ALTOTextLine,
        line_id: str
    ) -> etree.Element:
        """Create TextLine element."""
        text_line = etree.Element(
            "TextLine",
            ID=line_id,
            HPOS=f"{line.hpos:.2f}",
            VPOS=f"{line.vpos:.2f}",
            HEIGHT=f"{line.height:.2f}",
            WIDTH=f"{line.width:.2f}"
        )

        # Add strings (words)
        for string_idx, string in enumerate(line.strings, start=1):
            string_elem = self._create_string_element(
                string,
                f"{line_id}_S{string_idx}"
            )
            text_line.append(string_elem)

        return text_line

    def _create_string_element(
        self,
        string: ALTOString,
        string_id: str
    ) -> etree.Element:
        """Create String element (word)."""
        string_elem = etree.Element(
            "String",
            ID=string_id,
            CONTENT=string.content,
            HPOS=f"{string.hpos:.2f}",
            VPOS=f"{string.vpos:.2f}",
            HEIGHT=f"{string.height:.2f}",
            WIDTH=f"{string.width:.2f}",
            WC=f"{string.wc:.2f}"  # word confidence
        )

        return string_elem

    def generate(self, output_path: Union[str, Path]) -> None:
        """
        Generate and save ALTO XML file.

        Args:
            output_path: Path where ALTO XML file should be written
        """
        alto_xml = self.generate_alto_xml()

        tree = etree.ElementTree(alto_xml)
        tree.write(
            str(output_path),
            pretty_print=True,
            xml_declaration=True,
            encoding="UTF-8"
        )

    def to_string(self, pretty_print: bool = True) -> str:
        """
        Generate ALTO XML as a string.

        Args:
            pretty_print: Whether to format the XML with indentation

        Returns:
            String containing formatted ALTO XML
        """
        alto_xml = self.generate_alto_xml()
        return etree.tostring(
            alto_xml,
            pretty_print=pretty_print,
            xml_declaration=True,
            encoding="unicode"
        )
