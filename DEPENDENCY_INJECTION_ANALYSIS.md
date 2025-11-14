# Dependency Injection Analysis for Generators

## Current Architecture

### Hard Dependencies
The generators currently have hard dependencies on:
1. **`CeoItem`** - Specific dataclass from `clients` module
   - Used by: `HTMLGenerator`, `TXTGenerator`, `MODSGenerator`
2. **`weasyprint.HTML`** - PDF rendering library
   - Used by: `PDFGenerator`
3. **`PyMuPDF (fitz)`** - PDF text extraction
   - Used by: `ALTOGenerator`
4. **`Jinja2`** - Template engine
   - Used by: `HTMLGenerator`

### Current Coupling Points

```python
# HTMLGenerator
from clients import CeoItem
self.items: List[CeoItem] = list()

# TXTGenerator
from clients import CeoItem
self.item: CeoItem | None = None

# MODSGenerator
from clients import CeoItem
def __init__(self, item: CeoItem) -> None:
```

## Pros of Dependency Injection

### 1. **API Adaptability** ⭐⭐⭐⭐⭐
**High Value for Your Use Case**

Instead of being tied to `CeoItem`, you could support ANY news API:
```python
# Current - tightly coupled
generator = HTMLGenerator()
generator.items = [ceo_item1, ceo_item2]

# With DI - works with any API
class ArticleAdapter(Protocol):
    headline: str
    content: str
    authors: List[str]
    published_at: str
    # ... other required fields

generator = HTMLGenerator(article_adapter=MyNewsAPIAdapter())
generator.items = [news_api_item1, news_api_item2]
```

**Real-world benefit**: Support NYTimes API, AP News API, Reuters, etc. without changing generator code.

### 2. **Testing Improvements** ⭐⭐⭐⭐
**Significant Value**

```python
# Current - must create full CeoItem objects
def test_html_generator():
    item = CeoItem(
        id="1", uuid="abc", slug="test",
        headline="Test", content="...",
        # ... 25+ other required fields
    )

# With DI - mock only what you need
def test_html_generator():
    mock_article = Mock(spec=ArticleProtocol)
    mock_article.headline = "Test"
    mock_article.content = "Simple test"
    # ... only fields used in test
```

### 3. **Configuration Flexibility** ⭐⭐⭐⭐
**High Value**

```python
# Inject different renderers
pdf_gen = PDFGenerator(
    renderer=WeasyPrintRenderer(options={'dpi': 300})
    # or renderer=PlaywrightRenderer()
    # or renderer=PuppeteerRenderer()
)

# Inject different template engines
html_gen = HTMLGenerator(
    template_engine=Jinja2Engine()
    # or template_engine=MakoEngine()
    # or template_engine=CheetahEngine()
)
```

### 4. **Separation of Concerns** ⭐⭐⭐⭐
**Design Quality**

- Generators focus on generation logic
- Data access/adaptation is separate
- Each component has single responsibility
- Easier to understand and maintain

### 5. **Plugin Architecture** ⭐⭐⭐
**Medium Value**

```python
# Users can provide custom implementations
class CustomMODSMapper:
    def map_to_mods(self, article):
        # Custom mapping logic
        pass

mods_gen = MODSGenerator(mapper=CustomMODSMapper())
```

### 6. **Backward Compatibility** ⭐⭐⭐⭐
**Can be achieved with default parameters**

```python
# Still works the old way
generator = HTMLGenerator()  # Uses CeoItem by default
generator.items = [ceo_item]

# But also supports new way
generator = HTMLGenerator(adapter=GenericArticleAdapter)
```

## Cons of Dependency Injection

### 1. **Increased Complexity** ⚠️⚠️⚠️
**Moderate Concern**

- More interfaces/protocols to define
- More code to write and maintain
- Steeper learning curve for contributors
- More files in the codebase

**Mitigation**: Good documentation, clear examples, sensible defaults

### 2. **Verbosity** ⚠️⚠️
**Minor Concern**

```python
# Current - simple
gen = HTMLGenerator()

# With DI - more verbose
gen = HTMLGenerator(
    template_engine=Jinja2Engine(),
    article_adapter=CeoItemAdapter(),
    url_builder=DailyPrincetonianURLBuilder()
)
```

**Mitigation**: Use factory functions or builder pattern

### 3. **Over-Engineering Risk** ⚠️⚠️⚠️
**Real Risk**

If you only ever plan to use the Daily Princetonian API, DI might be unnecessary complexity.

**Question to ask**: Will you realistically support other news APIs in the next 2 years?

### 4. **Performance Overhead** ⚠️
**Very Minor**

