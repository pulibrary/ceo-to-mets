#!/usr/bin/env python3
"""
Fetch articles from Daily Princetonian API and generate PDF
Usage: python dp_to_pdf.py --start-date 2025-10-07 --end-date 2025-10-09
"""

import argparse
import json
from datetime import datetime

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
    html_generator = HTMLGenerator(items, include_images=include_images)

    # Generate PDF using PDFGenerator
    pdf_generator = PDFGenerator(html_generator.html)
    pdf_generator.dump(output_file)

    print(f"✓ PDF created successfully!")

def main():
    parser = argparse.ArgumentParser(
        description='Fetch Daily Princetonian articles and convert to PDF'
    )
    parser.add_argument(
        '--start-date',
        required=True,
        help='Start date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--end-date',
        required=True,
        help='End date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--output',
        default='articles.pdf',
        help='Output PDF filename (default: articles.pdf)'
    )
    parser.add_argument(
        '--type',
        default='article',
        choices=['article', 'opinion', 'sports'],
        help='Article type (default: article)'
    )
    parser.add_argument(
        '--include-images',
        action='store_true',
        help='Include featured images in PDF'
    )
    parser.add_argument(
        '--save-json',
        help='Also save raw JSON to this file'
    )
    
    args = parser.parse_args()

    try:
        # Initialize CeoClient
        client = CeoClient()

        # Fetch articles using CeoClient
        print(f"Fetching articles from {args.start_date} to {args.end_date}...")
        items = client.articles(args.start_date, args.end_date, args.type)

        if not items:
            print(f"✗ No articles found for the specified date range")
            return 1

        print(f"✓ Found {len(items)} articles")

        # Optionally save JSON
        if args.save_json:
            import dataclasses
            # Convert CeoItem objects to dicts for JSON serialization
            items_dict = [dataclasses.asdict(item) for item in items]
            with open(args.save_json, 'w', encoding='utf-8') as f:
                json.dump({'items': items_dict, 'total': len(items)}, f, ensure_ascii=False, indent=4)
            print(f"✓ Saved JSON to {args.save_json}")

        # Generate PDF
        generate_pdf(items, args.output, args.include_images)

        return 0

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit(main())
