from dataclasses import dataclass
from datetime import datetime
import requests


@dataclass
class CeoItem:
    id: str
    uuid: str
    slug: str
    seo_title: str
    seo_description: str
    seo_image: str
    headline: str
    subhead: str
    abstract: str
    content: str
    infobox: str
    template: str
    short_token: str
    status: str
    weight: str
    media_id: str
    created_at: str
    modified_at: str
    published_at: str
    metadata: str
    hits: str
    normalized_tags: str
    ceo_id: str
    ssts_id: str
    ssts_path: str
    tags: str
    authors: str
    dominantMedia: str


class CeoClient:
    endpoint = "https://www.dailyprincetonian.com/search.json"

    def __init__(self) -> None:
        self.timeout = 30


    def _clean_html_content(self, html_content):
        """Clean up HTML content for better PDF rendering"""
        if not html_content:
            return ""

        # The API returns HTML with escaped slashes in closing tags
        html_content = html_content.replace('<\\/p>', '</p>')
        html_content = html_content.replace('<\\/a>', '</a>')
        html_content = html_content.replace('<\\/h5>', '</h5>')
        html_content = html_content.replace('<\\/h6>', '</h6>')
        html_content = html_content.replace('<\\/i>', '</i>')

        return html_content



    def _parsed_date_string(self, date_str) -> datetime:
        format_code = "%Y-%m-%d"
        parsed_date = datetime.strptime(date_str, format_code)
        return parsed_date


    def _query_url(self, start_str:str, end_str:str, article_type) -> str:
        start = self._parsed_date_string(start_str)
        end = self._parsed_date_string(end_str)
        query  = f"{self.endpoint}?a=1&s=&ti=&ts_month={start.month}&ts_day={start.day}&ts_year={start.year}&te_month={end.month}&te_day={end.day}&te_year={end.year}&au=&tg=&ty={article_type}&o=date"
        return query


    def _requested_data(self, query:str, timeout=30):
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        response = requests.get(query, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()
    

    def articles(self, start_date:str, end_date:str, type:str = 'article'):
        query = self._query_url(start_date, end_date, type)
        data = self._requested_data(query, self.timeout)

        if data is not None:
            return [CeoItem(**item) for item in data['items']]
