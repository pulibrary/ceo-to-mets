#!/usr/bin/env python3
"""
Create a demo METS package for study and testing.

This script generates a complete METS package with sample articles
without needing to call the actual API. Useful for testing, learning,
and demonstrating the METS package structure.
"""

import argparse
import dataclasses
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from lxml import etree

from clients import CeoItem
from generators.alto_generator import ALTOGenerator
from generators.html_generator import HTMLGenerator
from generators.mods_generator import MODSGenerator
from generators.pdf_generator import PDFGenerator
from generators.txt_generator import TXTGenerator


def create_sample_articles():
    """Create sample CeoItem articles for demo."""
    articles = []

    # Article 1: News story
    articles.append(
        CeoItem(
            id="10001",
            uuid="abc-news-001",
            slug="campus-announces-new-sustainability-initiative",
            seo_title="Campus Announces New Sustainability Initiative",
            seo_description="University launches comprehensive plan to achieve carbon neutrality by 2030",
            seo_image="",
            headline="Campus Announces Ambitious Sustainability Initiative",
            subhead="University commits to carbon neutrality by 2030 with new green energy plan",
            abstract="<p>The university announced today a comprehensive sustainability initiative aimed at achieving carbon neutrality by 2030, marking one of the most ambitious environmental commitments among peer institutions.</p>",
            content="""
        <p>In a major announcement this morning, university administrators unveiled a sweeping sustainability
        initiative that will transform campus operations over the next decade. The plan includes significant
        investments in renewable energy, building retrofits, and sustainable transportation.</p>

        <p>"This is a defining moment for our institution," said President Jane Smith. "We have a responsibility
        to lead by example in addressing the climate crisis, and this plan demonstrates our commitment to a
        sustainable future."</p>

        <p>Key components of the initiative include:</p>
        <ul>
            <li>Installation of solar panels on all major campus buildings</li>
            <li>Transition to electric vehicle fleet by 2025</li>
            <li>Comprehensive building energy efficiency upgrades</li>
            <li>Expansion of campus composting and recycling programs</li>
            <li>New sustainable food procurement policies</li>
        </ul>

        <p>The plan has received widespread support from student environmental groups, who have been
        advocating for stronger climate action for years. "This is exactly the kind of bold leadership we
        need," said Student Environmental Council President Alex Johnson.</p>

        <p>The university estimates the initiative will require an investment of $50 million over the next
        decade, with much of that cost offset by energy savings and external grant funding.</p>
        """,
            infobox="",
            template="article",
            short_token="sus001",
            status="published",
            weight="1",
            media_id="",
            created_at="2025-10-15 08:00:00",
            modified_at="2025-10-15 09:00:00",
            published_at="2025-10-15 10:00:00",
            metadata="{}",
            hits="2500",
            normalized_tags="news,campus,sustainability,environment",
            ceo_id="10001",
            ssts_id="",
            ssts_path="",
            tags='[{"name": "News"}, {"name": "Campus"}, {"name": "Environment"}, {"name": "Sustainability"}]',
            authors='[{"name": "Sarah Chen"}, {"name": "Michael Rodriguez"}]',
            dominantMedia="",
        )
    )

    # Article 2: Opinion piece
    articles.append(
        CeoItem(
            id="10002",
            uuid="abc-opinion-001",
            slug="we-need-more-mental-health-resources",
            seo_title="Opinion: We Need More Mental Health Resources on Campus",
            seo_description="Student argues for expanded mental health services and reduced stigma",
            seo_image="",
            headline="We Need to Talk About Mental Health on Campus",
            subhead="It's time to invest in comprehensive support services for student wellbeing",
            abstract="<p>As students face mounting pressures, our current mental health resources are insufficient. We need immediate action to expand services and reduce stigma.</p>",
            content="""
        <p>Last week, I watched a close friend struggle to get a counseling appointment, only to be told
        the earliest available slot was three weeks away. This is unacceptable. When students are in crisis,
        three weeks might as well be three years.</p>

        <p>The numbers paint a troubling picture. According to a recent campus survey, 60% of students
        reported experiencing significant stress or anxiety in the past semester. Yet our counseling center
        is chronically understaffed, operating with just eight full-time counselors for a student body of
        5,000.</p>

        <p>This isn't just about numbers—it's about lives. Mental health challenges don't wait for convenient
        appointment times. Depression doesn't take breaks during exam periods. Anxiety doesn't pause for
        winter recess.</p>

        <p>We need immediate action on several fronts:</p>
        <ul>
            <li>Hire additional full-time counselors to reduce wait times</li>
            <li>Expand crisis intervention services and after-hours support</li>
            <li>Provide better training for RAs and peer supporters</li>
            <li>Create more group therapy and workshop options</li>
            <li>Partner with local mental health providers to expand capacity</li>
        </ul>

        <p>Some will say this is too expensive. I say: what's the cost of inaction? How do we measure the
        value of a student who gets help before reaching a crisis point? How do we calculate the long-term
        impact of supporting student mental health?</p>

        <p>Our peer institutions are investing heavily in mental health services. It's time we do the same.
        Student wellbeing should be our top priority—not an afterthought in the budget process.</p>
        """,
            infobox="",
            template="article",
            short_token="op001",
            status="published",
            weight="0",
            media_id="",
            created_at="2025-10-15 12:00:00",
            modified_at="2025-10-15 13:00:00",
            published_at="2025-10-15 14:00:00",
            metadata="{}",
            hits="1800",
            normalized_tags="opinion,mental-health,student-life",
            ceo_id="10002",
            ssts_id="",
            ssts_path="",
            tags='[{"name": "Opinion"}, {"name": "Mental Health"}, {"name": "Student Life"}]',
            authors='[{"name": "Emma Thompson"}]',
            dominantMedia="",
        )
    )

    # Article 3: Sports story
    articles.append(
        CeoItem(
            id="10003",
            uuid="abc-sports-001",
            slug="womens-soccer-advances-to-finals",
            seo_title="Women's Soccer Team Advances to Championship Finals",
            seo_description="Tigers defeat rivals in overtime thriller to secure spot in finals",
            seo_image="",
            headline="Women's Soccer Advances to Finals in Overtime Thriller",
            subhead="Last-minute goal sends Tigers to championship game for first time in five years",
            abstract="<p>The women's soccer team secured a dramatic 2-1 overtime victory against conference rivals, earning their first trip to the championship finals since 2020.</p>",
            content="""
        <p>In a match that will be remembered for years to come, the women's soccer team defeated their
        longtime rivals 2-1 in overtime Saturday afternoon, punching their ticket to the conference
        championship finals for the first time since 2020.</p>

        <p>Junior forward Maria Santos scored the golden goal in the 103rd minute, converting a perfect
        cross from sophomore midfielder Aisha Patel to send the home crowd into a frenzy. "I just knew I
        had to be in the right place at the right time," Santos said after the match. "Aisha put it right
        on my foot—I just had to finish it."</p>

        <p>The Tigers dominated possession throughout the match but struggled to break through their
        opponents' stubborn defense. Senior captain Rachel Kim finally broke the deadlock in the 67th
        minute, firing a powerful shot from just outside the penalty area that left the goalkeeper with
        no chance.</p>

        <p>But the visitors equalized just five minutes later on a controversial penalty kick, setting up
        a tense final twenty minutes of regulation that saw both teams create chances but fail to convert.</p>

        <p>Head coach Jennifer Martinez praised her team's resilience. "This group has worked so hard all
        season. They never gave up, even when things looked difficult. They deserve this moment."</p>

        <p>The Tigers will face top-seeded State University in the championship finals next Saturday.
        It will be a rematch of their early-season meeting, which State won 3-2 in a closely contested match.</p>

        <p>"We know what we're up against," Santos said. "But we're a different team now. We're ready."</p>
        """,
            infobox="",
            template="article",
            short_token="sp001",
            status="published",
            weight="0",
            media_id="",
            created_at="2025-10-15 18:00:00",
            modified_at="2025-10-15 19:00:00",
            published_at="2025-10-15 20:00:00",
            metadata="{}",
            hits="3200",
            normalized_tags="sports,soccer,womens-sports",
            ceo_id="10003",
            ssts_id="",
            ssts_path="",
            tags='[{"name": "Sports"}, {"name": "Soccer"}, {"name": "Women\'s Athletics"}]',
            authors='[{"name": "James Park"}]',
            dominantMedia="",
        )
    )

    return articles


