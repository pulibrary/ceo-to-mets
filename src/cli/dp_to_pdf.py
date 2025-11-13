#!/usr/bin/env python3
"""
Fetch articles from Daily Princetonian API and generate PDF.

This script allows you to download articles from the Daily Princetonian's
CEO API and convert them to a nicely formatted PDF document.
"""

import argparse
import json
import sys
from pathlib import Path

from clients import CeoClient
from generators.html_generator import HTMLGenerator
from generators.pdf_generator import PDFGenerator


def generate_pdf(items, output_file='articles.pdf', include_images=False):
    """
    Generate PDF from article items using HTMLGenerator and PDFGenerator.

    Args:
        items: List of CeoItem objects
        output_file: output PDF filename
        include_images: whether to include featured images
    """
    print(f"Generating PDF: {output_file}...")

    # Generate HTML using HTMLGenerator
    html_generator = HTMLGenerator()
    html_generator.items = items
    html_generator.generate(include_images=include_images)

    # Generate PDF using PDFGenerator
    pdf_generator = PDFGenerator(html_generator.html)
    pdf_generator.dump(output_file)

    print(f"✓ PDF created successfully!")

def main():
    """Main entry point for the dp-to-pdf command-line tool."""
    parser = argparse.ArgumentParser(
        prog='dp-to-pdf',
        description='Fetch Daily Princetonian articles and convert to PDF',
        epilog='Example: dp-to-pdf --start-date 2025-10-07 --end-date 2025-10-09 --output articles.pdf'
    )
    parser.add_argument(
        '--start-date',
        required=True,
        metavar='YYYY-MM-DD',
        help='Start date for article search'
    )
    parser.add_argument(
        '--end-date',
        required=True,
        metavar='YYYY-MM-DD',
        help='End date for article search'
    )
    parser.add_argument(
        '--output', '-o',
        default='articles.pdf',
        metavar='FILE',
        help='Output PDF filename (default: articles.pdf)'
    )
    parser.add_argument(
        '--type', '-t',
        default='article',
        choices=['article', 'opinion', 'sports'],
        help='Article type to fetch (default: article)'
    )
    parser.add_argument(
        '--include-images', '-i',
        action='store_true',
        help='Include featured images in PDF'
    )
    parser.add_argument(
        '--save-json',
        metavar='FILE',
        help='Also save raw JSON data to this file'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    try:
        # Validate output path
        output_path = Path(args.output)
        if output_path.exists() and not args.verbose:
            response = input(f"File {args.output} already exists. Overwrite? [y/N] ")
            if response.lower() not in ('y', 'yes'):
                print("Aborted.")
                return 0

        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize CeoClient
        if args.verbose:
            print("Initializing CEO Client...")
        client = CeoClient()

        # Fetch articles using CeoClient
        print(f"Fetching {args.type} articles from {args.start_date} to {args.end_date}...")
        items = client.articles(args.start_date, args.end_date, args.type)

        if not items:
            print(f"✗ No articles found for the specified date range")
            return 1

        print(f"✓ Found {len(items)} article{'s' if len(items) != 1 else ''}")

        # Optionally save JSON
        if args.save_json:
            if args.verbose:
                print(f"Saving JSON data to {args.save_json}...")
            import dataclasses
            # Convert CeoItem objects to dicts for JSON serialization
            items_dict = [dataclasses.asdict(item) for item in items]
            json_path = Path(args.save_json)
            json_path.parent.mkdir(parents=True, exist_ok=True)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump({'items': items_dict, 'total': len(items)}, f, ensure_ascii=False, indent=2)
            print(f"✓ Saved JSON to {args.save_json}")

        # Generate PDF
        generate_pdf(items, str(output_path), args.include_images)

        # Show file size
        file_size = output_path.stat().st_size
        size_mb = file_size / (1024 * 1024)
        print(f"  File size: {size_mb:.2f} MB")
        print(f"  Location: {output_path.absolute()}")

        return 0

    except KeyboardInterrupt:
        print("\n✗ Interrupted by user")
        return 130
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit(main())
