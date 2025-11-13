#!/usr/bin/env python3
"""
METS Generator for Daily Princetonian Issues
Generates METS XML with article derivatives (JSON, HTML, TXT, PDF)
"""

import hashlib
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from lxml import etree

from clients import CeoClient, CeoItem
from generators.html_generator import HTMLGenerator
from generators.mods_generator import MODSGenerator
from generators.pdf_generator import PDFGenerator
from generators.txt_generator import TXTGenerator


class MESTGenerator:
    """Generate METS files for Daily Princetonian issues"""

    def __init__(self, output_base_dir="mets_output"):
        self.output_base_dir = output_base_dir
        self.client = CeoClient()
        self.nsmap = {
            "mets": "http://www.loc.gov/METS/",
            "mods": "http://www.loc.gov/mods/v3",
            "xlink": "http://www.w3.org/1999/xlink",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        }

    def create_issue_package(self, date, article_type="article"):
        """
        Create a complete issue package with METS file

        Args:
            date: datetime object for the issue date
            article_type: type of articles to fetch

        Returns:
            Path to the generated METS file
        """
        # Create directory structure
        date_str = date.strftime("%Y-%m-%d")
        issue_dir = Path(self.output_base_dir) / date_str
        articles_dir = issue_dir / "articles"
        articles_dir.mkdir(parents=True, exist_ok=True)

        print(f"Creating issue package for {date_str}...")

        # Fetch articles from API using CeoClient
        # CeoClient expects string dates, so format the date
        start_date_str = date.strftime("%Y-%m-%d")
        # API requires next day for end_date to get articles for a single day
        end_date = date + timedelta(days=1)
        end_date_str = end_date.strftime("%Y-%m-%d")

        items = self.client.articles(start_date_str, end_date_str, article_type)

        if not items:
            print(f"No articles found for {date_str}")
            return None

        print(f"Found {len(items)} articles")

        # Generate derivatives for each article
        article_data = []
        for item in items:
            article_id = item["id"]
            article_slug = item["slug"]

            print(f"  Processing article {article_id}: {item['headline'][:50]}...")

            # Create article directory
            article_dir = articles_dir / f"article-{article_id}"
            article_dir.mkdir(exist_ok=True)

            # Generate derivatives
            files = self._generate_derivatives(item, article_dir, article_id)

            article_data.append(
                {"item": item, "files": files, "article_dir": article_dir}
            )

        # Generate METS XML
        mets_path = issue_dir / "mets.xml"
        self._generate_mets(date_str, article_data, mets_path)

        print(f"\n✓ Issue package created at: {issue_dir}")
        print(f"✓ METS file: {mets_path}")

        return mets_path

    def _generate_derivatives(self, item: CeoItem, article_dir: Path, article_id: str):
        """Generate JSON, HTML, TXT, and PDF derivatives for an article"""
        files = {}

        # 1. JSON - raw article data (convert dataclass to dict)
        json_path = article_dir / f"article-{article_id}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            # Convert CeoItem dataclass to dict
            import dataclasses

            item_dict = (
                dataclasses.asdict(item)
                if dataclasses.is_dataclass(item)
                else item.__dict__
            )
            json.dump(item_dict, f, ensure_ascii=False, indent=2)
        files["json"] = self._get_file_info(json_path, "application/json")

        # 2. HTML - formatted article content using HTMLGenerator
        html_generator = HTMLGenerator(item)
        html_path = article_dir / f"article-{article_id}.html"
        html_generator.generate(html_path)
        files["html"] = self._get_file_info(html_path, "text/html")

        # 3. TXT - plain text extraction using TXTGenerator
        txt_generator = TXTGenerator(item)
        txt_path = article_dir / f"article-{article_id}.txt"
        txt_generator.generate(txt_path)
        files["txt"] = self._get_file_info(txt_path, "text/plain")

        # 4. PDF - single article PDF using PDFGenerator
        pdf_generator = PDFGenerator(html_generator.html)
        pdf_path = article_dir / f"article-{article_id}.pdf"
        pdf_generator.generate(pdf_path)
        files["pdf"] = self._get_file_info(pdf_path, "application/pdf")

        return files

    def _get_file_info(self, file_path, mimetype):
        """Get file metadata including size and checksum"""
        file_size = os.path.getsize(file_path)

        # Calculate MD5 checksum
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)

        return {
            "path": file_path,
            "size": file_size,
            "checksum": md5_hash.hexdigest(),
            "mimetype": mimetype,
        }

    def _generate_mets(self, date_str, article_data, mets_path):
        """Generate METS XML file"""
        # Create root METS element
        METS = "{%s}" % self.nsmap["mets"]
        MODS = "{%s}" % self.nsmap["mods"]
        XLINK = "{%s}" % self.nsmap["xlink"]

        root = etree.Element(
            METS + "mets",
            nsmap=self.nsmap,
            attrib={
                "{%s}schemaLocation"
                % self.nsmap[
                    "xsi"
                ]: "http://www.loc.gov/METS/ http://www.loc.gov/standards/mets/mets.xsd "
                "http://www.loc.gov/mods/v3 http://www.loc.gov/standards/mods/v3/mods-3-7.xsd"
            },
        )

        # Veridian requires TYPE="Newspaper" attribute on the root element
        root.attrib["TYPE"] = "Newspaper"

        # METS Header
        mets_hdr = etree.SubElement(
            root, METS + "metsHdr", CREATEDATE=datetime.now().isoformat()
        )

        agent = etree.SubElement(
            mets_hdr, METS + "agent", ROLE="CREATOR", TYPE="ORGANIZATION"
        )
        name = etree.SubElement(agent, METS + "name")
        name.text = "Princeton University Library"

        # Generate dmdSec for each article
        for idx, article in enumerate(article_data, 1):
            dmd_id = f"DMD{idx}"
            self._add_dmd_sec(root, article["item"], dmd_id)

        # Generate fileSec
        file_sec = etree.SubElement(root, METS + "fileSec")

        for idx, article in enumerate(article_data, 1):
            file_grp = etree.SubElement(
                file_sec, METS + "fileGrp", USE=f"Article {article['item']['id']}"
            )

            for format_type, file_info in article["files"].items():
                file_id = f"FILE{idx}_{format_type.upper()}"

                file_elem = etree.SubElement(
                    file_grp,
                    METS + "file",
                    ID=file_id,
                    MIMETYPE=file_info["mimetype"],
                    SIZE=str(file_info["size"]),
                    CHECKSUM=file_info["checksum"],
                    CHECKSUMTYPE="MD5",
                )

                # Relative path from METS file location
                rel_path = os.path.relpath(file_info["path"], mets_path.parent)

                flocat = etree.SubElement(
                    file_elem,
                    METS + "FLocat",
                    LOCTYPE="URL",
                    attrib={XLINK + "href": f"file://{rel_path}"},
                )

        # Generate structMap
        struct_map = etree.SubElement(
            root, METS + "structMap", TYPE="logical", LABEL="Daily Princetonian Issue"
        )

        issue_div = etree.SubElement(
            struct_map, METS + "div", TYPE="Issue", LABEL=f"Issue of {date_str}"
        )

        for idx, article in enumerate(article_data, 1):
            item = article["item"]

            article_div = etree.SubElement(
                issue_div,
                METS + "div",
                TYPE="Article",
                LABEL=item["headline"],
                DMDID=f"DMD{idx}",
            )

            content_div = etree.SubElement(article_div, METS + "div", TYPE="Content")

            # Add fptr for each format
            for format_type in ["json", "html", "txt", "pdf"]:
                file_id = f"FILE{idx}_{format_type.upper()}"
                fptr = etree.SubElement(content_div, METS + "fptr", FILEID=file_id)

        # Write METS XML to file
        tree = etree.ElementTree(root)
        tree.write(
            str(mets_path), pretty_print=True, xml_declaration=True, encoding="UTF-8"
        )

        print(f"  ✓ Generated METS XML with {len(article_data)} articles")

    def _add_dmd_sec(self, root, item: CeoItem, dmd_id: str):
        """Add descriptive metadata section for an article using MODSGenerator"""
        METS = "{%s}" % self.nsmap["mets"]

        dmd_sec = etree.SubElement(root, METS + "dmdSec", ID=dmd_id)
        md_wrap = etree.SubElement(dmd_sec, METS + "mdWrap", MDTYPE="MODS")
        xml_data = etree.SubElement(md_wrap, METS + "xmlData")

        # Generate MODS record using MODSGenerator
        mods_generator = MODSGenerator(item)
        mods_element = mods_generator.generate_element()

        # Append the MODS element to xmlData
        xml_data.append(mods_element)


