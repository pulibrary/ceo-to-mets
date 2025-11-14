# Protocol-Based Architecture Example

This document shows a concrete example of how to refactor the generators to use Protocols for better modularity and API independence.

## Before: Tightly Coupled to CeoItem

```python
# generators/html_generator.py
from clients import CeoItem

class HTMLGenerator(Generator):
    def __init__(self):
        self.items: List[CeoItem] = list()  # Hard dependency on CeoItem

    def generate(self, include_images: bool = False) -> None:
        for item in self.items:
            # Directly accesses CeoItem properties
            headline = item.headline
            content = item.content
```

**Problem**: Can only work with Daily Princetonian's CeoItem.

## After: Protocol-Based (Backward Compatible)

### Step 1: Define the Protocol

```python
# generators/protocols.py
"""
Protocols defining interfaces for article data.

These protocols specify the minimum interface that article objects
must implement to work with the generators. Any object that provides
these properties can be used, regardless of its class.
"""

from typing import Protocol, Optional, List, runtime_checkable


@runtime_checkable
class ArticleProtocol(Protocol):
    """
    Minimum interface required for article objects.

    Any class that provides these properties can be used with the generators,
    including CeoItem from Daily Princetonian or articles from other APIs.
    """

    # Required fields
    @property
    def headline(self) -> str:
        """Article headline/title."""
        ...

    @property
    def content(self) -> str:
        """Main article content (may include HTML)."""
        ...

    @property
    def published_at(self) -> str:
        """Publication date/time as string."""
        ...

    # Optional fields
    @property
    def subhead(self) -> Optional[str]:
        """Article subheadline."""
        ...

    @property
    def abstract(self) -> Optional[str]:
        """Article abstract/summary."""
        ...

    @property
    def authors(self) -> Optional[str]:
        """Authors (JSON string or list)."""
        ...


@runtime_checkable
class IdentifiableArticle(ArticleProtocol, Protocol):
    """Article with unique identifier."""

    @property
    def id(self) -> str:
        """Unique article identifier."""
        ...

    @property
    def slug(self) -> str:
        """URL-friendly slug."""
        ...


@runtime_checkable
class MetadataArticle(IdentifiableArticle, Protocol):
    """Article with full metadata for MODS generation."""

    @property
    def tags(self) -> Optional[str]:
        """Article tags/categories."""
        ...

    @property
    def seo_title(self) -> Optional[str]:
        """SEO-optimized title."""
        ...

    @property
    def seo_description(self) -> Optional[str]:
        """SEO description."""
        ...
```

### Step 2: Update Generators (No Breaking Changes!)

```python
# generators/html_generator.py
from typing import List, Union
from .protocols import ArticleProtocol
from clients import CeoItem  # Still imported for backward compatibility

class HTMLGenerator(Generator):
    def __init__(self):
        # Accept any ArticleProtocol-compatible object
        # CeoItem works automatically because it already has these properties!
        self.items: List[ArticleProtocol] = list()

    def generate(self, include_images: bool = False) -> None:
        for item in self.items:
            # Same code as before - no changes needed!
            headline = item.headline  # Works with any ArticleProtocol
            content = item.content
            # ... rest of generation logic
```

**Key point**: CeoItem automatically satisfies ArticleProtocol because it has all the required properties. No changes needed!

### Step 3: Supporting Other APIs

Now you can easily support other news APIs:

```python
# example_nytimes.py
"""Example: Using generators with New York Times API."""

from dataclasses import dataclass
from typing import Optional
from generators import HTMLGenerator, TXTGenerator, MODSGenerator

# Define NYTimes article structure
@dataclass
class NYTimesArticle:
    """Article from NYTimes API."""
    # NYTimes uses different field names
    title: str  # Instead of 'headline'
    body: str   # Instead of 'content'
    pub_date: str  # Instead of 'published_at'
    abstract_text: Optional[str] = None
    byline: Optional[str] = None
    article_id: str = ""
    web_url: str = ""

    # Adapter properties to match ArticleProtocol
    @property
    def headline(self) -> str:
        return self.title

    @property
    def content(self) -> str:
        return self.body

    @property
    def published_at(self) -> str:
        return self.pub_date

    @property
    def abstract(self) -> Optional[str]:
        return self.abstract_text

    @property
    def authors(self) -> Optional[str]:
        return self.byline

    @property
    def id(self) -> str:
        return self.article_id

    @property
    def slug(self) -> str:
        # Generate slug from URL
        return self.web_url.split('/')[-1].replace('.html', '')

# Now it works with generators!
nyt_article = NYTimesArticle(
    title="Breaking News",
    body="<p>Article content...</p>",
    pub_date="2024-01-15",
    article_id="nyt-12345"
)

# Same generators work with NYTimes data
html_gen = HTMLGenerator()
html_gen.items = [nyt_article]  # ✅ Works!
html_gen.generate()

txt_gen = TXTGenerator()
txt_gen.item = nyt_article  # ✅ Works!
```

### Step 4: Generic Adapter (For APIs without adaptation)

