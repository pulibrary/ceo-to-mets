import re
from datetime import datetime
from pathlib import Path
from typing import List, Union

from jinja2 import Environment

from clients import CeoItem


class HTMLGenerator:
    template_string = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Daily Princetonian Articles</title>
    <style>
        @page {
            size: letter;
            margin: 2.5cm;
            @bottom-center {
                content: counter(page) " of " counter(pages);
                font-size: 9pt;
                color: #666;
            }
        }
        
        body {
            font-family: Georgia, 'Times New Roman', serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
        }
        
        .cover-page {
            text-align: center;
            padding-top: 4cm;
            page-break-after: always;
        }
        
        .cover-page h1 {
            font-size: 24pt;
            margin-bottom: 1cm;
        }
        
        .cover-page .date-range {
            font-size: 14pt;
            color: #666;
        }
        
        article {
            page-break-after: always;
            margin-bottom: 2cm;
        }
        
        article:last-child {
            page-break-after: auto;
        }
        
        .article-header {
            border-bottom: 2px solid #000;
            padding-bottom: 0.5cm;
            margin-bottom: 1cm;
        }
        
        h1 {
            font-size: 18pt;
            margin: 0 0 0.3cm 0;
            color: #000;
        }
        
        .subhead {
            font-size: 13pt;
            font-style: italic;
            color: #444;
            margin: 0.3cm 0;
        }
        
        .meta {
            font-size: 9pt;
            color: #666;
            margin-top: 0.5cm;
        }
        
        .meta-item {
            margin-right: 1cm;
        }
        
        .abstract {
            font-style: italic;
            color: #555;
            margin: 0.5cm 0 1cm 0;
            padding: 0.5cm;
            background: #f5f5f5;
            border-left: 3px solid #ccc;
        }
        
        .content {
            text-align: justify;
        }
        
        .content p {
            margin: 0.5cm 0;
        }
        
        .content a {
            color: #0066cc;
            text-decoration: none;
        }
        
        .content a:hover {
            text-decoration: underline;
        }
        
        .featured-image {
            width: 100%;
            text-align: center;
            margin: 1cm 0;
            page-break-inside: avoid;
        }
        
        .featured-image img {
            max-width: 70%;
            height: auto;
            display: inline-block;
        }
        
        .image-caption {
            font-size: 9pt;
            color: #666;
            font-style: italic;
            margin-top: 0.2cm;
            text-align: center;
            max-width: 70%;
            margin-left: auto;
            margin-right: auto;
        }
        
        .chart-image {
            width: 100%;
            text-align: center;
            margin: 1cm 0;
            page-break-inside: avoid;
        }
        
        .chart-image img {
            max-width: 85%;
            height: auto;
            display: inline-block;
        }
        
        .tags {
            margin-top: 1cm;
            padding-top: 0.5cm;
            border-top: 1px solid #ddd;
            font-size: 9pt;
            color: #666;
        }
        
        .tag {
            display: inline-block;
            background: #f0f0f0;
            padding: 0.1cm 0.3cm;
            margin-right: 0.2cm;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div class="cover-page">
        <h1>The Daily Princetonian</h1>
        <div class="date-range">
            Articles Archive<br>
            {{ total }} article{{ 's' if total != 1 else '' }}
        </div>
    </div>
    
    {% for item in items %}
    <article>
        <div class="article-header">
            <h1>{{ item.headline }}</h1>
            {% if item.subhead %}
            <div class="subhead">{{ item.subhead }}</div>
            {% endif %}
            <div class="meta">
                <span class="meta-item">
                    <strong>Published:</strong> 
                    {{ item.published_at|format_date }}
                </span>
                {% if item.authors %}
                <span class="meta-item">
                    <strong>By:</strong> 
                    {{ item.authors|map(attribute='name')|join(', ') }}
                </span>
                {% endif %}
            </div>
        </div>
        
        {% if item.abstract %}
        <div class="abstract">
            {{ item.abstract|clean_html|safe }}
        </div>
        {% endif %}
        
        {% if include_images and item.dominantMedia and item.dominantMedia.type == 'image' %}
        <div class="featured-image">
            <img src="https://snworksceo.imgix.net/pri/{{ item.dominantMedia.attachment_uuid }}.sized-1000x1000.{{ item.dominantMedia.extension }}" 
                 alt="{{ item.dominantMedia.title }}">
            {% if item.dominantMedia.content %}
            <div class="image-caption">
                {{ item.dominantMedia.content|clean_html|safe }}
            </div>
            {% endif %}
        </div>
        {% endif %}
        
        <div class="content">
            {{ item.content|clean_html|safe }}
        </div>
        
        {% if item.tags %}
        <div class="tags">
            <strong>Tags:</strong>
            {% for tag in item.tags %}
            <span class="tag">{{ tag.name }}</span>
            {% endfor %}
        </div>
        {% endif %}
    </article>
    {% endfor %}
</body>
</html>
"""

    # Template for single article
    single_article_template_string = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{{ item.headline }}</title>
    <style>
        body {
            font-family: Georgia, 'Times New Roman', serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 2cm auto;
            padding: 0 1cm;
        }
        header {
            border-bottom: 2px solid #000;
            padding-bottom: 1cm;
            margin-bottom: 1cm;
        }
        h1 {
            font-size: 24pt;
            margin: 0 0 0.5cm 0;
        }
        .subhead {
            font-size: 14pt;
            font-style: italic;
            color: #444;
            margin: 0.3cm 0;
        }
        .meta {
            font-size: 9pt;
            color: #666;
            margin-top: 0.5cm;
        }
        .abstract {
            font-style: italic;
            color: #555;
            margin: 1cm 0;
            padding: 0.5cm;
            background: #f5f5f5;
            border-left: 3px solid #ccc;
        }
        .content {
            text-align: justify;
        }
        .content p {
            margin: 0.5cm 0;
        }
        .content a {
            color: #0066cc;
        }
        .chart-image {
            text-align: center;
            margin: 1cm 0;
        }
        .chart-image img {
            max-width: 85%;
            height: auto;
        }
    </style>
</head>
<body>
    <article>
        <header>
           <h1>{{ item.headline }}</h1>
           {% if item.subhead %}
           <div class="subhead">{{ item.subhead }}</div>
           {% endif %}
            <div class="meta">
                <span class="meta-item">
                    <strong>Published:</strong>
                    {{ item.published_at|format_date }}
                </span>
                {% if item.authors %}
                <span class="meta-item">
                    <strong>By:</strong>
                    {{ item.authors|map(attribute='name')|join(', ') }}
                </span>
                {% endif %}
            </div>
        </header>

        {% if item.abstract %}
        <div class="abstract">
          {{ item.abstract|clean_html|safe }}
        </div>
        {% endif %}

        <div class="content">
            {{ item.content|clean_html|safe }}
        </div>
    </article>
</body>
</html>
"""

    def __init__(self, items: Union[CeoItem, List[CeoItem]], include_images: bool = False) -> None:
        """
        Initialize HTML generator with article(s).

        Args:
            items: Single CeoItem or list of CeoItems
            include_images: Whether to include featured images in HTML
        """
        self.items = items if isinstance(items, list) else [items]
        self.include_images = include_images
        self._html = None

    def _format_date(self, date_str) -> str:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%B %d, %Y at %I:%M %p")
        except:
            return date_str

    def _clean_html_content(self, html_content):
        """Clean up HTML content for better PDF rendering"""
        if not html_content:
            return ""

        # The API returns HTML with escaped slashes in closing tags
        html_content = html_content.replace("<\\/p>", "</p>")
        html_content = html_content.replace("<\\/a>", "</a>")
        html_content = html_content.replace("<\\/h5>", "</h5>")
        html_content = html_content.replace("<\\/h6>", "</h6>")
        html_content = html_content.replace("<\\/i>", "</i>")
        html_content = html_content.replace("<\\/script>", "</script>")
        html_content = html_content.replace("<\\/div>", "</div>")
        html_content = html_content.replace("<\\/figure>", "</figure>")
        html_content = html_content.replace("<\\/noscript>", "</noscript>")

        # Extract Flourish chart thumbnails from embedded code
        # Flourish embeds look like: <div class="flourish-embed" data-src="visualisation/ID">
        # The noscript fallback contains: <img src="https://public.flourish.studio/visualisation/ID/thumbnail">

        # Pattern to find Flourish embeds with their noscript thumbnails
        flourish_pattern = r'<figure><div class="embed-code">.*?<noscript><img src="(https://public\.flourish\.studio/visualisation/\d+/thumbnail)".*?</noscript>.*?</figure>'

        def replace_flourish(match):
            thumbnail_url = match.group(1)
            return f'<figure class="chart-image"><img src="{thumbnail_url}" alt="Chart" style="max-width: 100%; height: auto;"></figure>'

        html_content = re.sub(
            flourish_pattern, replace_flourish, html_content, flags=re.DOTALL
        )

        return html_content

    @property
    def html(self) -> str:
        """Generate HTML content from the article(s)."""
        if self._html is None:
            env = Environment()
            env.filters["clean_html"] = self._clean_html_content
            env.filters["format_date"] = self._format_date

            # Use single article template if only one article, otherwise use multi-article template
            if len(self.items) == 1:
                template = env.from_string(self.single_article_template_string)
                self._html = template.render(item=self.items[0])
            else:
                template = env.from_string(self.template_string)
                self._html = template.render(
                    items=self.items,
                    total=len(self.items),
                    include_images=self.include_images
                )
        return self._html

    def generate(self, output_path: Union[str, Path]) -> None:
        """
        Write HTML content to file.

        Args:
            output_path: Path where HTML file should be written
        """
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(self.html)
