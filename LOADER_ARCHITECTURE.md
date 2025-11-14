# Loader Architecture Analysis

## Use Case: Loading Articles from Multiple Sources

### Current Limitation
Right now, you can only load articles from the Daily Princetonian CEO API via `CeoClient`. But what if users have:
- JSONL file of pre-scraped articles
- CSV export from another CMS
- Parquet files from a data lake
- Database dump
- Another REST API
- RSS/Atom feeds
- Web scraping results

### Proposed Solution: Loader Abstraction

Create a **Loader** layer that sits between data sources and generators:

```
Data Sources        →    Loaders          →    Generators
────────────────         ─────────────         ──────────
CEO API             →    APILoader        →    HTMLGenerator
JSONL file          →    JSONLLoader      →    PDFGenerator
CSV file            →    CSVLoader        →    MODSGenerator
PostgreSQL DB       →    DatabaseLoader   →    ALTOGenerator
Web scraping        →    ScrapingLoader   →    TXTGenerator
```

## Architecture Options

### Option 1: Abstract Base Class (Simple)

**Complexity**: ⭐⭐ (Low-Medium)

```python
# loaders/base.py
from abc import ABC, abstractmethod
from typing import Iterator, Optional, Dict, Any
from generators.protocols import ArticleProtocol

class ArticleLoader(ABC):
    """
    Abstract base class for loading articles from various sources.

    Subclasses implement specific loading logic (API, files, database, etc.)
    """

    @abstractmethod
    def load(self) -> Iterator[ArticleProtocol]:
        """
        Load articles from the source.

        Yields:
            ArticleProtocol objects ready for use with generators
        """
        pass

    @abstractmethod
    def count(self) -> Optional[int]:
        """
        Return number of articles if known, None otherwise.

        Some sources (files) can report count upfront,
        others (APIs) may not know until loading.
        """
        pass


# loaders/api_loader.py
from clients import CeoClient, CeoItem

class CEOAPILoader(ArticleLoader):
    """Load articles from Daily Princetonian CEO API."""

    def __init__(self, start_date: str, end_date: str, article_type: str = "article"):
        self.start_date = start_date
        self.end_date = end_date
        self.article_type = article_type
        self.client = CeoClient()

    def load(self) -> Iterator[CeoItem]:
        """Load from API - returns CeoItem objects."""
        items = self.client.articles(self.start_date, self.end_date, self.article_type)
        yield from items

    def count(self) -> Optional[int]:
        """API doesn't provide count without fetching."""
        return None


# loaders/jsonl_loader.py
import json
from pathlib import Path
from typing import Iterator, Optional, Dict, Any
from generators.adapters import GenericArticle

class JSONLLoader(ArticleLoader):
    """
    Load articles from JSONL (JSON Lines) file.

    Each line should be a JSON object representing an article.
    Supports field mapping to convert source fields to our schema.
    """

    def __init__(
        self,
        file_path: str | Path,
        field_mapping: Optional[Dict[str, str]] = None,
        encoding: str = 'utf-8'
    ):
        """
        Initialize JSONL loader.

        Args:
            file_path: Path to JSONL file
            field_mapping: Maps our fields to source fields
                          e.g., {'headline': 'title', 'content': 'body'}
                          If None, assumes fields match our schema
            encoding: File encoding (default: utf-8)
        """
        self.file_path = Path(file_path)
        self.field_mapping = field_mapping or {}
        self.encoding = encoding

        if not self.file_path.exists():
            raise FileNotFoundError(f"JSONL file not found: {file_path}")

    def load(self) -> Iterator[GenericArticle]:
        """Load articles from JSONL file."""
        with open(self.file_path, 'r', encoding=self.encoding) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)

                    if self.field_mapping:
                        # Map source fields to our schema
                        article = GenericArticle.from_dict(data, self.field_mapping)
                    else:
                        # Assume fields already match
                        article = GenericArticle(**data)

                    yield article

                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON on line {line_num}: {e}")
                except Exception as e:
                    raise ValueError(f"Error processing line {line_num}: {e}")

    def count(self) -> int:
        """Count lines in file (fast for JSONL)."""
        with open(self.file_path, 'r', encoding=self.encoding) as f:
            return sum(1 for line in f if line.strip())
```

### Option 2: Protocol-Based (More Flexible)

**Complexity**: ⭐⭐⭐ (Medium)

