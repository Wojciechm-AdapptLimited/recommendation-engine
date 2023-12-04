import re
import scrapy
import html
import logging

from urllib.parse import urlparse
from scrapy.exceptions import CloseSpider
from ..items import CoppermindCrawlerItem


class CoppermindSpider(scrapy.Spider):
    name = "coppermind"
    allowed_domains = ["coppermind.net"]
    start_urls = ["https://coppermind.net/wiki/Cosmere"]
    not_allowed = ["Special:", "Help:", "Template:", "File:", "Coppermind:", "Summary:", "Cite:", "Category:", "User:",
                   "Portal:", "cite", "Cite", "User_talk", "Gallery", "Talk:", "Wikipedia:", "wikipedia:", "Help_talk:"]

    page_count = 0  # Counter for the number of pages scraped
    page_limit = 1000  # The desired number of pages to scrape

    custom_settings = {
        'LOG_LEVEL': logging.INFO,
    }

    visited_pages = set()

    def parse(self, response: scrapy.http.Response, **kwargs: dict) -> None:
        title = response.css("h1#firstHeading i::text").get()
        title_2 = response.css("h1#firstHeading::text").get()

        if title is None:
            title = title_2
        elif title_2 is not None:
            title = title + title_2
        else:
            return

        if title in self.visited_pages:
            return

        if self.page_count >= self.page_limit:
            raise CloseSpider('Reached page limit')

        self.page_count += 1  # Increment the counter
        self.logger.info(f'Page Count: {self.page_count}')
        self.visited_pages.add(title)

        try:
            self.logger.info(f'Parsing {response.url}')

            content = response.css("div.mw-parser-output")

            if "Category" not in response.url:
                # Parse and clean the current article
                article = self.parse_article(content)
                cleaned_article = self.clean_article(article)

                yield CoppermindCrawlerItem(
                    title=title,
                    url=response.url,
                    article=cleaned_article,
                )

            # Follow links within the same domain
            domain = urlparse(response.url).netloc

            for href in content.css('a::attr(href)').getall():
                url = response.urljoin(href)
                if urlparse(url).netloc != domain:
                    continue

                if "/wiki/" not in url:
                    continue

                if any([na in url for na in self.not_allowed]):
                    continue

                yield response.follow(url, callback=self.parse)
        except Exception as e:
            self.logger.error(f'Error parsing {response.url}: {e}')

    def parse_article(self, content) -> str:
        try:
            article_text = []

            for element in content.xpath('./*'):
                if element.root.tag == 'p':
                    text = element.xpath('string()').get().strip()
                    article_text.append(text) if text else None
                elif element.root.tag in ['ul', 'ol']:
                    list_items = element.css('li::text').getall()
                    for item in list_items:
                        article_text.append('- ' + item)
                elif element.root.tag == 'blockquote':
                    quote = element.xpath('string()').get().strip()
                    article_text.append(f'"{quote}"') if quote else None
                elif element.root.tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    header = element.xpath('string()').get().strip()
                    article_text.append(header) if header else None
                # Add more cases as needed
                else:
                    pass

            return ' '.join(article_text)
        except Exception as e:
            self.logger.error(f'Error parsing article: {e}')
            return ''

    @staticmethod
    def clean_article(text: str) -> str:
        # Remove inline citations
        text = re.sub(r'\[\d+\]', '', text)

        # Decode HTML entities
        text = html.unescape(text)

        # Replace specific special characters
        text = text.replace('—', '-').replace('–', '-')

        # Convert to lowercase
        text = text.lower()

        # Remove special characters like newlines, tabs, etc.
        for character in ["\n", "\t", "\r", "\xa0", "\u200b", "\u200e", "\u200f"]:
            text = text.replace(character, " ")

        # Collapse multiple spaces into one
        text = ' '.join(text.split())

        return text
