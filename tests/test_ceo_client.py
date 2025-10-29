"""Tests for CeoClient module."""

import pytest
from unittest.mock import Mock, patch
from clients import CeoClient, CeoItem


def test_ceo_client_initialization():
    """Test that CeoClient initializes correctly."""
    client = CeoClient()

    assert client.endpoint == "https://www.dailyprincetonian.com/search.json"
    assert client.timeout == 30


def test_ceo_client_parsed_date_string():
    """Test that CeoClient parses dates correctly."""
    client = CeoClient()

    date = client._parsed_date_string("2025-10-01")

    assert date.year == 2025
    assert date.month == 10
    assert date.day == 1


def test_ceo_client_query_url():
    """Test that CeoClient builds correct query URL."""
    client = CeoClient()

    url = client._query_url("2025-10-01", "2025-10-02", "article")

    # Check URL components
    assert "https://www.dailyprincetonian.com/search.json" in url
    assert "ts_month=10" in url
    assert "ts_day=1" in url
    assert "ts_year=2025" in url
    assert "te_month=10" in url
    assert "te_day=2" in url
    assert "te_year=2025" in url
    assert "ty=article" in url


def test_ceo_client_clean_html_content():
    """Test that CeoClient cleans HTML content."""
    client = CeoClient()

    html = "<p>Test<\\/p><a>Link<\\/a>"
    cleaned = client._clean_html_content(html)

    # Check that escaped slashes are removed
    assert "<\\/p>" not in cleaned
    assert "<\\/a>" not in cleaned
    assert "</p>" in cleaned
    assert "</a>" in cleaned


def test_ceo_client_clean_html_handles_empty():
    """Test that CeoClient handles empty HTML."""
    client = CeoClient()

    cleaned = client._clean_html_content("")

    assert cleaned == ""


def test_ceo_client_clean_html_handles_none():
    """Test that CeoClient handles None HTML."""
    client = CeoClient()

    cleaned = client._clean_html_content(None)

    assert cleaned == ""


@patch("clients.requests.get")
def test_ceo_client_articles_success(mock_get):
    """Test that CeoClient.articles() fetches and parses articles."""
    # Mock the API response
    mock_response = Mock()
    mock_response.json.return_value = {
        "items": [
            {
                "id": "12345",
                "uuid": "abc-123",
                "slug": "test-article",
                "seo_title": "Test Article",
                "seo_description": "Test description",
                "seo_image": "",
                "headline": "Test Headline",
                "subhead": "Test Subhead",
                "abstract": "Test abstract",
                "content": "Test content",
                "infobox": "",
                "template": "article",
                "short_token": "abc",
                "status": "published",
                "weight": "0",
                "media_id": "",
                "created_at": "2025-10-01 10:00:00",
                "modified_at": "2025-10-01 11:00:00",
                "published_at": "2025-10-01 12:00:00",
                "metadata": "{}",
                "hits": "100",
                "normalized_tags": "news",
                "ceo_id": "12345",
                "ssts_id": "",
                "ssts_path": "",
                "tags": "",
                "authors": "",
                "dominantMedia": "",
            }
        ]
    }
    mock_get.return_value = mock_response

    client = CeoClient()
    articles = client.articles("2025-10-01", "2025-10-02", "article")

    # Check that articles were returned
    assert len(articles) == 1
    assert isinstance(articles[0], CeoItem)
    assert articles[0].headline == "Test Headline"
    assert articles[0].id == "12345"

    # Check that the API was called
    mock_get.assert_called_once()


@patch("clients.requests.get")
def test_ceo_client_articles_empty_response(mock_get):
    """Test that CeoClient handles empty API response."""
    # Mock empty response
    mock_response = Mock()
    mock_response.json.return_value = {"items": []}
    mock_get.return_value = mock_response

    client = CeoClient()
    articles = client.articles("2025-10-01", "2025-10-02", "article")

    # Should return empty list
    assert articles == []


@patch("clients.requests.get")
def test_ceo_client_articles_none_response(mock_get):
    """Test that CeoClient handles None response."""
    # Mock None response
    mock_response = Mock()
    mock_response.json.return_value = None
    mock_get.return_value = mock_response

    client = CeoClient()
    articles = client.articles("2025-10-01", "2025-10-02", "article")

    # Should return None or handle gracefully
    assert articles is None or articles == []


@patch("clients.requests.get")
def test_ceo_client_uses_correct_headers(mock_get):
    """Test that CeoClient uses correct headers."""
    mock_response = Mock()
    mock_response.json.return_value = {"items": []}
    mock_get.return_value = mock_response

    client = CeoClient()
    client.articles("2025-10-01", "2025-10-02", "article")

    # Check that correct headers were used
    call_args = mock_get.call_args
    headers = call_args[1]["headers"]

    assert "User-Agent" in headers
    assert "Mozilla" in headers["User-Agent"]


@patch("clients.requests.get")
def test_ceo_client_uses_timeout(mock_get):
    """Test that CeoClient uses timeout."""
    mock_response = Mock()
    mock_response.json.return_value = {"items": []}
    mock_get.return_value = mock_response

    client = CeoClient()
    client.articles("2025-10-01", "2025-10-02", "article")

    # Check that timeout was used
    call_args = mock_get.call_args
    timeout = call_args[1]["timeout"]

    assert timeout == 30


@patch("clients.requests.get")
def test_ceo_client_handles_different_article_types(mock_get):
    """Test that CeoClient handles different article types."""
    mock_response = Mock()
    mock_response.json.return_value = {"items": []}
    mock_get.return_value = mock_response

    client = CeoClient()

    # Test different article types
    for article_type in ["article", "opinion", "sports"]:
        client.articles("2025-10-01", "2025-10-02", article_type)

        # Check that the type was included in the URL
        call_args = mock_get.call_args
        url = call_args[0][0]
        assert f"ty={article_type}" in url


@patch("clients.requests.get")
def test_ceo_client_raises_for_status(mock_get):
    """Test that CeoClient raises exception on HTTP error."""
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = Exception("HTTP Error")
    mock_get.return_value = mock_response

    client = CeoClient()

    with pytest.raises(Exception, match="HTTP Error"):
        client.articles("2025-10-01", "2025-10-02", "article")


def test_ceo_client_requested_data_method():
    """Test that _requested_data method exists and has correct signature."""
    client = CeoClient()

    # Check that the method exists
    assert hasattr(client, "_requested_data")
    assert callable(client._requested_data)