```python
# loaders/protocols.py
from typing import Protocol, Iterator, Optional
from generators.protocols import ArticleProtocol

class LoaderProtocol(Protocol):
    """Protocol for article loaders."""

    def load(self) -> Iterator[ArticleProtocol]:
        """Load and yield articles."""
        ...

    def count(self) -> Optional[int]:
        """Return article count if available."""
        ...


# Now ANY object with load() and count() methods works!
# Don't need to inherit from a base class
```

### Option 3: Functional Approach (Pythonic)

**Complexity**: ⭐ (Very Low)

```python
# loaders/functions.py
from typing import Iterator, Dict, Any, Callable
from pathlib import Path
import json

def load_from_jsonl(
    file_path: str | Path,
    mapper: Callable[[Dict[str, Any]], ArticleProtocol]
) -> Iterator[ArticleProtocol]:
    """
    Load articles from JSONL file.

    Args:
        file_path: Path to JSONL file
        mapper: Function that converts JSON dict to ArticleProtocol

    Yields:
        ArticleProtocol objects
    """
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                yield mapper(data)


def load_from_api(start_date: str, end_date: str) -> Iterator[CeoItem]:
    """Load from CEO API."""
    client = CeoClient()
    yield from client.articles(start_date, end_date)


# Usage - simple and explicit
articles = load_from_jsonl('data.jsonl', mapper=lambda d: GenericArticle(**d))
# or
articles = load_from_api('2024-01-01', '2024-01-31')
```

## Recommended: Hybrid Approach

**Complexity**: ⭐⭐ (Low-Medium) - **Best bang for buck**

Combine the strengths of each approach:

```python
# loaders/__init__.py
"""
Article loaders for various data sources.

Loaders abstract the source of article data (API, files, database, etc.)
and provide a consistent interface for loading ArticleProtocol objects.
"""

from abc import ABC, abstractmethod
from typing import Iterator, Optional, Dict, Any, Callable
from pathlib import Path
import json
from generators.protocols import ArticleProtocol
from generators.adapters import GenericArticle


class ArticleLoader(ABC):
    """Base class for article loaders."""

    @abstractmethod
    def load(self) -> Iterator[ArticleProtocol]:
        """Load and yield articles."""
        pass

    def count(self) -> Optional[int]:
        """Return count if available. Override in subclasses."""
        return None

    def __iter__(self):
        """Make loader iterable."""
        return self.load()


# Simple loaders using base class
class JSONLLoader(ArticleLoader):
    """Load from JSONL file with field mapping support."""

    def __init__(
        self,
        file_path: str | Path,
        field_mapping: Optional[Dict[str, str]] = None,
        article_factory: Optional[Callable[[Dict], ArticleProtocol]] = None
    ):
        """
        Args:
            file_path: Path to JSONL file
            field_mapping: Map source fields to our schema
            article_factory: Custom function to create articles from dicts
                           If None, uses GenericArticle.from_dict
        """
        self.file_path = Path(file_path)
        self.field_mapping = field_mapping
        self.article_factory = article_factory or self._default_factory

        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

    def _default_factory(self, data: Dict[str, Any]) -> ArticleProtocol:
        """Default article creation."""
        if self.field_mapping:
            return GenericArticle.from_dict(data, self.field_mapping)
        return GenericArticle(**data)

    def load(self) -> Iterator[ArticleProtocol]:
        """Load articles from JSONL."""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):  # Support comments
                    continue

                try:
                    data = json.loads(line)
                    yield self.article_factory(data)
                except Exception as e:
                    raise ValueError(f"Error on line {line_num}: {e}") from e

    def count(self) -> int:
        """Count non-empty lines."""
        with open(self.file_path, 'r') as f:
            return sum(1 for line in f if line.strip() and not line.startswith('#'))


class CSVLoader(ArticleLoader):
    """Load from CSV file."""

    def __init__(
        self,
        file_path: str | Path,
        field_mapping: Dict[str, str],
        delimiter: str = ','
    ):
        self.file_path = Path(file_path)
        self.field_mapping = field_mapping
        self.delimiter = delimiter

    def load(self) -> Iterator[ArticleProtocol]:
        """Load from CSV."""
        import csv
        with open(self.file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=self.delimiter)
            for row in reader:
                yield GenericArticle.from_dict(row, self.field_mapping)

    def count(self) -> int:
        """Count rows (excluding header)."""
        import csv
        with open(self.file_path, 'r') as f:
            return sum(1 for _ in csv.DictReader(f, delimiter=self.delimiter))


class APILoader(ArticleLoader):
    """Load from Daily Princetonian CEO API."""

    def __init__(
        self,
        start_date: str,
        end_date: str,
        article_type: str = "article",
        client: Optional['CeoClient'] = None
    ):
        self.start_date = start_date
        self.end_date = end_date
        self.article_type = article_type
        # Allow dependency injection of client for testing
        self.client = client or CeoClient()

    def load(self) -> Iterator[ArticleProtocol]:
        """Load from API."""
        items = self.client.articles(
            self.start_date,
            self.end_date,
            self.article_type
        )
        yield from items


# Convenience functions for simple cases
def from_jsonl(
    file_path: str | Path,
    field_mapping: Optional[Dict[str, str]] = None
) -> Iterator[ArticleProtocol]:
    """
    Quick function to load from JSONL.

    Example:
        articles = from_jsonl('articles.jsonl', {'headline': 'title'})
    """
    return JSONLLoader(file_path, field_mapping).load()


def from_csv(
    file_path: str | Path,
    field_mapping: Dict[str, str],
    delimiter: str = ','
) -> Iterator[ArticleProtocol]:
    """Quick function to load from CSV."""
    return CSVLoader(file_path, field_mapping, delimiter).load()


def from_api(
    start_date: str,
    end_date: str,
    article_type: str = "article"
) -> Iterator[ArticleProtocol]:
    """Quick function to load from API."""
    return APILoader(start_date, end_date, article_type).load()
```

