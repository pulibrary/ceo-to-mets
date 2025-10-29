import sys
import os
from pathlib import Path
import pytest

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Also add the src directory
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Print paths for debugging
print(f"Python path: {sys.path}")


@pytest.fixture
def sample_ceo_item():
    """Create a sample CeoItem for testing."""
    from clients import CeoItem

    return CeoItem(
        id="12345",
        uuid="abc-123-def",
        slug="sample-article-slug",
        seo_title="Sample Article Title",
        seo_description="This is a sample article description",
        seo_image="https://example.com/image.jpg",
        headline="Sample Article Headline",
        subhead="This is a sample subhead",
        abstract="This is a sample abstract with <p>HTML content</p>.",
        content="<p>This is the article content.</p><p>It has multiple paragraphs.</p>",
        infobox="",
        template="article",
        short_token="abc123",
        status="published",
        weight="0",
        media_id="",
        created_at="2025-10-01 10:00:00",
        modified_at="2025-10-01 11:00:00",
        published_at="2025-10-01 12:00:00",
        metadata="{}",
        hits="100",
        normalized_tags="news,campus",
        ceo_id="12345",
        ssts_id="",
        ssts_path="",
        tags='[{"name": "News"}, {"name": "Campus"}]',
        authors='[{"name": "John Doe"}, {"name": "Jane Smith"}]',
        dominantMedia="",
    )


@pytest.fixture
def sample_ceo_items():
    """Create a list of sample CeoItems for testing."""
    from clients import CeoItem

    items = []
    for i in range(3):
        item = CeoItem(
            id=f"1234{i}",
            uuid=f"abc-123-def-{i}",
            slug=f"sample-article-slug-{i}",
            seo_title=f"Sample Article Title {i}",
            seo_description=f"This is sample article description {i}",
            seo_image=f"https://example.com/image{i}.jpg",
            headline=f"Sample Article Headline {i}",
            subhead=f"This is sample subhead {i}",
            abstract=f"<p>This is sample abstract {i}</p>",
            content=f"<p>This is article content {i}.</p><p>It has multiple paragraphs.</p>",
            infobox="",
            template="article",
            short_token=f"abc12{i}",
            status="published",
            weight="0",
            media_id="",
            created_at=f"2025-10-0{i+1} 10:00:00",
            modified_at=f"2025-10-0{i+1} 11:00:00",
            published_at=f"2025-10-0{i+1} 12:00:00",
            metadata="{}",
            hits=f"{100 + i}",
            normalized_tags="news,campus",
            ceo_id=f"1234{i}",
            ssts_id="",
            ssts_path="",
            tags=f'[{{"name": "News"}}, {{"name": "Campus"}}]',
            authors=f'[{{"name": "Author {i}"}}]',
            dominantMedia="",
        )
        items.append(item)

    return items
