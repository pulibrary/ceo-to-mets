# Daily Princetonian METS Package Generator

A Python toolkit for generating METS (Metadata Encoding and Transmission Standard) packages for Daily Princetonian newspaper articles. This project creates standardized digital preservation packages with multiple format derivatives and comprehensive metadata.

## Overview

This project provides a complete workflow for converting Daily Princetonian articles into METS packages suitable for digital preservation and access. It generates multiple derivative formats (HTML, PDF, TXT, ALTO XML) along with standardized MODS metadata, all packaged according to the METS standard.

### Key Features

- **Multiple Format Generation**: Create HTML, PDF, plain text, and ALTO XML from article data
- **MODS Metadata**: Generate comprehensive descriptive metadata in MODS format
- **ALTO XML Support**: Produce layout and coordinate information with **word-level segmentation**
- **METS Packaging**: Bundle everything into standard METS containers with checksums
- **Demo Mode**: Test and learn without API access using sample articles

## Quick Start

### Prerequisites

- Python 3.12 or higher
- PDM (Python Development Master) or pip

### Installation

Using PDM (recommended):
```bash
pdm install
```

Using pip:
```bash
pip install -e .
```

After installation, the `dp-to-pdf` and `demo-mets` commands will be available in your environment.

### Generate Demo METS Package

Create a demo METS package with sample articles (no API access required):

```bash
# Create demo package in default location
demo-mets

# Specify custom output directory and date
demo-mets --output my_demo --date 2024-12-01

# Quiet mode (minimal output)
demo-mets --quiet

# Verbose mode (detailed progress)
demo-mets --verbose

# See all options
demo-mets --help
```

**Demo METS Options:**
- `--output` / `-o`: Output directory (default: demo_mets_output)
- `--date`: Issue date in YYYY-MM-DD format (default: 2025-10-15)
- `--verbose` / `-v`: Show detailed progress
- `--quiet` / `-q`: Minimal output

The demo package includes:
- Complete METS XML file with full metadata
- 3 sample articles (news, opinion, sports)
- All derivative formats (JSON, HTML, TXT, PDF, ALTO)
- Proper file structure for study and testing

### Fetch Articles and Generate PDFs

Fetch real articles from the Daily Princetonian API:

```bash
# Basic usage - fetch articles and create PDF
dp-to-pdf --start-date 2024-01-01 --end-date 2024-01-31

# Specify output file and include images
dp-to-pdf --start-date 2024-01-01 --end-date 2024-01-31 \
  --output january_articles.pdf \
  --include-images

# Fetch opinion articles and save JSON
dp-to-pdf --start-date 2024-01-01 --end-date 2024-01-31 \
  --type opinion \
  --save-json articles.json

# See all options
dp-to-pdf --help
```

**Available Options:**
- `--start-date` / `--end-date`: Date range for articles (YYYY-MM-DD)
- `--output` / `-o`: Output PDF filename (default: articles.pdf)
- `--type` / `-t`: Article type: article, opinion, or sports (default: article)
- `--include-images` / `-i`: Include featured images in PDF
- `--save-json`: Save raw article data as JSON
- `--verbose` / `-v`: Show detailed progress

## Project Structure

```
.
├── src/
│   ├── clients.py                    # API client and data models
│   ├── cli/
│   │   ├── dp_to_pdf.py              # CLI: fetch articles and generate PDF
│   │   └── demo_mets.py              # CLI: generate demo METS package
│   ├── generate_mets.py              # METS package generator (library)
│   └── generators/
│       ├── html_generator.py         # Generate formatted HTML
│       ├── pdf_generator.py          # Generate PDF from HTML
│       ├── txt_generator.py          # Extract plain text
│       ├── alto_generator.py         # Generate ALTO XML with word segmentation
│       └── mods_generator.py         # Generate MODS metadata
├── tests/                            # Comprehensive test suite (79 tests)
│   ├── conftest.py                   # Pytest fixtures
│   ├── data/                         # Test data files
│   └── test_*.py                     # Test modules
└── README.md                         # This file
```

## Command-Line Tools

The package provides two main command-line tools:

**1. `demo-mets`** - Generate demo METS packages without API access
- Perfect for learning, testing, and demonstrating METS structure
- Creates complete packages with sample articles
- No external dependencies or API keys required

**2. `dp-to-pdf`** - Fetch real articles and generate PDFs
- Connects to Daily Princetonian CEO API
- Downloads and formats articles by date range
- Generates professional PDFs with optional images

## Generators

### HTML Generator
Converts article data to formatted HTML using Jinja2 templates.

```python
from generators.html_generator import HTMLGenerator

html_gen = HTMLGenerator(article_item)
html_gen.generate("output/article.html")
```

### PDF Generator
Creates PDF documents from HTML using WeasyPrint.

```python
from generators.pdf_generator import PDFGenerator

pdf_gen = PDFGenerator(html_content)
pdf_gen.generate("output/article.pdf")
```

### TXT Generator
Extracts plain text from HTML content.

```python
from generators.txt_generator import TXTGenerator

txt_gen = TXTGenerator(article_item)
txt_gen.generate("output/article.txt")
```

### ALTO Generator
Generates ALTO v4.4 XML with word-level segmentation and coordinate information.

**New in latest version: Word-level segmentation!** Each word gets its own `<String>` element with precise bounding boxes, plus `<SP>` (space) elements between words.

```python
from generators.alto_generator import ALTOGenerator

alto_gen = ALTOGenerator("path/to/article.pdf", article_item)
alto_gen.generate("output/article.alto.xml")
```