## Usage Examples

### Example 1: JSONL File with Field Mapping

```python
from loaders import JSONLLoader
from generators import HTMLGenerator, PDFGenerator

# JSONL file has different field names
# File content:
# {"title": "Breaking News", "body": "<p>Content</p>", "date": "2024-01-15"}
# {"title": "More News", "body": "<p>More content</p>", "date": "2024-01-16"}

# Create loader with field mapping
loader = JSONLLoader(
    'articles.jsonl',
    field_mapping={
        'headline': 'title',      # our field: source field
        'content': 'body',
        'published_at': 'date'
    }
)

# Load and generate
html_gen = HTMLGenerator()
html_gen.items = list(loader)  # Loader is iterable!
html_gen.generate()

pdf_gen = PDFGenerator(html_gen.html)
pdf_gen.dump('output.pdf')

print(f"Processed {loader.count()} articles")
```

### Example 2: CSV File

```python
from loaders import CSVLoader

# CSV file:
# Article Title,Article Content,Publication Date,Author
# "News Story","<p>Content</p>","2024-01-15","John Doe"

loader = CSVLoader(
    'articles.csv',
    field_mapping={
        'headline': 'Article Title',
        'content': 'Article Content',
        'published_at': 'Publication Date',
        'authors': 'Author'
    }
)

articles = list(loader)
```

### Example 3: Custom Article Factory

```python
from loaders import JSONLLoader
from dataclasses import dataclass

# Custom article type
@dataclass
class BlogPost:
    headline: str
    content: str
    published_at: str
    author_name: str = ""

    @property
    def authors(self) -> str:
        return f'[{{"name": "{self.author_name}"}}]'

# Custom factory function
def create_blog_post(data: dict) -> BlogPost:
    return BlogPost(
        headline=data['post_title'],
        content=data['post_content'],
        published_at=data['created_at'],
        author_name=data.get('author', 'Anonymous')
    )

loader = JSONLLoader('blogs.jsonl', article_factory=create_blog_post)
```

### Example 4: Multiple Sources

```python
from loaders import JSONLLoader, CSVLoader, APILoader
import itertools

# Load from multiple sources
api_articles = APILoader('2024-01-01', '2024-01-31')
jsonl_articles = JSONLLoader('archived_articles.jsonl')
csv_articles = CSVLoader('imported_articles.csv', mapping={...})

# Combine all sources
all_articles = itertools.chain(
    api_articles,
    jsonl_articles,
    csv_articles
)

# Generate from all sources
html_gen = HTMLGenerator()
html_gen.items = list(all_articles)
```

### Example 5: Streaming Large Files

```python
# Don't load everything into memory
loader = JSONLLoader('huge_file.jsonl')

# Process one at a time
for article in loader:
    # Generate individual files
    html_gen = HTMLGenerator()
    html_gen.items = [article]
    html_gen.generate()

    pdf_gen = PDFGenerator(html_gen.html)
    pdf_gen.dump(f'output/article_{article.id}.pdf')
```

## CLI Integration

### Updated dp-to-pdf CLI