def generate_derivatives(article, article_dir, verbose=False):
    """Generate JSON, HTML, TXT, PDF, and ALTO derivatives for an article."""
    files = {}
    article_id = article.id

    if verbose:
        print(f"  Generating derivatives for article {article_id}...")

    # 1. JSON - raw article data
    json_path = article_dir / f"article-{article_id}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        item_dict = dataclasses.asdict(article)
        json.dump(item_dict, f, ensure_ascii=False, indent=2)
    files["json"] = get_file_info(json_path, "application/json")

    # 2. HTML - formatted article content
    html_generator = HTMLGenerator()
    html_generator.items = [article]
    html_generator.generate()
    html_path = article_dir / f"article-{article_id}.html"
    html_generator.dump(html_path)
    files["html"] = get_file_info(html_path, "text/html")

    # 3. TXT - plain text extraction
    txt_generator = TXTGenerator()
    txt_generator.item = article
    txt_path = article_dir / f"article-{article_id}.txt"
    txt_generator.dump(txt_path)
    files["txt"] = get_file_info(txt_path, "text/plain")

    # 4. PDF - single article PDF
    pdf_generator = PDFGenerator(html_generator.html)
    pdf_path = article_dir / f"article-{article_id}.pdf"
    pdf_generator.dump(pdf_path)
    files["pdf"] = get_file_info(pdf_path, "application/pdf")

    # 5. ALTO - layout and text coordinates
    alto_generator = ALTOGenerator()
    alto_generator.pdf_path = pdf_path
    alto_path = article_dir / f"article-{article_id}.alto.xml"
    alto_generator.dump(alto_path)
    files["alto"] = get_file_info(alto_path, "application/xml+alto")

    return files