```python
# generators/adapters.py
"""
Adapters for converting various article formats to work with generators.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from .protocols import MetadataArticle


@dataclass
class GenericArticle:
    """
    Generic article adapter for any news API.

    Use this when the source API doesn't match ArticleProtocol.
    """

    headline: str
    content: str
    published_at: str
    id: str = ""
    slug: str = ""
    subhead: Optional[str] = None
    abstract: Optional[str] = None
    authors: Optional[str] = None
    tags: Optional[str] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any], field_mapping: Dict[str, str]) -> 'GenericArticle':
        """
        Create article from dictionary with custom field mapping.

        Args:
            data: Source data dictionary
            field_mapping: Maps our field names to source field names
                          e.g., {'headline': 'title', 'content': 'body'}

        Example:
            >>> article_data = {'title': 'News', 'body': 'Content...'}
            >>> mapping = {'headline': 'title', 'content': 'body'}
            >>> article = GenericArticle.from_dict(article_data, mapping)
        """
        kwargs = {}
        for our_field, source_field in field_mapping.items():
            if source_field in data:
                kwargs[our_field] = data[source_field]
        return cls(**kwargs)


# Example usage with a custom API
api_response = {
    'article_title': 'Breaking News',
    'article_body': '<p>Content here</p>',
    'publication_date': '2024-01-15',
    'author_names': 'John Doe, Jane Smith'
}

mapping = {
    'headline': 'article_title',
    'content': 'article_body',
    'published_at': 'publication_date',
    'authors': 'author_names'
}

article = GenericArticle.from_dict(api_response, mapping)

# Works with all generators
html_gen = HTMLGenerator()
html_gen.items = [article]  # ✅ Works!
```

## Benefits Demonstrated

### 1. Zero Breaking Changes
```python
# Old code still works exactly the same
from clients import CeoItem

item = CeoItem(...)
gen = HTMLGenerator()
gen.items = [item]  # ✅ Still works!
```

### 2. Easy Extension
```python
# New code can use any compatible type
from my_api import MyArticle

article = MyArticle(...)
gen = HTMLGenerator()
gen.items = [article]  # ✅ Works if it has required properties!
```

### 3. Type Safety
```python
# MyPy catches issues at development time
gen = HTMLGenerator()
gen.items = [{"headline": "test"}]  # ❌ MyPy error: dict doesn't match protocol

gen.items = [article]  # ✅ MyPy verifies protocol compatibility
```

### 4. Clear Documentation
```python
# Protocol clearly documents what's needed
# No need to read through generator code to understand requirements
from generators.protocols import ArticleProtocol

# Anyone can see what properties are required
help(ArticleProtocol)
```

## Migration Path

### Phase 1: Add Protocols (No Breaking Changes)
1. Create `generators/protocols.py`
2. Define `ArticleProtocol` and related protocols
3. Update type hints in generators
4. **All existing code still works**

### Phase 2: Document Extension Points
1. Add documentation showing how to support other APIs
2. Add examples (like NYTimes example above)
3. Update README with protocol documentation

### Phase 3: Optional - Add Adapters
1. Create `generators/adapters.py`
2. Add `GenericArticle` for easy adaptation
3. Provide utility functions for common conversions

### Phase 4: Optional - Extract Rendering
1. Create protocols for PDF rendering
2. Create protocols for XML generation
3. Allow custom implementations (low priority)

## Real-World Example: Support Multiple News Sources

```python
# main.py
"""
Example: Multi-source news aggregator using the same generators.
"""

from generators import HTMLGenerator, PDFGenerator
from clients import CeoClient, CeoItem  # Daily Princetonian
from nytimes_client import NYTimesClient  # Hypothetical
from ap_news_client import APNewsClient    # Hypothetical

# Fetch from multiple sources
dp_client = CeoClient()
nyt_client = NYTimesClient()
ap_client = APNewsClient()

# All return ArticleProtocol-compatible objects
dp_articles = dp_client.articles("2024-01-01", "2024-01-31", "news")
nyt_articles = nyt_client.search(query="university", date="2024-01-01")
ap_articles = ap_client.get_education_news("2024-01-01")

# Combine articles from different sources
all_articles = dp_articles + nyt_articles + ap_articles

# Same generators work with all sources!
html_gen = HTMLGenerator()
html_gen.items = all_articles
html_gen.generate()

pdf_gen = PDFGenerator(html_gen.html)
pdf_gen.dump("multi_source_news.pdf")
```

## Testing Benefits

```python
# Before: Need to create full CeoItem for every test
def test_html_generator():
    item = CeoItem(
        id="1", uuid="abc-123", slug="test-article",
        seo_title="Test", seo_description="Test description",
        seo_image="", headline="Test Headline",
        subhead="Test Subhead", abstract="Test abstract",
        content="<p>Test content</p>", infobox="",
        template="article", short_token="test",
        status="published", weight="0", media_id="",
        created_at="2024-01-01 10:00:00",
        modified_at="2024-01-01 11:00:00",
        published_at="2024-01-01 12:00:00",
        metadata="{}", hits="100",
        normalized_tags="test,article",
        ceo_id="1", ssts_id="", ssts_path="",
        tags='[{"name": "Test"}]',
        authors='[{"name": "Test Author"}]',
        dominantMedia=""
    )
    # ... test code

# After: Create minimal test objects
from dataclasses import dataclass

@dataclass
class SimpleArticle:
    headline: str
    content: str
    published_at: str
    subhead: str = ""
    abstract: str = ""
    authors: str = ""

def test_html_generator():
    item = SimpleArticle(
        headline="Test",
        content="<p>Simple content</p>",
        published_at="2024-01-01"
    )
    # ... test code
```

## Conclusion

The Protocol-based approach gives you:
- ✅ No breaking changes
- ✅ Easy to support other APIs
- ✅ Type safety
- ✅ Better testing
- ✅ Clear documentation
- ✅ Pythonic design
- ✅ Minimal complexity

All with just adding one protocols.py file and updating type hints!
