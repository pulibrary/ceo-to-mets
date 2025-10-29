#!/usr/bin/env python3
"""Quick test to verify MODS generator works with JSON strings."""

import sys
sys.path.insert(0, 'src')

from clients import CeoItem
from generators.mods_generator import MODSGenerator

# Create a test item with JSON strings for authors and tags
test_item = CeoItem(
    id="12345",
    uuid="abc-123-def",
    slug="test-article",
    seo_title="Test",
    seo_description="Test",
    seo_image="",
    headline="Test Headline",
    subhead="Test Subhead",
    abstract="Test abstract",
    content="Test content",
    infobox="",
    template="article",
    short_token="abc",
    status="published",
    weight="0",
    media_id="",
    created_at="2025-10-01 10:00:00",
    modified_at="2025-10-01 11:00:00",
    published_at="2025-10-01 12:00:00",
    metadata="{}",
    hits="100",
    normalized_tags="news",
    ceo_id="12345",
    ssts_id="",
    ssts_path="",
    tags='[{"name": "News"}, {"name": "Campus"}]',
    authors='[{"name": "John Doe"}, {"name": "Jane Smith"}]',
    dominantMedia="",
)

# Test MODS generation
print("Testing MODSGenerator...")
generator = MODSGenerator(test_item)
mods_element = generator.generate_element()
xml_string = generator.to_string(pretty_print=True)

print("\n✓ MODS element created successfully")
print("\nGenerated XML:")
print(xml_string)

# Check for expected content
assert "Test Headline" in xml_string
assert "John Doe" in xml_string
assert "Jane Smith" in xml_string
assert "News" in xml_string
assert "Campus" in xml_string
assert "2025-10-01" in xml_string

print("\n✓ All assertions passed!")
print("✓ MODS generator is working correctly with JSON strings")
