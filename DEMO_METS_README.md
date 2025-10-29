# Demo METS Package Generator

This script creates a demonstration METS (Metadata Encoding and Transmission Standard) package with sample Daily Princetonian articles for study and testing purposes.

## What it Does

The `create_demo_mets.py` script generates a complete METS package without requiring API access. It creates:

- **3 sample articles** covering different content types:
  - News: Campus sustainability initiative announcement
  - Opinion: Student mental health resources editorial
  - Sports: Women's soccer championship coverage

- **Multiple format derivatives** for each article:
  - **JSON**: Raw article data
  - **HTML**: Formatted article for web viewing
  - **TXT**: Plain text extraction
  - **PDF**: Formatted PDF document

- **Complete METS XML** with:
  - Descriptive metadata (MODS format)
  - File section with checksums and file references
  - Structural map showing issue organization

## Running the Script

### Prerequisites

Install dependencies first:
```bash
pdm install
```

### Generate Demo Package

```bash
python3 create_demo_mets.py
```

Or if using PDM:
```bash
pdm run python create_demo_mets.py
```

## Output Structure

The script creates the following directory structure:

```
demo_mets_output/
└── 2025-10-15/
    ├── mets.xml                          # Main METS file
    └── articles/
        ├── article-10001/
        │   ├── article-10001.json        # Raw data
        │   ├── article-10001.html        # Web format
        │   ├── article-10001.txt         # Plain text
        │   └── article-10001.pdf         # PDF format
        ├── article-10002/
        │   ├── article-10002.json
        │   ├── article-10002.html
        │   ├── article-10002.txt
        │   └── article-10002.pdf
        └── article-10003/
            ├── article-10003.json
            ├── article-10003.html
            ├── article-10003.txt
            └── article-10003.pdf
```

## What You Can Learn

### 1. METS Structure
Open `mets.xml` to see:
- How metadata is organized using MODS format
- File section with checksums and MIME types
- Structural map showing relationships between files
- XML namespaces and schema references

### 2. Generator Usage
The script demonstrates:
- Creating `CeoItem` objects from sample data
- Using `HTMLGenerator` for formatted HTML output
- Using `PDFGenerator` to create PDF files
- Using `TXTGenerator` for plain text extraction
- Using `MODSGenerator` for metadata

### 3. MODS Metadata
Examine how articles are described:
- Title and subtitle encoding
- Author information
- Publication dates
- Abstracts and subjects/tags
- Identifiers and URLs

### 4. File Organization
Study how digital objects are:
- Organized into logical groupings
- Referenced with file pointers
- Documented with checksums
- Described with MIME types

## Use Cases

- **Learning METS**: Study the XML structure without needing API access
- **Testing**: Use as test data for METS processing tools
- **Development**: Reference implementation for METS generation
- **Documentation**: Example of complete digital newspaper issue package
- **Validation**: Verify METS XML against schema validators

## Sample Articles

### Article 1: News (ID: 10001)
**Headline**: "Campus Announces Ambitious Sustainability Initiative"
- Multi-paragraph news story with quotes
- Includes bullet list of initiatives
- Multiple authors

### Article 2: Opinion (ID: 10002)
**Headline**: "We Need to Talk About Mental Health on Campus"
- Student opinion piece
- Personal narrative style
- Advocacy and recommendations

### Article 3: Sports (ID: 10003)
**Headline**: "Women's Soccer Advances to Finals in Overtime Thriller"
- Game coverage with play-by-play
- Player quotes and statistics
- Championship implications

## Technical Details

- **Namespaces**: Uses standard METS and MODS namespaces
- **Schema**: References official LOC schemas
- **Checksums**: MD5 hashes for file integrity
- **Paths**: Relative file references for portability
- **Encoding**: UTF-8 throughout

## Related Scripts

- `dp_to_pdf.py`: Fetch real articles from API and generate PDF
- `generate_mets.py`: Generate METS package from API data
- `test_mods_quick.py`: Quick test of MODS generator

## Questions?

This demo package illustrates the complete workflow from article data through multiple format derivatives to final METS packaging. It's designed to be self-contained and educational.

For more information about METS: https://www.loc.gov/standards/mets/
For more information about MODS: https://www.loc.gov/standards/mods/
