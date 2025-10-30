"""
ALTO XML Generator for Daily Princetonian Articles

This module generates ALTO (Analyzed Layout and Text Object) XML files from PDF documents.
ALTO v4.4 format is used to describe the layout and text content with coordinate information.
"""

from pathlib import Path
from typing import List, Optional, Union
from dataclasses import dataclass
from lxml import etree
import fitz  # PyMuPDF


@dataclass
class ALTOString:
    """Represents a word/string in ALTO format with coordinates."""
    content: str
    hpos: float
    vpos: float
    width: float
    height: float
    wc: float = 1.0  # Word confidence (0.0-1.0)


@dataclass
class ALTOTextLine:
    """Represents a line of text in ALTO format."""
    strings: List[ALTOString]
    hpos: float
    vpos: float
    width: float
    height: float


@dataclass
class ALTOTextBlock:
    """Represents a block of text (e.g., paragraph) in ALTO format."""
    lines: List[ALTOTextLine]
    hpos: float
    vpos: float
    width: float
    height: float
    block_type: str = "paragraph"


@dataclass
class ALTOPage:
    """Represents a page in ALTO format."""
    page_number: int
    width: float
    height: float
    blocks: List[ALTOTextBlock]


class ALTOGenerator:
    """
    Generate ALTO XML from PDF files.

    ALTO (Analyzed Layout and Text Object) is an XML schema for describing
    layout and content of scanned documents. While typically used for OCR
    workflows, we generate ALTO from PDFs to provide coordinate information
    for text layout.

    This implementation uses PyMuPDF to extract text with coordinates from PDFs
    and structures it according to ALTO v4.4 specifications.
    """

    ALTO_NAMESPACE = "http://www.loc.gov/standards/alto/ns-v4#"
    ALTO_VERSION = "4.4"

    def __init__(self, pdf_path: Union[str, Path], article_item=None):
        """
        Initialize ALTO generator.

        Args:
            pdf_path: Path to the PDF file to process
            article_item: Optional CeoItem with article metadata
        """
        self.pdf_path = Path(pdf_path)
        self.article_item = article_item

        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")

    def extract_layout_from_pdf(self) -> List[ALTOPage]:
        """
        Extract text layout information from PDF using PyMuPDF.

        Returns:
            List of ALTOPage objects containing layout information
        """
        pages = []

        with fitz.open(self.pdf_path) as pdf_doc:
            for page_num in range(len(pdf_doc)):
                page = pdf_doc[page_num]
                page_width = page.rect.width
                page_height = page.rect.height

                blocks = []

                # Extract text with detailed layout information using dict format
                # to get block and line structure, then use words for word-level detail
                text_dict = page.get_text("dict")

                # Also get word-level information
                words = page.get_text("words")  # Returns list of (x0, y0, x1, y1, "word", block_no, line_no, word_no)

                # Build a mapping of (block_no, line_no) -> list of word tuples
                from collections import defaultdict
                word_map = defaultdict(list)
                for word_tuple in words:
                    if len(word_tuple) >= 7:
                        x0, y0, x1, y1, word_text, block_no, line_no = word_tuple[:7]
                        word_map[(block_no, line_no)].append({
                            'text': word_text,
                            'bbox': [x0, y0, x1, y1]
                        })

                for block in text_dict.get("blocks", []):
                    if block.get("type") != 0:  # Skip non-text blocks
                        continue

                    lines = []
                    block_bbox = block.get("bbox", [0, 0, 0, 0])
                    block_no = block.get("number", 0)

                    for line_idx, line in enumerate(block.get("lines", [])):
                        strings = []
                        line_bbox = line.get("bbox", [0, 0, 0, 0])

                        # Get words for this line from the word map
                        line_words = word_map.get((block_no, line_idx), [])

                        if line_words:
                            # Use word-level segmentation
                            for word_info in line_words:
                                word_text = word_info['text'].strip()
                                if not word_text:
                                    continue

                                bbox = word_info['bbox']
                                alto_string = ALTOString(
                                    content=word_text,
                                    hpos=bbox[0],
                                    vpos=bbox[1],
                                    width=bbox[2] - bbox[0],
                                    height=bbox[3] - bbox[1],
                                    wc=1.0
                                )
                                strings.append(alto_string)
                        else:
                            # Fallback: split span text into words manually
                            for span in line.get("spans", []):
                                text = span.get("text", "").strip()
                                if not text:
                                    continue

                                bbox = span.get("bbox", [0, 0, 0, 0])
                                span_width = bbox[2] - bbox[0]

                                # Split text into words
                                words_in_span = text.split()
                                if len(words_in_span) == 1:
                                    # Single word, use full span bbox
                                    alto_string = ALTOString(
                                        content=text,
                                        hpos=bbox[0],
                                        vpos=bbox[1],
                                        width=span_width,
                                        height=bbox[3] - bbox[1],
                                        wc=1.0
                                    )
                                    strings.append(alto_string)
                                else:
                                    # Multiple words, estimate positions
                                    total_chars = sum(len(w) for w in words_in_span)
                                    current_x = bbox[0]

                                    for word in words_in_span:
                                        # Estimate word width based on character count
                                        word_width = (len(word) / total_chars) * span_width * 0.9  # 0.9 to account for spaces

                                        alto_string = ALTOString(
                                            content=word,
                                            hpos=current_x,
                                            vpos=bbox[1],
                                            width=word_width,
                                            height=bbox[3] - bbox[1],
                                            wc=1.0
                                        )
                                        strings.append(alto_string)

                                        # Move to next word position (word width + space)
                                        current_x += word_width + (span_width * 0.1 / len(words_in_span))

                        if strings:
                            alto_line = ALTOTextLine(
                                strings=strings,
                                hpos=line_bbox[0],
                                vpos=line_bbox[1],
                                width=line_bbox[2] - line_bbox[0],
                                height=line_bbox[3] - line_bbox[1]
                            )
                            lines.append(alto_line)

                    if lines:
                        alto_block = ALTOTextBlock(
                            lines=lines,
                            hpos=block_bbox[0],
                            vpos=block_bbox[1],
                            width=block_bbox[2] - block_bbox[0],
                            height=block_bbox[3] - block_bbox[1],
                            block_type="paragraph"
                        )
                        blocks.append(alto_block)

                alto_page = ALTOPage(
                    page_number=page_num + 1,
                    width=page_width,
                    height=page_height,
                    blocks=blocks
                )
                pages.append(alto_page)

        return pages

    def generate_alto_xml(self) -> etree.Element:
        """
        Generate ALTO v4.4 XML structure.

        Returns:
            lxml Element containing the complete ALTO XML structure
        """
        pages = self.extract_layout_from_pdf()

        nsmap = {
            None: self.ALTO_NAMESPACE,
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }

        # Root element
        alto = etree.Element(
            f"{{{self.ALTO_NAMESPACE}}}alto",
            nsmap=nsmap,
            attrib={
                "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation":
                    f"{self.ALTO_NAMESPACE} "
                    "http://www.loc.gov/standards/alto/v4/alto-4-4.xsd"
            }
        )

        # Description section
        description = etree.SubElement(alto, f"{{{self.ALTO_NAMESPACE}}}Description")

        measurement_unit = etree.SubElement(description, f"{{{self.ALTO_NAMESPACE}}}MeasurementUnit")
        measurement_unit.text = "pixel"

        source_image_info = etree.SubElement(description, f"{{{self.ALTO_NAMESPACE}}}sourceImageInformation")
        file_name = etree.SubElement(source_image_info, f"{{{self.ALTO_NAMESPACE}}}fileName")
        file_name.text = self.pdf_path.name

        # Processing software info
        processing = etree.SubElement(description, f"{{{self.ALTO_NAMESPACE}}}Processing")
        processing.set("ID", "PROC1")

        processing_software = etree.SubElement(processing, f"{{{self.ALTO_NAMESPACE}}}processingSoftware")
        software_creator = etree.SubElement(processing_software, f"{{{self.ALTO_NAMESPACE}}}softwareCreator")
        software_creator.text = "Daily Princetonian METS Generator"

        software_name = etree.SubElement(processing_software, f"{{{self.ALTO_NAMESPACE}}}softwareName")
        software_name.text = "ALTOGenerator"

        software_version = etree.SubElement(processing_software, f"{{{self.ALTO_NAMESPACE}}}softwareVersion")
        software_version.text = "1.0"

        # Layout section
        layout = etree.SubElement(alto, f"{{{self.ALTO_NAMESPACE}}}Layout")

        for alto_page in pages:
            page_elem = etree.SubElement(
                layout, f"{{{self.ALTO_NAMESPACE}}}Page",
                ID=f"PAGE_{alto_page.page_number}",
                PHYSICAL_IMG_NR=str(alto_page.page_number),
                HEIGHT=f"{alto_page.height:.2f}",
                WIDTH=f"{alto_page.width:.2f}"
            )

            print_space = etree.SubElement(
                page_elem, f"{{{self.ALTO_NAMESPACE}}}PrintSpace",
                HPOS="0",
                VPOS="0",
                HEIGHT=f"{alto_page.height:.2f}",
                WIDTH=f"{alto_page.width:.2f}"
            )

            for block_idx, block in enumerate(alto_page.blocks, 1):
                text_block = etree.SubElement(
                    print_space, f"{{{self.ALTO_NAMESPACE}}}TextBlock",
                    ID=f"TB_{alto_page.page_number}_{block_idx}",
                    HPOS=f"{block.hpos:.2f}",
                    VPOS=f"{block.vpos:.2f}",
                    HEIGHT=f"{block.height:.2f}",
                    WIDTH=f"{block.width:.2f}"
                )

                for line_idx, line in enumerate(block.lines, 1):
                    text_line = etree.SubElement(
                        text_block, f"{{{self.ALTO_NAMESPACE}}}TextLine",
                        ID=f"TL_{alto_page.page_number}_{block_idx}_{line_idx}",
                        HPOS=f"{line.hpos:.2f}",
                        VPOS=f"{line.vpos:.2f}",
                        HEIGHT=f"{line.height:.2f}",
                        WIDTH=f"{line.width:.2f}"
                    )

                    # Track element indices for String and SP elements
                    element_idx = 1
                    sp_idx = 1

                    for string_idx, string in enumerate(line.strings):
                        # Add String element
                        string_elem = etree.SubElement(
                            text_line, f"{{{self.ALTO_NAMESPACE}}}String",
                            ID=f"P{alto_page.page_number}_ST{element_idx:05d}",
                            CONTENT=string.content,
                            HPOS=f"{string.hpos:.2f}",
                            VPOS=f"{string.vpos:.2f}",
                            HEIGHT=f"{string.height:.2f}",
                            WIDTH=f"{string.width:.2f}",
                            WC=f"{string.wc:.2f}"
                        )
                        element_idx += 1

                        # Add SP (space) element between words (but not after the last word)
                        if string_idx < len(line.strings) - 1:
                            next_string = line.strings[string_idx + 1]
                            # Calculate space position and width
                            space_hpos = string.hpos + string.width
                            space_width = next_string.hpos - space_hpos
                            # Only add SP if there's a meaningful gap
                            if space_width > 0:
                                sp_elem = etree.SubElement(
                                    text_line, f"{{{self.ALTO_NAMESPACE}}}SP",
                                    ID=f"P{alto_page.page_number}_SP{sp_idx:05d}",
                                    HPOS=f"{space_hpos:.2f}",
                                    VPOS=f"{string.vpos:.2f}",
                                    WIDTH=f"{space_width:.2f}"
                                )
                                sp_idx += 1

        return alto

    def to_string(self, pretty_print: bool = True) -> str:
        """
        Generate ALTO XML as a string.

        Args:
            pretty_print: Whether to format the XML with indentation

        Returns:
            ALTO XML as a UTF-8 string
        """
        alto_xml = self.generate_alto_xml()
        return etree.tostring(
            alto_xml,
            pretty_print=pretty_print,
            encoding='unicode',
            xml_declaration=False
        )

    def generate(self, output_path: Union[str, Path]) -> None:
        """
        Generate and save ALTO XML to a file.

        Args:
            output_path: Path where the ALTO XML file will be saved
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        alto_xml = self.generate_alto_xml()
        tree = etree.ElementTree(alto_xml)
        tree.write(
            str(output_path),
            pretty_print=True,
            xml_declaration=True,
            encoding='UTF-8'
        )
