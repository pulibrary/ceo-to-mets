import json
from datetime import datetime
from typing import Dict

from lxml import etree
import html2text

from clients import CeoItem


class MODSGenerator:
    """Generate MODS (Metadata Object Description Schema) XML for articles."""

    def __init__(self, item: CeoItem) -> None:
        """
        Initialize MODS generator with article data.

        Args:
            item: CeoItem containing article data
        """
        self.item = item
        self.nsmap = {
            "mods": "http://www.loc.gov/mods/v3",
        }

    def generate_element(self) -> etree.Element:
        """
        Generate MODS XML element for the article.

        Returns:
            lxml Element containing MODS metadata
        """
        MODS = "{%s}" % self.nsmap["mods"]

        # Create MODS record
        mods = etree.Element(MODS + "mods", version="3.7", nsmap=self.nsmap)

        # Title
        title_info = etree.SubElement(mods, MODS + "titleInfo")
        title = etree.SubElement(title_info, MODS + "title")
        title.text = self.item.headline

        if self.item.subhead:
            subtitle = etree.SubElement(title_info, MODS + "subTitle")
            subtitle.text = self.item.subhead

        # Authors
        if self.item.authors:
            # Handle authors whether it's a JSON string or list
            authors = self.item.authors
            if isinstance(authors, str):
                # Try to parse JSON string
                try:
                    authors = json.loads(authors)
                except (json.JSONDecodeError, ValueError):
                    # If parsing fails, treat as single author name
                    authors = [{"name": authors}]
            elif not isinstance(authors, list):
                authors = []

            for author in authors:
                if isinstance(author, dict) and "name" in author:
                    name_elem = etree.SubElement(mods, MODS + "name", type="personal")
                    name_part = etree.SubElement(name_elem, MODS + "namePart")
                    name_part.text = author["name"]
                    role = etree.SubElement(name_elem, MODS + "role")
                    role_term = etree.SubElement(role, MODS + "roleTerm", type="text")
                    role_term.text = "author"

        # Origin info (publication date)
        if self.item.published_at:
            origin_info = etree.SubElement(mods, MODS + "originInfo")
            date_issued = etree.SubElement(
                origin_info, MODS + "dateIssued", encoding="iso8601"
            )
            try:
                dt = datetime.strptime(self.item.published_at, "%Y-%m-%d %H:%M:%S")
                date_issued.text = dt.strftime("%Y-%m-%d")
            except:
                date_issued.text = self.item.published_at

        # Abstract
        if self.item.abstract:
            # Strip HTML from abstract
            h = html2text.HTML2Text()
            h.ignore_links = True
            h.ignore_images = True
            abstract_text = h.handle(self.item.abstract).strip()

            abstract = etree.SubElement(mods, MODS + "abstract")
            abstract.text = abstract_text

        # Genre
        genre = etree.SubElement(mods, MODS + "genre")
        genre.text = "article"

        # Identifier
        identifier = etree.SubElement(mods, MODS + "identifier", type="local")
        identifier.text = self.item.id

        # Location (URL)
        location = etree.SubElement(mods, MODS + "location")
        url = etree.SubElement(location, MODS + "url")
        url.text = f"https://www.dailyprincetonian.com/article/{self.item.slug}"

        # Tags as subjects
        if self.item.tags:
            # Handle tags whether it's a JSON string or list
            tags = self.item.tags
            if isinstance(tags, str):
                # Try to parse JSON string
                try:
                    tags = json.loads(tags)
                except (json.JSONDecodeError, ValueError):
                    # If parsing fails, skip tags
                    tags = []
            elif not isinstance(tags, list):
                tags = []

            for tag in tags:
                if isinstance(tag, dict) and "name" in tag:
                    subject = etree.SubElement(mods, MODS + "subject")
                    topic = etree.SubElement(subject, MODS + "topic")
                    topic.text = tag["name"]

        return mods

    def to_string(self, pretty_print: bool = True) -> str:
        """
        Generate MODS XML as a string.

        Args:
            pretty_print: Whether to format the XML with indentation

        Returns:
            String containing formatted MODS XML
        """
        mods_element = self.generate_element()
        return etree.tostring(
            mods_element,
            pretty_print=pretty_print,
            xml_declaration=False,
            encoding="unicode",
        )