- Extra function calls through interfaces
- In practice: negligible for I/O-bound operations
- Not a real concern for this use case

### 5. **Breaking Changes** ⚠️⚠️⚠️⚠️
**Significant Concern**

- Existing code using generators would need updates
- Tests would need refactoring
- CLI tools would need changes
- Documentation needs rewriting

**Mitigation**: Maintain backward compatibility with default parameters

## Recommended Approach

### Option 1: Protocol-Based DI (Recommended)
**Best for: Supporting multiple APIs while keeping it Pythonic**

```python
from typing import Protocol, List

class Article(Protocol):
    """Protocol defining what generators need from an article."""
    @property
    def headline(self) -> str: ...

    @property
    def content(self) -> str: ...

    @property
    def authors(self) -> List[str]: ...

    # ... other required properties

class HTMLGenerator(Generator):
    def __init__(self, article_type: type[Article] = CeoItem):
        self.article_type = article_type
        self.items: List[Article] = []
```

**Pros**:
- Type-safe
- No runtime dependency injection framework
- Works with existing CeoItem without changes
- Duck typing friendly (Pythonic)

### Option 2: Adapter Pattern
**Best for: Minimal changes to existing code**

```python
class ArticleAdapter(ABC):
    @abstractmethod
    def get_headline(self) -> str: pass

    @abstractmethod
    def get_content(self) -> str: pass

class CeoItemAdapter(ArticleAdapter):
    def __init__(self, item: CeoItem):
        self.item = item

    def get_headline(self) -> str:
        return self.item.headline

class HTMLGenerator(Generator):
    def __init__(self, adapter_class=CeoItemAdapter):
        self.adapter_class = adapter_class
```

**Pros**:
- Familiar OOP pattern
- Easier to understand
- Explicit conversion points

### Option 3: Hybrid - Protocols + Default Implementation
**Best for: Your use case**

```python
# Define minimal protocol
class ArticleData(Protocol):
    headline: str
    content: str
    authors: list[str]
    published_at: str

# CeoItem already satisfies this protocol!
# No changes needed to existing code

# Generator accepts anything matching protocol
class HTMLGenerator(Generator):
    def __init__(self):
        self.items: List[ArticleData] = []

    def generate(self, include_images: bool = False) -> None:
        # Works with CeoItem, or any compatible type
        for item in self.items:
            headline = item.headline  # Protocol guarantees this exists
```

**Pros**:
- Minimal code changes
- Backward compatible
- Opens door for other APIs
- Type-safe
- No runtime overhead

## My Recommendation

**Implement Option 3: Protocols + Type Hints**

### Why?

1. ✅ **Zero breaking changes** - CeoItem already works as-is
2. ✅ **Opens extensibility** - Other APIs can be added easily
3. ✅ **Minimal complexity** - Just define protocols, no DI framework
4. ✅ **Type safety** - MyPy will catch issues
5. ✅ **Pythonic** - Uses Python's structural typing (PEP 544)
6. ✅ **Documentation value** - Protocols clearly show what's needed

### Implementation Strategy

1. **Phase 1**: Define Article protocols (no code changes needed)
2. **Phase 2**: Update type hints to use protocols instead of CeoItem
3. **Phase 3**: Document how to support other APIs
4. **Phase 4** (optional): Extract PDF/ALTO rendering to injectable components

### When NOT to use DI

Don't inject dependencies for:
- **weasyprint** - It's the standard for HTML→PDF in Python
- **PyMuPDF** - Best library for PDF text extraction
- **lxml** - Standard for XML in Python

These are implementation details, not business logic. The choice of library is not a concern for API adaptation.

## Example Implementation

I can show you what this would look like in practice if you'd like to proceed!

## Questions to Consider

1. **Do you plan to support other news APIs?** (NYTimes, AP, Reuters, etc.)
   - Yes → Go with DI
   - No → Keep it simple

2. **Is this primarily for Princeton use, or a general tool?**
   - Princeton only → Less need for DI
   - General tool → Strong case for DI

3. **What's your tolerance for complexity vs. flexibility?**
   - Want simple, focused tool → Avoid DI
   - Want extensible framework → Embrace DI

4. **How much existing code would break?**
   - A lot → Be very careful
   - Not much → Easier to implement

## My Take

Given that you have:
- Working code with 79 passing tests
- Specific use case (Daily Princetonian)
- Good test coverage
- CLI tools in production

I'd recommend: **Start with Protocol-based type hints (Option 3)**

This gives you:
- Flexibility for the future
- No breaking changes now
- Clear documentation of requirements
- Easy path to support other APIs later if needed

You get 80% of the benefits with 20% of the complexity.