def get_file_info(file_path, mimetype):
    """Get file metadata including size and checksum."""
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


def generate_mets(date_str, article_data, mets_path):
    """Generate METS XML file."""
    nsmap = {
        "mets": "http://www.loc.gov/METS/",
        "mods": "http://www.loc.gov/mods/v3",
        "xlink": "http://www.w3.org/1999/xlink",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }

    METS = "{%s}" % nsmap["mets"]
    XLINK = "{%s}" % nsmap["xlink"]

    root = etree.Element(
        METS + "mets",
        nsmap=nsmap,
        attrib={
            "{%s}schemaLocation"
            % nsmap[
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
        add_dmd_sec(root, article["item"], dmd_id, nsmap)

    # Generate fileSec
    file_sec = etree.SubElement(root, METS + "fileSec")

    for idx, article in enumerate(article_data, 1):
        file_grp = etree.SubElement(
            file_sec, METS + "fileGrp", USE=f"Article {article['item'].id}"
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
        root, METS + "structMap", TYPE="logical", LABEL="Daily Princetonian Demo Issue"
    )

    issue_div = etree.SubElement(
        struct_map, METS + "div", TYPE="Issue", LABEL=f"Demo Issue - {date_str}"
    )

    for idx, article in enumerate(article_data, 1):
        item = article["item"]

        article_div = etree.SubElement(
            issue_div,
            METS + "div",
            TYPE="Article",
            LABEL=item.headline,
            DMDID=f"DMD{idx}",
        )

        content_div = etree.SubElement(article_div, METS + "div", TYPE="Content")

        # Add fptr for each format
        for format_type in ["json", "html", "txt", "pdf", "alto"]:
            file_id = f"FILE{idx}_{format_type.upper()}"
            fptr = etree.SubElement(content_div, METS + "fptr", FILEID=file_id)

    # Write METS XML to file
    tree = etree.ElementTree(root)
    tree.write(
        str(mets_path), pretty_print=True, xml_declaration=True, encoding="UTF-8"
    )


def add_dmd_sec(root, item, dmd_id, nsmap):
    """Add descriptive metadata section for an article using MODSGenerator."""
    METS = "{%s}" % nsmap["mets"]

    dmd_sec = etree.SubElement(root, METS + "dmdSec", ID=dmd_id)
    md_wrap = etree.SubElement(dmd_sec, METS + "mdWrap", MDTYPE="MODS")
    xml_data = etree.SubElement(md_wrap, METS + "xmlData")

    # Generate MODS record using MODSGenerator
    mods_generator = MODSGenerator(item)
    mods_element = mods_generator.generate_element()

    # Append the MODS element to xmlData
    xml_data.append(mods_element)


def main():
    """Create the demo METS package."""
    parser = argparse.ArgumentParser(
        prog='demo-mets',
        description='Generate a demo METS package with sample Daily Princetonian articles',
        epilog='This tool creates a complete METS package without needing API access'
    )
    parser.add_argument(
        '--output', '-o',
        default='demo_mets_output',
        metavar='DIR',
        help='Output directory (default: demo_mets_output)'
    )
    parser.add_argument(
        '--date',
        default='2025-10-15',
        metavar='YYYY-MM-DD',
        help='Issue date for the demo package (default: 2025-10-15)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed progress information'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Minimal output (only errors and final summary)'
    )

    args = parser.parse_args()

    # Setup verbosity
    quiet = args.quiet
    verbose = args.verbose and not quiet

    if not quiet:
        print("=" * 70)
        print("Daily Princetonian Demo METS Package Generator")
        print("=" * 70)
        print()

    # Setup output directory
    output_dir = Path(args.output)
    date_str = args.date
    issue_dir = output_dir / date_str
    articles_dir = issue_dir / "articles"
    articles_dir.mkdir(parents=True, exist_ok=True)

    if verbose:
        print(f"Output directory: {issue_dir}")
        print()

    # Create sample articles
    if not quiet:
        print("Creating sample articles...")
    articles = create_sample_articles()
    if not quiet:
        print(f"✓ Created {len(articles)} sample articles")
        print()

    # Generate derivatives for each article
    article_data = []
    for article in articles:
        if not quiet:
            headline = article.headline[:60] + "..." if len(article.headline) > 60 else article.headline
            print(f"Processing: {headline}")

        article_dir = articles_dir / f"article-{article.id}"
        article_dir.mkdir(exist_ok=True)

        files = generate_derivatives(article, article_dir, verbose=verbose)

        article_data.append(
            {"item": article, "files": files, "article_dir": article_dir}
        )

        if not quiet:
            print(f"  ✓ Generated JSON, HTML, TXT, PDF, ALTO")

    if not quiet:
        print()

    # Generate METS XML
    if not quiet:
        print("Generating METS XML...")
    mets_path = issue_dir / "mets.xml"
    generate_mets(date_str, article_data, mets_path)
    if not quiet:
        print(f"✓ Generated METS XML with {len(article_data)} articles")
        print()

    print("=" * 70)
    print("Demo METS package created successfully!")
    print("=" * 70)
    print()
    print(f"Location: {issue_dir.absolute()}")
    print()
    print("Package contents:")
    print(f"  • mets.xml - METS metadata file")
    print(f"  • articles/ - Directory containing {len(articles)} articles")
    print()
    print("Each article includes:")
    print("  • JSON - Raw article data")
    print("  • HTML - Formatted article for web viewing")
    print("  • TXT - Plain text extraction")
    print("  • PDF - Formatted PDF document")
    print("  • ALTO - Layout and text coordinates (XML)")
    print()
    print("You can explore the package structure and study the METS XML format.")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