See [WORD_SEGMENTATION_SUMMARY.md](WORD_SEGMENTATION_SUMMARY.md) for detailed documentation.

### MODS Generator
Creates MODS v3.7 metadata records.

```python
from generators.mods_generator import MODSGenerator

mods_gen = MODSGenerator(article_item)
mods_xml = mods_gen.generate_xml()
```

## Command-Line Tools

### Fetch Article and Generate PDF

```bash
python3 src/dp_to_pdf.py <article_id>
```

Example:
```bash
python3 src/dp_to_pdf.py 12345
```

### Generate METS Package from API

```bash
python3 src/generate_mets.py --date YYYY-MM-DD [--output-dir DIR]
```

Example:
```bash
python3 src/generate_mets.py --date 2025-10-15 --output-dir mets_packages
```

## Testing

Run the complete test suite:

```bash
pdm run test
```

Run tests with verbose output:

```bash
pdm run test_verbose
```

Run tests with coverage:

```bash
pytest --cov=generators --cov-report=html
```

### Test Coverage

The project includes comprehensive tests for:
- All generator classes
- ALTO word-level segmentation
- MODS metadata generation
- METS package structure
- PDF generation
- HTML formatting

## Output Examples

### METS Package Structure

```
mets_packages/
└── 2025-10-15/
    ├── mets.xml                          # Main METS file
    └── articles/
        ├── article-10001/
        │   ├── article-10001.json        # Raw article data
        │   ├── article-10001.html        # Formatted HTML
        │   ├── article-10001.txt         # Plain text
        │   ├── article-10001.pdf         # PDF document
        │   └── article-10001.alto.xml    # ALTO with word segmentation
        ├── article-10002/
        │   └── ...
        └── article-10003/
            └── ...
```

### ALTO Word Segmentation Example

```xml
<TextLine ID="TL_1_1_1" HPOS="101.02" VPOS="363.21" HEIGHT="12.50" WIDTH="382.34">
  <String ID="P1_ST00001" CONTENT="As" HPOS="101.02" VPOS="363.21"
          HEIGHT="12.50" WIDTH="12.34" WC="1.00"/>
  <SP ID="P1_SP00001" HPOS="113.36" VPOS="363.21" WIDTH="5.00"/>
  <String ID="P1_ST00002" CONTENT="students" HPOS="118.36" VPOS="363.21"
          HEIGHT="12.50" WIDTH="42.15" WC="1.00"/>
  <SP ID="P1_SP00002" HPOS="160.51" VPOS="363.21" WIDTH="5.00"/>
  <String ID="P1_ST00003" CONTENT="face" HPOS="165.51" VPOS="363.21"
          HEIGHT="12.50" WIDTH="24.20" WC="1.00"/>
  <!-- ... more words ... -->
</TextLine>
```

## Dependencies

### Core Dependencies
- **requests**: API client for fetching articles
- **weasyprint**: PDF generation from HTML
- **lxml**: XML processing for METS, MODS, and ALTO
- **jinja2**: HTML template rendering
- **html2text**: Plain text extraction
- **pymupdf**: PDF text extraction and word segmentation

### Development Dependencies
- **pytest**: Testing framework
- **pytest-cov**: Test coverage reporting
- **pytest-mock**: Mocking support
- **ruff**: Python linter
- **mypy**: Static type checking

## Standards Compliance

This project implements the following standards:

- **METS v1.12**: Metadata Encoding and Transmission Standard
- **MODS v3.7**: Metadata Object Description Schema
- **ALTO v4.4**: Analyzed Layout and Text Object (with word-level segmentation)

### References
- [METS Standard](https://www.loc.gov/standards/mets/)
- [MODS Standard](https://www.loc.gov/standards/mods/)
- [ALTO Standard](https://www.loc.gov/standards/alto/)

## Development

### Running Linter

```bash
pdm run lint
```

### Type Checking

```bash
pdm run typecheck
```

### Code Coverage

Generate HTML coverage report:

```bash
pdm run cov
pdm run cov_report  # Starts local server to view report
```

## Recent Updates

### Word-Level Segmentation (Latest)
- Added word-level segmentation to ALTO XML generator
- Each word now gets its own `<String>` element with accurate bounding boxes
- Added `<SP>` (space) elements between words
- Improved coordinate accuracy using PyMuPDF's word extraction
- Comprehensive test coverage for word segmentation features

See [WORD_SEGMENTATION_SUMMARY.md](WORD_SEGMENTATION_SUMMARY.md) for complete details.

## Use Cases

### Digital Preservation
Create standardized preservation packages for newspaper articles with comprehensive metadata and multiple access formats.

### Research and Analysis
Extract structured text with coordinate information for digital humanities research, text mining, and layout analysis.

### Archive Management
Generate METS packages that can be ingested into digital asset management systems and institutional repositories.

### Access Systems
Provide multiple derivative formats (HTML, PDF, text) for different access scenarios while maintaining format relationships through METS.

## Demo Mode

The `create_demo_mets.py` script is perfect for:
- **Learning**: Study METS/MODS/ALTO structure without API access
- **Testing**: Use sample data for development and testing
- **Documentation**: Reference implementation examples
- **Training**: Teach digital preservation workflows

The demo generates realistic sample articles covering news, opinion, and sports content.

## License

MIT License

## Author

**Cliff Wulfman** (cwulfman@princeton.edu)
Princeton University Library

## Contributing

This project is part of the Daily Princetonian digital archive initiative. For questions or contributions, please contact the author.

## Acknowledgments

- Built with support from Princeton University Library
- ALTO word segmentation powered by PyMuPDF
- PDF generation using WeasyPrint
- Standards compliance based on Library of Congress specifications
