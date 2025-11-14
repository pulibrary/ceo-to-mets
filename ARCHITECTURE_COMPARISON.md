# Architecture Comparison: Current vs. Proposed

## Current Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI / User Code                          │
│  (dp-to-pdf, demo-mets, custom scripts)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │    CeoClient     │ ◄── Hard-coded to Daily Princetonian API
              │  (CEO API only)  │
              └─────────┬────────┘
                        │
                        ▼
                  ┌──────────┐
                  │ CeoItem  │ ◄── Specific dataclass
                  └────┬─────┘
                       │
        ┌──────────────┼──────────────┬──────────────┐
        │              │              │              │
        ▼              ▼              ▼              ▼
┌──────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
│    HTML      │ │   TXT    │ │   MODS   │ │     PDF      │
│  Generator   │ │Generator │ │Generator │ │  Generator   │
└──────┬───────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘
       │              │            │              │
       └──────────────┴────────────┴──────────────┘
                      │
                      ▼
              ┌──────────────┐
              │ ALTO Generator│
              └──────────────┘
```

**Limitations**:
- ❌ Can only use Daily Princetonian CEO API
- ❌ Can't process pre-existing data files
- ❌ Can't support other news sources
- ❌ Testing requires full CeoItem objects
- ❌ No batch processing from archives

## Proposed Architecture with Protocols + Loaders

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLI / User Code                             │
│         (dp-to-pdf, demo-mets, custom scripts)                      │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                ┌────────────┴─────────────┐
                │   Choose Data Source      │
                └────────┬─────────────────┘
                         │
        ┌────────────────┼────────────────┬──────────────┐
        │                │                │              │
        ▼                ▼                ▼              ▼
┌──────────────┐  ┌─────────────┐  ┌──────────┐  ┌──────────────┐
│  APILoader   │  │ JSONLLoader │  │CSVLoader │  │  Custom      │
│              │  │             │  │          │  │  Loader      │
│ ┌──────────┐ │  │             │  │          │  │              │
│ │CeoClient │ │  │             │  │          │  │              │
│ └──────────┘ │  │             │  │          │  │              │
└──────┬───────┘  └──────┬──────┘  └────┬─────┘  └──────┬───────┘
       │                 │               │               │
       └─────────────────┴───────────────┴───────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  ArticleProtocol    │ ◄── Interface, not specific class
              │   (any source)      │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  GenericArticle     │ ◄── Adapter for field mapping
              │  or CeoItem         │
              │  or CustomType      │
              └──────────┬──────────┘
                         │
        ┌────────────────┼────────────────┬──────────────┐
        │                │                │              │
        ▼                ▼                ▼              ▼
┌──────────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐
│    HTML      │  │   TXT    │  │   MODS   │  │     PDF      │
│  Generator   │  │Generator │  │Generator │  │  Generator   │
└──────┬───────┘  └────┬─────┘  └────┬─────┘  └──────┬───────┘
       │               │             │               │
       └───────────────┴─────────────┴───────────────┘
                       │
                       ▼
               ┌──────────────┐
               │ALTO Generator│
               └──────────────┘
```

**Benefits**:
- ✅ Multiple data sources (API, files, database, etc.)
- ✅ Field mapping for any format
- ✅ Batch processing from archives
- ✅ Easy testing with minimal data
- ✅ Support for other news APIs
- ✅ Reproducible research workflows

## Data Flow Comparison

### Current Flow (Single Path)

```
Daily Princetonian API
         ↓
    CeoClient.articles()
         ↓
   List[CeoItem] ←────────────────┐
         ↓                         │
   Generators                      │
         ↓                         │
    Output Files                   │
                                   │
No other way to get data in ───────┘
```

### Proposed Flow (Multiple Paths)