```python
# src/cli/dp_to_pdf.py
def main():
    parser = argparse.ArgumentParser(...)

    # Add new options
    parser.add_argument(
        '--from-jsonl',
        metavar='FILE',
        help='Load articles from JSONL file instead of API'
    )
    parser.add_argument(
        '--from-csv',
        metavar='FILE',
        help='Load articles from CSV file instead of API'
    )
    parser.add_argument(
        '--field-mapping',
        metavar='JSON',
        help='JSON string mapping source fields to our schema'
    )

    args = parser.parse_args()

    # Determine loader based on arguments
    if args.from_jsonl:
        mapping = json.loads(args.field_mapping) if args.field_mapping else None
        loader = JSONLLoader(args.from_jsonl, field_mapping=mapping)
    elif args.from_csv:
        if not args.field_mapping:
            parser.error("--field-mapping required with --from-csv")
        mapping = json.loads(args.field_mapping)
        loader = CSVLoader(args.from_csv, field_mapping=mapping)
    else:
        # Original API behavior
        loader = APILoader(args.start_date, args.end_date, args.type)

    # Rest of code works the same
    items = list(loader)
    generate_pdf(items, args.output, args.include_images)
```

### New Usage

```bash
# Original - from API
dp-to-pdf --start-date 2024-01-01 --end-date 2024-01-31

# New - from JSONL file
dp-to-pdf --from-jsonl articles.jsonl --output articles.pdf

# New - from JSONL with field mapping
dp-to-pdf --from-jsonl scraped.jsonl \
  --field-mapping '{"headline":"title","content":"body","published_at":"date"}' \
  --output output.pdf

# New - from CSV
dp-to-pdf --from-csv export.csv \
  --field-mapping '{"headline":"Title","content":"Content"}' \
  --output output.pdf
```

## Complexity Analysis

### Added Complexity: ⭐⭐ (Low-Medium)

**New Files** (3-4 files):
- `src/loaders/__init__.py` - Base classes and exports
- `src/loaders/file_loaders.py` - JSONL, CSV loaders
- `src/loaders/api_loader.py` - API loader wrapper
- `tests/test_loaders.py` - Loader tests

**Lines of Code**:
- Base infrastructure: ~150 lines
- JSONL loader: ~80 lines
- CSV loader: ~60 lines
- API loader: ~40 lines
- Tests: ~200 lines
- **Total: ~530 lines**

**Maintenance**: Low - straightforward code, minimal dependencies

### Benefits vs. Complexity

**Huge Benefits**:
1. ✅ Users can process pre-scraped/archived data
2. ✅ Batch processing without API rate limits
3. ✅ Reproducible research (same data file)
4. ✅ Data lake integration (Parquet, database dumps)
5. ✅ Easy testing with fixture data
6. ✅ Cross-walk any data format

**Minimal Complexity**:
- Simple abstraction layer
- Each loader is independent
- Easy to understand and test
- Users can write custom loaders

## Recommended Implementation

### Phase 1: Core Infrastructure (2-3 hours)
1. Create `src/loaders/` package
2. Define `ArticleLoader` base class
3. Implement `JSONLLoader`
4. Add basic tests

### Phase 2: Additional Loaders (2 hours)
1. Implement `CSVLoader`
2. Wrap existing `CeoClient` in `APILoader`
3. Add comprehensive tests

### Phase 3: CLI Integration (1-2 hours)
1. Update `dp-to-pdf` to support file sources
2. Add `--from-jsonl` and `--from-csv` options
3. Update documentation

### Phase 4: Advanced Features (optional)
1. Database loader
2. Parquet loader
3. Multiple file loader (glob patterns)
4. Remote file loader (HTTP/S3)

## Example JSONL Field Mapping Config

For complex mappings, support config files:

```yaml
# field_mapping.yaml
source_format: wordpress_export
mapping:
  headline: post_title
  content: post_content
  published_at: post_date
  authors: post_author
  abstract: post_excerpt
  id: ID
  slug: post_name

transforms:
  # Optional transformations
  published_at: "datetime.strptime(value, '%Y-%m-%d %H:%M:%S')"
  authors: "json.dumps([{'name': value}])"
```

```python
# Load with config
loader = JSONLLoader('export.jsonl', config_file='field_mapping.yaml')
```

## Conclusion

**Recommendation: Implement the Loader abstraction**

**Why?**
- ⭐⭐⭐⭐⭐ **Very high value** for users
- ⭐⭐ **Low-medium complexity** to implement
- ✅ Unlocks many use cases (archives, batch processing, research)
- ✅ Fits perfectly with Protocol architecture
- ✅ Makes tool much more versatile
- ✅ Easy to extend with new sources

**Total Additional Complexity**: ~530 lines of code, 3-4 new files

**Return on Investment**: Excellent - significantly expands use cases with minimal complexity.

Should I proceed with implementation?
