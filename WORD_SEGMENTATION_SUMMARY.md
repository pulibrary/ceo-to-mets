# Word-Level Segmentation Implementation for ALTO Files

## Overview

The ALTOGenerator class has been successfully extended to support word-level segmentation in ALTO XML files. Previously, the generator created one `<String>` element per line containing all the text. Now it creates individual `<String>` elements for each word with accurate bounding boxes, and adds `<SP>` (space) elements between words.

## Changes Made

### 1. Modified `extract_layout_from_pdf()` (src/generators/alto_generator.py:86-227)

**Key improvements:**
- Uses PyMuPDF's `get_text("words")` method to extract individual words with precise bounding boxes
- Creates a word map structure: `(block_no, line_no) -> list of word dictionaries`
- Each word dictionary contains: `{'text': word_text, 'bbox': [x0, y0, x1, y1]}`
- Implements a fallback mechanism that manually splits spans into words when word-level data is unavailable

**Algorithm:**
```python
# Get word-level information from PyMuPDF
words = page.get_text("words")  # Returns (x0, y0, x1, y1, word, block_no, line_no, word_no)

# Build mapping of (block_no, line_no) -> list of words
word_map = defaultdict(list)
for word_tuple in words:
    if len(word_tuple) >= 7:
        x0, y0, x1, y1, word_text, block_no, line_no = word_tuple[:7]
        word_map[(block_no, line_no)].append({
            'text': word_text,
            'bbox': [x0, y0, x1, y1]
        })

# For each line, create ALTOString objects from words
for word_info in line_words:
    alto_string = ALTOString(
        content=word_text,
        hpos=bbox[0],
        vpos=bbox[1],
        width=bbox[2] - bbox[0],
        height=bbox[3] - bbox[1],
        wc=1.0
    )
```

**Fallback behavior:**
- If word-level data is not available from PyMuPDF, the code splits span text manually
- Estimates word positions based on character count ratios
- Ensures compatibility with various PDF formats

### 2. Modified `generate_alto_xml()` (src/generators/alto_generator.py:308-351)

**Key improvements:**
- Generates `<String>` elements for each word with updated ID format: `P{page}_ST{index:05d}`
- Inserts `<SP>` elements between consecutive words with ID format: `P{page}_SP{index:05d}`
- Calculates space dimensions dynamically:
  - `space_hpos = current_word.hpos + current_word.width`
  - `space_width = next_word.hpos - space_hpos`
- Only adds SP elements when `space_width > 0`

**XML Structure:**
```xml
<TextLine ID="TL_1_1_1" HPOS="101.02" VPOS="363.21" HEIGHT="12.50" WIDTH="382.34">
  <String ID="P1_ST00001" CONTENT="As" HPOS="101.02" VPOS="363.21" HEIGHT="12.50" WIDTH="12.34" WC="1.00"/>
  <SP ID="P1_SP00001" HPOS="113.36" VPOS="363.21" WIDTH="5.00"/>
  <String ID="P1_ST00002" CONTENT="students" HPOS="118.36" VPOS="363.21" HEIGHT="12.50" WIDTH="42.15" WC="1.00"/>
  <SP ID="P1_SP00002" HPOS="160.51" VPOS="363.21" WIDTH="5.00"/>
  <String ID="P1_ST00003" CONTENT="face" HPOS="165.51" VPOS="363.21" HEIGHT="12.50" WIDTH="24.20" WC="1.00"/>
  <!-- ... more words ... -->
</TextLine>
```

### 3. Added Comprehensive Tests (tests/test_alto_generator.py)

Three new test methods were added:

#### `test_alto_has_word_level_segmentation()`
- Verifies that `<String>` elements are created
- Checks that all required attributes are present (ID, CONTENT, HPOS, VPOS, WIDTH, HEIGHT, WC)

#### `test_alto_has_space_elements()`
- Verifies that `<SP>` elements are inserted between words
- Ensures SP elements have required attributes (ID, HPOS, VPOS, WIDTH)

#### `test_alto_word_segmentation_content()`
- Validates that each `<String>` element contains individual words (not multi-word strings)
- Ensures proper word splitting

## Before vs After Comparison

### Before (Line-Level)
```xml
<TextBlock ID="TB_1_6" HPOS="101.02" VPOS="363.21" HEIGHT="12.50" WIDTH="382.34">
  <TextLine ID="TL_1_6_1" HPOS="101.02" VPOS="363.21" HEIGHT="12.50" WIDTH="382.34">
    <String ID="S_1_6_1_1"
            CONTENT="As students face mounting pressures, our current mental health resources are"
            HPOS="101.02"
            VPOS="363.21"
            HEIGHT="12.50"
            WIDTH="382.34"
            WC="1.00"/>
  </TextLine>
</TextBlock>
```