```
┌──────────────────────────┐
│    Data Sources          │
├──────────────────────────┤
│ • CEO API                │
│ • JSONL files            │
│ • CSV exports            │
│ • Database dumps         │
│ • Other APIs             │
│ • Web scraping results   │
│ • Parquet files          │
└────────┬─────────────────┘
         ↓
┌────────────────────────────────┐
│         Loaders                 │
│  (with field mapping)           │
└────────┬───────────────────────┘
         ↓
┌────────────────────────────────┐
│    ArticleProtocol             │
│  (normalized interface)         │
└────────┬───────────────────────┘
         ↓
┌────────────────────────────────┐
│       Generators                │
│  (unchanged, work with all)     │
└────────┬───────────────────────┘
         ↓
     Output Files
```

## Code Comparison

### Current: Tightly Coupled

```python
# Only works with Daily Princetonian
from clients import CeoClient

client = CeoClient()
items = client.articles('2024-01-01', '2024-01-31', 'article')

html_gen = HTMLGenerator()
html_gen.items = items  # Must be CeoItem objects
html_gen.generate()
```

**Problem**: No way to use pre-existing data or other sources.

### Proposed: Flexible Sources

```python
# Option 1: API (same as before)
from loaders import APILoader

loader = APILoader('2024-01-01', '2024-01-31')
items = list(loader)

# Option 2: JSONL file
from loaders import JSONLLoader

loader = JSONLLoader(
    'archived_articles.jsonl',
    field_mapping={'headline': 'title', 'content': 'body'}
)
items = list(loader)

# Option 3: CSV file
from loaders import CSVLoader

loader = CSVLoader('export.csv', field_mapping={...})
items = list(loader)

# Option 4: Mix sources
from loaders import APILoader, JSONLLoader
import itertools

api_items = APILoader('2024-01-01', '2024-01-31')
file_items = JSONLLoader('archive.jsonl')
all_items = list(itertools.chain(api_items, file_items))

# Generators work with all sources!
html_gen = HTMLGenerator()
html_gen.items = items  # From any source
html_gen.generate()
```

## Use Case Comparison

### Current: Limited Use Cases

| Use Case | Supported? | Notes |
|----------|-----------|-------|
| Fetch live articles | ✅ Yes | Primary use case |
| Process archived articles | ❌ No | Must re-fetch from API |
| Batch process scraped data | ❌ No | No way to import |
| Reproducible research | ❌ Limited | Can't use fixed dataset |
| Support other news APIs | ❌ No | Hard-coded to CEO API |
| Testing with fixtures | ⚠️ Awkward | Must create full CeoItem |
| Cross-institution usage | ❌ No | Princeton-specific |

### Proposed: Expanded Use Cases

| Use Case | Supported? | Notes |
|----------|-----------|-------|
| Fetch live articles | ✅ Yes | Via APILoader |
| Process archived articles | ✅ Yes | Via JSONLLoader |
| Batch process scraped data | ✅ Yes | Via file loaders |
| Reproducible research | ✅ Yes | Fixed JSONL datasets |
| Support other news APIs | ✅ Yes | Via custom loaders |
| Testing with fixtures | ✅ Easy | Minimal test data |
| Cross-institution usage | ✅ Yes | Generic loaders |
| Database integration | ✅ Yes | Via DatabaseLoader |
| Data lake processing | ✅ Yes | Via Parquet/Arrow loaders |

## Complexity Comparison

### Lines of Code

| Component | Current | Proposed | Delta |
|-----------|---------|----------|-------|
| Core clients | 150 | 150 | 0 |
| Generators | 800 | 850 | +50 (protocols) |
| **Loaders** | **0** | **330** | **+330** |
| CLI tools | 400 | 500 | +100 (options) |
| Tests | 2000 | 2300 | +300 |
| **Total** | **3350** | **4130** | **+780** |

### File Count

| Type | Current | Proposed | Delta |
|------|---------|----------|-------|
| Core modules | 8 | 8 | 0 |
| **Loader modules** | **0** | **4** | **+4** |
| Protocol definitions | 0 | 1 | +1 |
| Tests | 7 | 9 | +2 |
| Docs | 1 | 4 | +3 |
| **Total** | **16** | **26** | **+10** |