def main():
    """Command-line interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate METS package for Daily Princetonian issue",
        epilog="Examples:\n"
        "  Single date:  python generate_mets.py 2025-10-08\n"
        "  Date range:   python generate_mets.py 2025-10-07 --end-date 2025-10-09\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("date", help="Issue date or start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="End date for range (YYYY-MM-DD)")
    parser.add_argument(
        "--output-dir",
        default="mets_output",
        help="Output directory (default: mets_output)",
    )
    parser.add_argument(
        "--type",
        default="article",
        choices=["article", "opinion", "sports"],
        help="Article type (default: article)",
    )
    parser.add_argument("--debug", action="store_true", help="Show debug information")

    args = parser.parse_args()

    # Parse dates
    try:
        start_date = datetime.strptime(args.date, "%Y-%m-%d")
        if args.end_date:
            end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
        else:
            # API requires different start and end dates, so add one day
            end_date = start_date + timedelta(days=1)
    except ValueError:
        print(f"Error: Invalid date format. Use YYYY-MM-DD")
        return 1

    if start_date > end_date:
        print("Error: Start date must be before end date")
        return 1

    # Generate METS package
    generator = MESTGenerator(args.output_dir)

    # If date range spans multiple days, warn user
    if (end_date - start_date).days > 0:
        print(f"Note: Fetching articles from {start_date.date()} to {end_date.date()}")
        print(f"      All articles will be in one METS package for {start_date.date()}")

    try:
        # Use create_issue_package method which now uses CeoClient internally
        mets_path = generator.create_issue_package(start_date, args.type)

        if mets_path is None:
            print(f"\n✗ No articles found for {start_date.date()}")
            if not args.end_date:
                print(f"\n💡 Tips:")
                print(f"  • There may be no articles published on this exact date")
                print(
                    f"  • Try a date range: --end-date {(start_date + timedelta(days=2)).strftime('%Y-%m-%d')}"
                )
            return 1

        print(f"\n✓ Success! METS package created")
        return 0

    except Exception as e:
        print(f"\n✗ Error: {e}")
        if args.debug:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