### After (Word-Level with Spaces)
```xml
<TextBlock ID="TB_1_6" HPOS="101.02" VPOS="363.21" HEIGHT="12.50" WIDTH="382.34">
  <TextLine ID="TL_1_6_1" HPOS="101.02" VPOS="363.21" HEIGHT="12.50" WIDTH="382.34">
    <String ID="P1_ST00001" CONTENT="As" HPOS="101.02" VPOS="363.21" HEIGHT="12.50" WIDTH="12.34" WC="1.00"/>
    <SP ID="P1_SP00001" HPOS="113.36" VPOS="363.21" WIDTH="5.00"/>
    <String ID="P1_ST00002" CONTENT="students" HPOS="118.36" VPOS="363.21" HEIGHT="12.50" WIDTH="42.15" WC="1.00"/>
    <SP ID="P1_SP00002" HPOS="160.51" VPOS="363.21" WIDTH="5.00"/>
    <String ID="P1_ST00003" CONTENT="face" HPOS="165.51" VPOS="363.21" HEIGHT="12.50" WIDTH="24.20" WC="1.00"/>
    <SP ID="P1_SP00003" HPOS="189.71" VPOS="363.21" WIDTH="5.00"/>
    <!-- ... additional words ... -->
  </TextLine>
</TextBlock>
```

## Technical Details

### PyMuPDF Word Extraction
PyMuPDF's `get_text("words")` method returns a list of tuples:
```python
(x0, y0, x1, y1, "word", block_no, line_no, word_no)
```

Where:
- `x0, y0, x1, y1`: Bounding box coordinates (left, top, right, bottom)
- `"word"`: The text content of the word
- `block_no`: Block number in the page
- `line_no`: Line number within the block
- `word_no`: Word number within the line

### ALTO v4.4 Compliance
The implementation maintains full compliance with the ALTO v4.4 standard:
- All required attributes are present
- Proper namespace usage: `http://www.loc.gov/standards/alto/ns-v4#`
- Valid element hierarchy: `Page > PrintSpace > TextBlock > TextLine > (String | SP)`
- Coordinate system in pixels

## Benefits

1. **Precise Word Boundaries**: Each word has accurate bounding box coordinates from PyMuPDF's layout analysis
2. **Enhanced Search Capabilities**: Enables word-level text searching and highlighting
3. **OCR Workflow Compatibility**: Compatible with standard ALTO-based OCR and document analysis workflows
4. **Explicit Space Information**: SP elements provide precise space dimensions and positions
5. **Backward Compatibility**: Maintains existing block/line structure hierarchy
6. **Robust Fallback**: Manual word splitting ensures compatibility with various PDF formats

## Files Modified

```
src/generators/alto_generator.py
├── extract_layout_from_pdf() [lines 86-227]
│   ├── Added word-level extraction using PyMuPDF
│   ├── Created word mapping structure
│   └── Implemented fallback word splitting
└── generate_alto_xml() [lines 308-351]
    ├── Updated String element generation
    ├── Added SP element insertion
    └── Updated ID format for String and SP elements

tests/test_alto_generator.py
├── test_alto_has_word_level_segmentation()
├── test_alto_has_space_elements()
└── test_alto_word_segmentation_content()
```

## Usage

The implementation is transparent to existing code. Simply use the ALTOGenerator as before:

```python
from generators.alto_generator import ALTOGenerator

# Create generator
generator = ALTOGenerator("path/to/document.pdf")

# Generate ALTO XML file with word-level segmentation
generator.generate("output/document.alto.xml")

# Or get as string
alto_xml_string = generator.to_string()
```

The generated ALTO files will now automatically include word-level segmentation with SP elements.

## Testing

Run the test suite to verify the implementation:

```bash
pytest tests/test_alto_generator.py -v
```

Or run specific word segmentation tests:

```bash
pytest tests/test_alto_generator.py::TestALTOGenerator::test_alto_has_word_level_segmentation -v
pytest tests/test_alto_generator.py::TestALTOGenerator::test_alto_has_space_elements -v
pytest tests/test_alto_generator.py::TestALTOGenerator::test_alto_word_segmentation_content -v
```

## Future Enhancements

Potential improvements for future iterations:

1. **Character Confidence (CC)**: Add character-level confidence scores (currently not provided by PyMuPDF for PDF extraction)
2. **Hyphenation Detection**: Detect and mark hyphenated words that span lines
3. **Font Information**: Include font family, size, and style attributes
4. **Language Detection**: Add language hints for multilingual documents
5. **Reading Order**: Implement explicit reading order attributes

## References

- [ALTO v4.4 Schema Documentation](http://www.loc.gov/standards/alto/v4/alto-4-4.xsd)
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)
- [ALTO Standard Homepage](https://www.loc.gov/standards/alto/)