### Maintenance Burden

| Aspect | Current | Proposed | Impact |
|--------|---------|----------|--------|
| Understanding | Simple | Medium | ⚠️ Need docs |
| Testing | Moderate | Easy | ✅ Easier fixtures |
| Adding sources | Impossible | Easy | ✅ Just add loader |
| Bug surface | Small | Medium | ⚠️ More code paths |
| User flexibility | Low | High | ✅ More options |

## Migration Path

### Phase 1: Add Protocols (Week 1)
- Create `generators/protocols.py`
- Update type hints
- **Zero breaking changes**

### Phase 2: Add Loaders (Week 2)
- Create `loaders/` package
- Implement `JSONLLoader` and `CSVLoader`
- Wrap `CeoClient` in `APILoader`
- **Still backward compatible**

### Phase 3: Update CLI (Week 3)
- Add `--from-jsonl` option to `dp-to-pdf`
- Add `--from-csv` option
- Update documentation

### Phase 4: Advanced (Optional)
- Add more loaders (database, Parquet, etc.)
- Add config file support for mappings
- Add loader plugins system

## Performance Comparison

### Memory Usage

**Current**:
```python
# Must load all into memory at once
items = client.articles(...)  # Loads entire list
```

**Proposed**:
```python
# Can stream large files
for article in loader:  # Yields one at a time
    process(article)
```

**Impact**: Can handle files larger than memory ✅

### API Rate Limits

**Current**:
- Must hit API every time
- Subject to rate limits
- Network dependent

**Proposed**:
- Save data locally as JSONL
- Process offline
- Reproducible without API

**Impact**: Better for batch jobs and research ✅

## Real-World Scenarios

### Scenario 1: Researcher Analyzing Historical Articles

**Current Workflow** (painful):
1. Fetch articles from API (hope it's still available)
2. Process immediately
3. Lose data when done
4. Can't reproduce analysis

**Proposed Workflow** (better):
1. Fetch once, save to JSONL
2. Keep dataset for reproducibility
3. Process any time, offline
4. Share dataset with collaborators
5. Consistent results

### Scenario 2: Multi-Institution Project

**Current**: Each institution needs CEO API access (Princeton-specific)

**Proposed**: Institutions use their own APIs/databases
```python
# Princeton
loader = APILoader(...)

# Stanford (different CMS)
loader = JSONLLoader('stanford_export.jsonl', mapping=stanford_mapping)

# MIT (database)
loader = DatabaseLoader(connection_string, query, mapping=mit_mapping)

# All generate same outputs using same generators!
```

### Scenario 3: Incremental Processing

**Current**: Process everything together

**Proposed**: Process in batches
```python
# Process 1000 articles at a time
loader = JSONLLoader('huge_archive.jsonl')
batch_size = 1000

for i, article in enumerate(loader):
    if i % batch_size == 0:
        # Save checkpoint, free memory
        save_checkpoint(i)
```

## Recommendation Summary

**Implement both Protocols + Loaders**

### Benefits
- ⭐⭐⭐⭐⭐ Massive increase in flexibility
- ⭐⭐⭐⭐⭐ Enables batch/offline processing
- ⭐⭐⭐⭐⭐ Supports reproducible research
- ⭐⭐⭐⭐ Better testing
- ⭐⭐⭐⭐ Cross-institutional usage

### Costs
- ⭐⭐ Medium complexity increase (~780 LOC)
- ⭐⭐ More documentation needed
- ⭐ Slightly steeper learning curve

### Verdict
**Excellent ROI** - Transforms tool from single-purpose to general framework while maintaining simplicity for basic use cases.

### Implementation Order
1. **Week 1**: Protocols (enables future flexibility, zero risk)
2. **Week 2**: Loaders (unlocks file processing)
3. **Week 3**: CLI integration (makes it accessible)
4. **Future**: Advanced loaders as needed

**Start with Phase 1 (Protocols) - it's low-risk and sets foundation for everything else.**
